import sys


def is_system(stream):
    return stream == sys.stdin or stream == sys.stdout or stream == sys.stderr


def close_if_not_system(stream):
    if not is_system(stream):
        stream.close()
