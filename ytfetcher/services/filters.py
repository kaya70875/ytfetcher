def min_duration(sec: float) -> bool:
    """
    Returns a filter function that checks if a video's duration is greater than or equal to the specified seconds.

    Args:
        sec (float): The minimum duration in seconds.

    Returns:
        function: A function that takes a video object and returns True if its duration is greater than or equal to sec, otherwise False.
    """
    return lambda v: v.duration and v.duration >= sec


def max_duration(sec: float) -> bool:
    """
    Returns a filter function that checks if a video's duration is less than or equal to the specified seconds.

    Args:
        sec (float): The maximum duration in seconds.

    Returns:
        function: A function that takes a video object and returns True if its duration is less than or equal to sec, otherwise False.
    """
    return lambda v: v.duration and v.duration <= sec


def min_views(n: int) -> bool:
    """
    Returns a filter function that checks if a video's view count is greater than or equal to the specified number.

    Args:
        n (int): The minimum number of views.

    Returns:
        function: A function that takes a video object and returns True if its view count is greater than or equal to n, otherwise False.
    """
    return lambda v: v.view_count and v.view_count >= n


def max_views(n: int) -> bool:
    """
    Returns a filter function that checks if a video's view count is less than or equal to the specified number.

    Args:
        n (int): The maximum number of views.

    Returns:
        function: A function that takes a video object and returns True if its view count is less than or equal to n, otherwise False.
    """
    return lambda v: v.view_count and v.view_count <= n


def filter_by_title(title: str) -> bool:
    """
    Returns a filter function that checks if a video's title starts with the specified string.

    Args:
        title (str): The title string to check against.

    Returns:
        function: A function that takes a video object and returns True if its title starts with title, otherwise False.
    """
    return lambda v: v.title and v.title.startswith(title)