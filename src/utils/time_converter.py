def ms_to_seconds(ms):
    """Converts milliseconds to seconds."""
    return ms / 1000

def ms_to_readable(ms):
    """
    Converts milliseconds to a human-readable string.

    Parameters:
        ms (int): Number of milliseconds to convert.

    Returns:
        str: Human-readable string, e.g., '1 hour 23 min'.
    """

    seconds = ms_to_seconds(ms)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours:
        return f'{hours} hour{"s" if hours > 1 else ''} {minutes} min'
    else:
        return f'{minutes} min'

def ms_to_minutes(ms):
    """
        Converts ms into minutes.

        Parameters:
            ms (int): Number of milliseconds to convert.

        Returns:
            str: e.g. '02:45'.
        """
    seconds = ms_to_seconds(ms)
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    return f'{minutes:02}:{seconds:02}'
