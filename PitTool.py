#! /usr/bin/env python

import getopt
import sys

import numpy
from PIL import Image

VERBOSE = False
KEYSIZE = 8 #from 1 to 16
KEYLSB = 1 #from 1 to 5
RMS = 0
LSB = 2 #from 1 to 5
FORMAT = "RGB"
USAGE = """Usage: PitTool [options] input file
Tool to find informations from image 

Options : 

-k --keysize : number of pixels used to calculate the hidden message length (8 by default)
-kl --keylsb : number of lsb used to calculate the hidden message length (1 by default)
-l --lsb     : number of lsb used to hide informations (2 by default)
-f --format  : format used to get informations (RGB by default)
-v --verbose : enable the verbose mode (disabled by default)
-h --help    : show the help

"""


def main():
    global KEYSIZE, KEYLSB, VERBOSE
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'hvk:kl:l:f:', ['help', 'verbose', 'keysize=', 'keylsb=', 'lsb=', "format="])
    except getopt.GetoptError as err:
        print USAGE
        sys.exit(1)

    for o, a in options:
        if o in ("-k", "--keysize"):
            try:
                KEYSIZE = int(a)
            except ValueError:
                print "Only integer for the keysize"
                quit()
        if o in ("-kl", "--keylsb"):
            try:
                KEYSIZE = int(a)
            except ValueError:
                print "Only integer for the keylsb"
                quit()
        if o in ("-v", "--verbose"):
            VERBOSE = True
        if o in ("-h", "--help"):
            print USAGE
            quit()

    if not arguments and not options:
        print USAGE

    if arguments:
        print handle_image(arguments[0])


def handle_image(parameters):
    img = Image.open(parameters)
    matrix = numpy.array(img)
    pit_key_size(matrix);
    get_informations(matrix,RMS,LSB,FORMAT)
    quit()


def pit_key_size(matrix):
    global RMS
    """Calculate the length of the key"""
    key_pixels = matrix[0][0:KEYSIZE]
    rms = ""
    for row in key_pixels:
        rms += str(int(int_to_lsb(row,KEYLSB),2))
    RMS = int(rms)

def int_to_lsb(pixel,number_of_lsb):
    """return the lsb of a pixel"""
    lsb = 8-number_of_lsb
    red = '{0:08b}'.format(pixel[0])
    green = '{0:08b}'.format(pixel[1])
    blue = '{0:08b}'.format(pixel[2])
    return red[lsb:8]+green[lsb:8]+blue[lsb:8]

def get_informations(matrix,key_length,LSB,FORMAT):

    for nrow,row in enumerate(matrix):
        for ncolumn,column in enumerate(row):
            # remove the lsb used for calculate the keysize
            if not nrow == 0 or not (ncolumn <= KEYSIZE):
                get_information_from_pixel(column)

def get_information_from_pixel(pixel):
    global RMS
    information = int_to_lsb(pixel,LSB)
    if is_key_size_reached(information):
        quit()

def is_key_size_reached(information):
    global RMS
    RMS -= len(information)
    if RMS - len(information) <= 0 :
        return True
    return False

if __name__ == "__main__":
    main()
