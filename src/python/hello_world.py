import os
import sys

def entry_point(argv):
    os.write(1, bytes("Hello World!"))
    return 0


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
