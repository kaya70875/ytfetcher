class YoutubeV3Error(Exception):
    """
    Base exception for all Youtube V3 api errors.
    """

class YTFetcherError(Exception):
    """
    Base exception for all YTFetcher errors.
    """

class ExporterError(Exception):
    """
    Base exception for all Exporter errors.
    """

class SystemPathCannotFound(ExporterError):
    """
    Raises when specified path cannot found.
    """

class NoDataToExport(ExporterError):
    """
    Raises when channel snippets and transcripts are empty.
    """

class InvalidTimeout(YTFetcherError):
    """
    Raises when timeout is invalid type.
    """

class InvalidHeaders(YTFetcherError):
    """
    Raises when headers are invalid.
    """

class InvalidChannel(YoutubeV3Error):
    """
    Raises when channel handle is invalid or cannot found.
    """

class InvalidApiKey(YoutubeV3Error):
    """
    Raises when api key for Youtube V3 is invalid.
    """

class MaxResultsExceed(YoutubeV3Error):
    """
    Raises when max_results bigger than 500 videos.
    """

class NoChannelVideosFound(YoutubeV3Error):
    """
    Raises when a channel has no videos to fetch.
    """

