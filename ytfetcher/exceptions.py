class YTFetcherError(Exception):
    """
    Base exception for all YTFetcher errors.
    """

class ExporterError(Exception):
    """
    Base exception for all Exporter errors.
    """

class OutputDirectoryNotFoundError(ExporterError):
    """
    Raised when the specified output directory does not exist.
    """

class NoDataToExport(ExporterError):
    """
    Raises when channel snippets and transcripts are empty.
    """

class InvalidHeaders(YTFetcherError):
    """
    Raises when headers are invalid.
    """

class TranscriptFetchError(YTFetcherError):
    """
    Raises when transcripts could not be fetched.
    """

class ChannelFetchError(YTFetcherError):
    """
    Base exception for all ChannelFetcher errors.
    """

class PlaylistFetchError(YTFetcherError):
    """
    Base exception for all PlaylistFetcher errors.
    """

class SearchFetchError(YTFetcherError):
    """
    Base exception for all SearchFetcher errors.
    """
    def __init__(self, query: str, msg: str):
        self.query = query
        self.msg = msg
        super().__init__(f"Search failed for query {query} : {msg}")

class VideoListFetchError(YTFetcherError):
    """
    Base exception for all VideoListFetcher errors.
    """

class PlaylistIdNotFound(PlaylistFetchError):
    """
    Raises when playlist id not found.
    """
    def __init__(self, playlist_id: str):
        self.playlist_id = playlist_id
        super().__init__(f"No playlist found for ID: {playlist_id}")

class ChannelNotFound(ChannelFetchError):
    """
    Raises when channel not found.
    """
    def __init__(self, channel_handle: str):
        self.channel_handle = channel_handle
        super().__init__(f"Channel '{channel_handle}' not found.")

class ChannelTabUnavailable(ChannelFetchError):
    """
    Raises when specified tab not found.
    """
    def __init__(self, channel_handle: str, tab: str):
        self.channel_handle = channel_handle
        self.tab = tab
        super().__init__(f"There is no '{tab}' tab for channel '{channel_handle}'")

class InCompleteVideoId(VideoListFetchError):
    """
    Raises when video id truncated or incomplete.
    """
    def __init__(self, video_id: str):
        self.video_id = video_id
        super().__init__(f'Video id {video_id} is incomplete or truncated.')

class VideoUnavailable(VideoListFetchError):
    """
    Raises when video id is not available or correct.
    """
    def __init__(self, video_id: str):
        self.video_id = video_id
        super().__init__(f"Video id {video_id} is not available.")