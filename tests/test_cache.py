from ytfetcher import YTFetcher, DLSnippet, VideoTranscript
from ytfetcher.models.channel import Transcript
from ytfetcher.config import FetchOptions, HTTPConfig
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher.cache.sqlite_cache import SQLiteCache
from ytfetcher._youtube_dl import BaseYoutubeDLFetcher
from unittest.mock import MagicMock
import sqlite3
import pytest

@pytest.fixture
def sample_transcripts():
    return [
        Transcript(
            text='text1',
            start=1,
            duration=1
        ),
        Transcript(
            text='text2',
            start=2,
            duration=2
        )
    ]

def test_transcripts_are_cached(tmp_path, sample_transcripts):
    class DummyFetcher(BaseYoutubeDLFetcher):
        def fetch(self) -> list[DLSnippet]:
            return [
                DLSnippet(
                    video_id='id1',
                    title='channelname1',
                    description='description1',
                )
            ]

    fetch_options = FetchOptions(cache_enabled=True, cache_path=tmp_path)
    fetcher = YTFetcher(youtube_dl_fetcher=DummyFetcher(), options=fetch_options)

    mocked_fetch = MagicMock(
        side_effect=[
            [VideoTranscript(video_id='id1', transcripts=sample_transcripts)],
            [VideoTranscript(video_id='id1', transcripts=sample_transcripts)],
        ]
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(TranscriptFetcher, "fetch", mocked_fetch)

        first_result = fetcher.fetch_transcripts()
        second_result = fetcher.fetch_transcripts()

    assert len(first_result) == 1
    assert len(second_result) == 1
    assert mocked_fetch.call_count == 1

    db_file = tmp_path / "cache.sqlite3"

    with sqlite3.connect(db_file) as conn:
        table_names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

    assert "transcript_cache" in table_names
    assert "metadata_cache" not in table_names

def test_custom_cache_path_is_used(tmp_path, sample_transcripts):
    custom_dir = tmp_path / "my_custom_cache"

    class DummyFetcher(BaseYoutubeDLFetcher):
        def fetch(self) -> list[DLSnippet]:
            return [
                DLSnippet(
                    video_id="id1",
                    title="channelname1",
                    description="description1",
                )
            ]

    fetch_options = FetchOptions(
        cache_enabled=True,
        cache_path=custom_dir,
    )

    fetcher = YTFetcher(
        youtube_dl_fetcher=DummyFetcher(),
        options=fetch_options,
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            TranscriptFetcher,
            "fetch",
            MagicMock(
                return_value=[
                    VideoTranscript(
                        video_id="id1",
                        transcripts=sample_transcripts,
                    )
                ]
            ),
        )

        fetcher.fetch_transcripts()

    db_file = custom_dir / "cache.sqlite3"

    assert db_file.exists()

    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT COUNT(*) FROM transcript_cache"
        ).fetchone()[0]

    assert rows == 1

def test_cache_clear_removes_all_rows(tmp_path, sample_transcripts):
    cache_dir = tmp_path

    class DummyFetcher(BaseYoutubeDLFetcher):
        def fetch(self) -> list[DLSnippet]:
            return [
                DLSnippet(
                    video_id="id1",
                    title="channelname1",
                    description="description1",
                )
            ]

    fetch_options = FetchOptions(
        cache_enabled=True,
        cache_path=cache_dir,
    )

    fetcher = YTFetcher(
        youtube_dl_fetcher=DummyFetcher(),
        options=fetch_options,
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            TranscriptFetcher,
            "fetch",
            MagicMock(
                return_value=[
                    VideoTranscript(
                        video_id="id1",
                        transcripts=sample_transcripts,
                    )
                ]
            ),
        )

        fetcher.fetch_transcripts()

    db_file = cache_dir / "cache.sqlite3"

    with sqlite3.connect(db_file) as conn:
        rows_before = conn.execute(
            "SELECT COUNT(*) FROM transcript_cache"
        ).fetchone()[0]

    assert rows_before == 1

    cache = SQLiteCache(cache_dir)
    cache.clear()

    with sqlite3.connect(db_file) as conn:
        rows_after = conn.execute(
            "SELECT COUNT(*) FROM transcript_cache"
        ).fetchone()[0]

    assert rows_after == 0

def test_ttl_purges_old_rows(tmp_path):
    cache = SQLiteCache(tmp_path, ttl=1)  # 1 day TTL
    db = tmp_path / "cache.sqlite3"

    # Insert an artificially old row
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO transcript_cache (video_id, cache_key, payload, updated_at) VALUES (?, ?, ?, ?)",
            ("old", "k", "{}", "2000-01-01 00:00:00")
        )
        conn.commit()

    deleted = cache.purge_expired()
    assert deleted >= 1

    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM transcript_cache WHERE video_id='old'").fetchone()[0]
    assert count == 0

def test_ttl_does_not_remove_fresh_rows(tmp_path):
    cache = SQLiteCache(tmp_path, ttl=7)

    vt = VideoTranscript(video_id="fresh", transcripts=[])
    cache.upsert_transcripts([vt], cache_key="k")

    removed = cache.purge_expired()
    assert removed == 0

    rows = cache.get_transcripts(["fresh"], "k")
    assert len(rows) == 1

def test_ttl_zero_disables_expiration(tmp_path):
    cache = SQLiteCache(tmp_path, ttl=0)

    with sqlite3.connect(cache.db_file) as conn:
        conn.execute(
            "INSERT INTO transcript_cache (video_id, cache_key, payload, updated_at) VALUES (?, ?, ?, ?)",
            ("old", "k", "{}", "2000-01-01 00:00:00")
        )

    removed = cache.purge_expired()
    assert removed == 0

def test_ttl_purges_on_initialize(tmp_path):
    cache_dir = tmp_path

    db_file = cache_dir / "cache.sqlite3"
    cache_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_file) as conn:
        conn.execute("""
            CREATE TABLE transcript_cache (
                video_id TEXT NOT NULL,
                cache_key TEXT NOT NULL,
                payload TEXT NOT NULL,
                updated_at TIMESTAMP,
                PRIMARY KEY (video_id, cache_key)
            )
        """)
        conn.execute(
            "INSERT INTO transcript_cache VALUES (?, ?, ?, ?)",
            ("old", "k", "{}", "2000-01-01 00:00:00")
        )

    cache = SQLiteCache(cache_dir, ttl=1)

    with sqlite3.connect(db_file) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM transcript_cache"
        ).fetchone()[0]

    assert count == 0