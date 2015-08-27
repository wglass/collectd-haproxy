import sys


PY3 = sys.version_info >= (3,)


def iteritems(dictionary):
    if PY3:
        return dictionary.items()

    return dictionary.iteritems()


def coerce_long(string):
    if not PY3:
        return long(string)

    return int(string)
