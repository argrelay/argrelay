"""
"""


def format_time_to_relative(
    curr_time_ms,
    prev_time_ms,
) -> str:
    """
    Format time to relative:
    https://stackoverflow.com/a/6109105/441652
    """

    ms_per_second = 1000
    ms_per_minute = ms_per_second * 60
    ms_per_hour = ms_per_minute * 60
    ms_per_day = ms_per_hour * 24

    elapsed_time = curr_time_ms - prev_time_ms

    if elapsed_time < ms_per_minute:
        return f"{round(elapsed_time / ms_per_second)} seconds ago"
    elif elapsed_time < ms_per_hour:
        return f"{round(elapsed_time / ms_per_minute)} minutes ago"
    elif elapsed_time < ms_per_day:
        return f"{round(elapsed_time / ms_per_hour)} hours ago"
    else:
        return f"{round(elapsed_time / ms_per_day)} days ago"
