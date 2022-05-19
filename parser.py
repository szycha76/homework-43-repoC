#!/usr/bin/env python3

import os
import sys


# "Standard" lines identifier:
PREFIX = " warning: "


def me():
    return sys.argv[0].split(os.sep)[-1]


def usage():  # pragma: no-cover
    print(f"Usage: python3 {me()} <doxygen-log-file>")


def guess_separator(sample):
    """Based on the doxygen.log file I've seen I assume that separator is a character
    between the filename and line number, and that the standard line has form of:
    <path>?<line-number>? warning: <rest-of-the-message>
    where "?" is the separator we need to detect.  Hence
    - the character directly preceeding " warning: " string is a separator
    - if it directly follows <path>?<line-number> sequence.

    Confirmation: file <path> exists and has at least <line-number> lines (see
    confirm_separator() function below).
    """

    guesses = {}

    for line in sample:
        pos = line.find(PREFIX)
        guess = line[pos - 1]
        try:
            guesses[guess] += 1
        except KeyError:
            guesses[guess] = 1

    if len(guesses) == 1:
        G = list(guesses.keys())[0]
        return confirm_separator(G, sample)


def confirm_separator(G, sample):

    # Each line has to have the separator
    l = [x for x in sample if G in x]
    if len(l) < len(sample):
        return None

    # Do not read the same file more than once!
    max_lines = {}
    for line in l:
        A = line.split(G, 2)
        try:
            max_lines[A[0]] = max(int(max_lines[A[0]]), int(A[1]))
        except KeyError:
            max_lines[A[0]] = int(A[1])

    for f in max_lines:
        try:
            if max_lines[f] > file_len(f):
                return None
        except FileNotFoundError:
            return None

    return G


def file_len(filename):
    """
    Taken from: https://stackoverflow.com/q/845058
    See documentation and discussion there
    """
    with open(filename) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1


def ignore_non_standard_lines(f):
    return [x for x in f.read().split("\n") if " warning: " in x]


def to_csv(log, sep):
    csv = ['"line","file","message"'] + [
        f'{z[1]},"{z[0].removeprefix(os.getcwd()+os.sep)}","{z[2].removeprefix(PREFIX)}"'
        for z in [x.split(sep, 2) for x in log]
    ]

    with open("doxygen.csv", "w") as f:
        f.write("\n".join(csv))


def main():  # pragma: no-cover
    try:
        with open(sys.argv[1], "r") as f:
            log = ignore_non_standard_lines(f)
    except IndexError:
        usage()
        sys.exit(22)
    except FileNotFoundError:
        print(f'{me()}: File "{sys.argv[1]}" could not be found')
        sys.exit(2)
    except Exception as e:
        print('Uncaught exception: "{repr(e)}"')
        sys.exit(1)

    sep = guess_separator(log[:25])
    if sep:
        to_csv(log, sep)
    else:
        print("I couldn't figure out what a separator character was used.")
        sys.exit(11)


main()

# vim: et sw=4 ts=4 relativenumber number
