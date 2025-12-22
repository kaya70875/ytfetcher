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