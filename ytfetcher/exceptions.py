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

class ChannelFetchError(YTFetcherError):
    """
    Raises when any ChannelFetcher error occurs.
    """

class PlaylistFetchError(YTFetcherError):
    """
    Raises when any PlaylistFetcher error occurs.
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