import sqlite3
import json
import logging
from pathlib import Path
from ytfetcher.models.channel import VideoTranscript

logger = logging.getLogger(__name__)

class SQLiteCache:
    """
    SQLite-based cache for storing and retrieving video transcripts.
    
    This class manages a SQLite database for caching video transcript data,
    providing methods to store, retrieve, and manage transcript entries
    with support for multiple cache keys and language configurations.
    """
    def __init__(self, cache_dir: str, ttl: int = 7):
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
                    payload TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (video_id, cache_key)
                )
                """
            )
        
        logger.debug("SQLite cache table ensured.")

        if self.ttl > 0:
            removed_rows = self.purge_expired()
            if removed_rows > 0:
                logger.debug(f'Removed records older than {self.ttl} days. Total rows removed: {removed_rows}')

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

    def get_transcripts(self, video_ids: list[str], cache_key: str) -> list[VideoTranscript]:
        if not video_ids:
            logger.debug("Cache lookup skipped: empty video_ids list.")
            return []

        placeholders = ",".join("?" for _ in video_ids)
        query = (
            f"SELECT payload FROM transcript_cache WHERE cache_key = ? "
            f"AND video_id IN ({placeholders})"
        )

        with self._connect() as conn:
            rows = conn.execute(query, [cache_key, *video_ids]).fetchall()

        logger.debug(
            "Cache lookup for %d videos with key=%s | hits=%d",
            len(video_ids),
            cache_key,
            len(rows),
        )

        return [VideoTranscript.model_validate_json(payload) for (payload,) in rows]

    def upsert_transcripts(self, transcripts: list[VideoTranscript], cache_key: str) -> None:
        if not transcripts:
            logger.debug("Upsert skipped: no transcripts provided.")
            return

        rows = [
            (transcript.video_id, cache_key, transcript.model_dump_json())
            for transcript in transcripts
        ]

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO transcript_cache (video_id, cache_key, payload, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(video_id, cache_key) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                rows,
            )

        logger.debug(
            "Upserted %d transcripts into cache with key=%s",
            len(transcripts),
            cache_key,
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
