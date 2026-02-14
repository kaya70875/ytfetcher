import sqlite3
import json
from pathlib import Path
from ytfetcher.models.channel import VideoTranscript

class SQLiteCache:
    """
    SQLite-based cache for storing and retrieving video transcripts.
    
    This class manages a SQLite database for caching video transcript data,
    providing methods to store, retrieve, and manage transcript entries
    with support for multiple cache keys and language configurations.
    """
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.db_file = self.cache_dir / "cache.sqlite3"
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)

        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        
        return conn

    def _initialize(self) -> None:
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
    
    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE from transcript_cache")

    def get_transcripts(self, video_ids: list[str], cache_key: str) -> list[VideoTranscript]:
        if not video_ids:
            return []

        placeholders = ",".join("?" for _ in video_ids)
        query = (
            f"SELECT payload FROM transcript_cache WHERE cache_key = ? "
            f"AND video_id IN ({placeholders})"
        )

        with self._connect() as conn:
            rows = conn.execute(query, [cache_key, *video_ids]).fetchall()

        return [VideoTranscript.model_validate_json(payload) for (payload,) in rows]

    def upsert_transcripts(self, transcripts: list[VideoTranscript], cache_key: str) -> None:
        if not transcripts:
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

    @staticmethod
    def build_transcript_cache_key(languages: list[str], manually_created: bool) -> str:
        return json.dumps(
            {
                "languages": languages,
                "manually_created": manually_created,
            },
            sort_keys=True,
        )
