def min_duration(sec: float) -> bool:
    return lambda v: v.duration and v.duration >= sec

def max_duration(sec: float) -> bool:
    return lambda v: v.duration and v.duration <= sec

def min_views(n: int) -> bool:
    return lambda v: v.view_count and v.view_count >= n

def max_views(n: int) -> bool:
    return lambda v: v.view_count and v.view_count <= n

def filter_by_title(title: str) -> bool:
    return lambda v: v.title and v.title.startswith(title)