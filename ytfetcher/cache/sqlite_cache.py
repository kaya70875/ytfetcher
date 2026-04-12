import sqlite3
import json
import logging
from pathlib import Path
from ytfetcher.models.channel import FailedTranscript, VideoTranscript

logger = logging.getLogger(__name__)

class SQLiteCache:
    """
    SQLite-based cache for storing and retrieving video transcripts.
    
    This class manages a SQLite database for caching video transcript data,
    providing methods to store, retrieve, and manage transcript entries
    with support for multiple cache keys and language configurations.
    """
    def __init__(self, cache_dir: str, ttl: int = 7):
        """
        Initialize the SQLiteCache.

        Args:
            cache_dir (str): The directory where the SQLite database file 
                will be stored. Will be expanded if using tilde (e.g., "~/cache").
            ttl (int): Time-To-Live in days. Cached entries older than this 
                will be considered expired. Defaults to 7.

        Raises:
            ValueError: If the provided cache_dir exists but is not a directory.
        """
        self.cache_dir = Path(cache_dir).expanduser()

        if self.cache_dir.exists() and not self.cache_dir.is_dir():
            raise ValueError('cache_dir must be a directory.')
        
        self.db_file = self.cache_dir / "cache.sqlite3"
        self.ttl = ttl
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_file)

            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            
            return conn
        except sqlite3.DatabaseError:
            logger.exception("Failed to connect to SQLite database at %s", self.db_file)
            raise

    def _initialize(self) -> None:
        logger.debug(
            "Initializing SQLite cache at %s (ttl=%d days)",
            self.db_file,
            self.ttl,
        )

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transcript_cache (
                    video_id TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'success',
                    fail_reason TEXT,
                    payload TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (video_id, cache_key)
                )
                """
            )

            self._migrate(conn)

        logger.debug("SQLite cache table ensured.")

        if self.ttl > 0:
            removed_rows = self.purge_expired()
            if removed_rows > 0:
                logger.debug(f'Removed records older than {self.ttl} days. Total rows removed: {removed_rows}')
    def _migrate(self, conn: sqlite3.Connection) -> None:
        existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(transcript_cache)")}

        # Add new columns if they don't exist
        if "status" not in existing_columns:
            conn.execute("ALTER TABLE transcript_cache ADD COLUMN status TEXT NOT NULL DEFAULT 'SUCCESS'")
        if "fail_reason" not in existing_columns:
            conn.execute("ALTER TABLE transcript_cache ADD COLUMN fail_reason TEXT")

        # Fix payload NOT NULL constraint if needed by recreating the table
        payload_row = next(row for row in conn.execute("PRAGMA table_info(transcript_cache)") if row[1] == "payload")
        payload_is_not_null = payload_row[3] == 1  # column index 3 is the notnull flag

        if payload_is_not_null:
            logger.debug("Migrating: relaxing NOT NULL constraint on payload column.")
            conn.executescript(
                """
                BEGIN;
                CREATE TABLE transcript_cache_new (
                    video_id    TEXT NOT NULL,
                    cache_key   TEXT NOT NULL,
                    status      TEXT NOT NULL DEFAULT 'SUCCESS',
                    fail_reason TEXT,
                    payload     TEXT,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (video_id, cache_key)
                );
                INSERT INTO transcript_cache_new (video_id, cache_key, status, fail_reason, payload, updated_at)
                    SELECT video_id, cache_key, status, fail_reason, payload, updated_at FROM transcript_cache;
                DROP TABLE transcript_cache;
                ALTER TABLE transcript_cache_new RENAME TO transcript_cache;
                COMMIT;
                """
            )
            logger.debug("Migration complete: payload column now allows NULL.")

    def clear(self) -> None:
        logger.info("Clearing entire transcript cache at %s", self.db_file)
        with self._connect() as conn:
            conn.execute("DELETE from transcript_cache")
    
    def purge_expired(self) -> int:
        """
        Remove rows older than ttl days.
        Returns the number of rows deleted.
        """

        if self.ttl <= 0:
            logger.debug("TTL <= 0, skipping cache purge.")
            return 0
        
        sql = """
        DELETE FROM transcript_cache
        WHERE updated_at <= datetime('now', ?)
        """

        with self._connect() as conn:
            cur = conn.execute(sql, (f"-{self.ttl} days",))
            deleted = cur.rowcount if hasattr(cur, "rowcount") else 0
            conn.commit()
        
        return deleted

    def get_cached_states(self, video_ids: list[str], cache_key: str) -> tuple[list[VideoTranscript], list[FailedTranscript]]:
        if not video_ids:
            logger.debug("Cache lookup skipped: empty video_ids list.")
            return [], []

        placeholders = ",".join("?" for _ in video_ids)
        query = (
            f"SELECT video_id, status, fail_reason, payload FROM transcript_cache WHERE cache_key = ? "
            f"AND video_id IN ({placeholders})"
        )

        with self._connect() as conn:
            rows = conn.execute(query, [cache_key, *video_ids]).fetchall()

        successes: list[VideoTranscript] = []
        failures: list[FailedTranscript] = []

        for video_id, status, fail_reason, payload in rows:
            if status == "SUCCESS":
                successes.append(VideoTranscript.model_validate_json(payload))
            else:
                failures.append(FailedTranscript(
                    video_id=video_id,
                    reason=fail_reason or "Unknown",
                    message=f"Cached failure: {fail_reason}"
                ))

        logger.debug(
            "Cache lookup for %d videos | hits=%d successes, %d known failures",
            len(video_ids), len(successes), len(failures)
        )

        return successes, failures

    def upsert_transcripts(self, transcripts: list[VideoTranscript], cache_key: str) -> None:
        if not transcripts:
            return

        rows = [
            (transcript.video_id, cache_key, "SUCCESS", None, transcript.model_dump_json())
            for transcript in transcripts
        ]
        self._upsert(rows)

        logger.debug("Upserted %d transcripts into cache with key=%s", len(transcripts), cache_key)

    def upsert_failures(self, failures: list[FailedTranscript], cache_key: str) -> None:
        """
        Persists permanent (non-retryable) failures so they are never fetched again.
        """
        if not failures:
            return

        rows = [
            (failure.video_id, cache_key, "FAILED", failure.reason, None)
            for failure in failures
        ]
        self._upsert(rows)

        logger.debug("Upserted %d failures into cache with key=%s", len(failures), cache_key)

    def _upsert(self, rows: list[tuple]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO transcript_cache (video_id, cache_key, status, fail_reason, payload, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(video_id, cache_key) DO UPDATE SET
                    status      = excluded.status,
                    fail_reason = excluded.fail_reason,
                    payload     = excluded.payload,
                    updated_at  = CURRENT_TIMESTAMP
                """,
                rows,
            )

    @staticmethod
    def build_transcript_cache_key(languages: list[str] | str, manually_created: bool) -> str:
        return json.dumps(
            {
                "languages": languages,
                "manually_created": manually_created,
            },
            sort_keys=True,
        )
