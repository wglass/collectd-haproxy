import sys


PY3 = sys.version_info >= (3,)


def iteritems(dictionary):
    """
    Helper function for iterating over (key, value) dict tuples.

    In Python 3 the "iteritems()" method went away and "items()"
    became an iterator method.

    :param dictionary: The dictionary to iterate over.
    :type dictionary: dict
    """
    if PY3:
        return dictionary.items()

    return dictionary.iteritems()


def coerce_long(string):
    """
    Function for coercing a string into a long ("10.4" -> 10.4).

    In Python 3 the long and int types were unified, so no more
    "long".

    :param string: The string value to coerce.
    :type string: str
    """
    if not PY3:
        return long(string)  # noqa

    return int(string)
