from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    VideoUnavailable,
    InvalidVideoId,
    NoTranscriptFound,
)

PERMANENTLY_FAILED_EXCEPTIONS = (
    TranscriptsDisabled,
    VideoUnavailable,
    InvalidVideoId,
    NoTranscriptFound,
)

RETRYABLE_ERRORS = frozenset({
    "TransientNetworkError"
})
