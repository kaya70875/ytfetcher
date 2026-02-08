import sqlite3
import json
from pathlib import Path
from ytfetcher.models.channel import VideoTranscript

class SQLiteCache:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

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
