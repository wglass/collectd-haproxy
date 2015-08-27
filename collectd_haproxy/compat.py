import sys


PY3 = sys.version_info >= (3,)


def iteritems(dictionary):
    if PY3:
        return dictionary.items()

    return dictionary.iteritems()


def coerce_long(string):
    if PY3:
        long = int

    return long(string)
