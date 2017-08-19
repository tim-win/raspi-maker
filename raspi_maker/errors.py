"""Exceptional."""


class NotGunnaDoItException(Exception):
    """Throw when you simply refuse to follow orders."""
    pass

def check_for_root_device(*args):
    """Throw exception if trying to write to sda.

    Parameters
    ----------
    str : block device ids. As many as you want.

    Returns
    -------
    bool : True if successful (no 'sda' in args)

    Raises
    ------
    raspi_maker.errors.NotGunnaDoItException : seriously, no.
    """

    if 'sda' in args:
        raise NotGunnaDoItException(
            'you really think Im going to thrash your root partition.\n' +
            'To force, please edit the source code.')
    return True