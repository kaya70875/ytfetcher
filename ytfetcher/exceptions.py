class YoutubeV3Error(Exception):
    """
    Base exception for all Youtube V3 api errors.
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

