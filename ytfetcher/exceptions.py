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