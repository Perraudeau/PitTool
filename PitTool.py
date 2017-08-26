#! /usr/bin/env python

import getopt
import sys

VERBOSE = False

USAGE = """Usage: PitTool [options] input file
Tool to find informations from image 

Options : 

-v --verbose : enable the verbose mode (disabled by default)
-h --help    : show the help

"""


def main():
    global VERBOSE
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'hv', ['help''verbose'])
    except getopt.GetoptError as err:
        print USAGE
        sys.exit(1)

    for o, a in options:
        if o in ("-v", "--verbose"):
            VERBOSE = True
        if o in ("-h", "--help"):
            print USAGE
            quit()

    if not arguments and not options:
        print USAGE

    if arguments:
        print arguments[0]

if __name__ == "__main__":
    main()
