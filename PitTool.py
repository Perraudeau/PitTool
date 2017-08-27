#! /usr/bin/env python

import getopt
import sys
import binascii

import numpy
from PIL import Image

VERBOSE = False
KEYSIZE = 8  # from 1 to 16
KEYLSB = 1  # from 1 to 5
RMS = 0
LSB = 2  # from 1 to 5
FORMAT = "RGB"
INDICATOR = 0
PARITY = 0
CHANNEL_SELECTION = "012"
INFO = ""
RIGHT = 0
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
    global KEYSIZE, KEYLSB, VERBOSE, CHANNEL_SELECTION
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'hvk:kl:l:f:',
                                           ['help', 'verbose', 'keysize=', 'keylsb=', 'lsb=', "format="])
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
        CHANNEL_SELECTION = "012"
        print handle_image(arguments[0])
        CHANNEL_SELECTION = "021"
        print handle_image(arguments[0])
        CHANNEL_SELECTION = "102"
        print handle_image(arguments[0])
        CHANNEL_SELECTION = "120"
        print handle_image(arguments[0])
        CHANNEL_SELECTION = "210"
        print handle_image(arguments[0])
        CHANNEL_SELECTION = "201"
        print handle_image(arguments[0])
        quit()


def handle_image(parameters):
    img = Image.open(parameters)
    matrix = numpy.array(img)
    pit_key_size(matrix);
    get_informations(matrix, RMS, LSB, FORMAT)


def pit_key_size(matrix):
    global RMS, PARITY, INDICATOR, CHANNEL_SELECTION
    """Calculate the length of the key"""
    key_pixels = matrix[0][0:KEYSIZE]
    rms = ""
    for row in key_pixels:
        rms += str(int(int_to_lsb(row, KEYLSB), 2))
    if (int(rms) % 2 == 0):
        INDICATOR = 1
    elif (is_prime(int(rms))):
        INDICATOR = 2
    PARITY = get_parity(int(rms))
    RMS = int(rms)
    # CHANNEL_SELECTION = get_channel_selection_criteria()

def get_parity(v):
    v ^= v >> 16
    v ^= v >> 8
    v ^= v >> 4
    v &= 0xf
    return (0x6996 >> v) & 1


def is_prime(num):
    ret = True
    if num > 1:
        for i in range(2, num):
            if (num % i) == 0:
                ret = False
                break
        else:
            ret = False

    else:
        ret = False
    return ret


def int_to_lsb(pixel, number_of_lsb):
    """return the lsb of a pixel"""
    lsb = 7 - number_of_lsb
    red = '{0:08b}'.format(pixel[0])
    green = '{0:08b}'.format(pixel[1])
    blue = '{0:08b}'.format(pixel[2])
    return str(red[lsb:7]) + str(green[lsb:7]) + str(blue[lsb:7])


def get_informations(matrix, key_length, LSB, FORMAT):
    for nrow, row in enumerate(matrix):
        for ncolumn, column in enumerate(row):
            # remove the lsb used for calculate the keysize
            if not nrow == 0 or not (ncolumn <= KEYSIZE):
                b = get_bits_from_pixel(column)
                if b:
                    return


def get_bits_from_pixel(pixel):
    bits_useful = int_to_lsb(pixel, LSB)
    get_information_from_bits(bits_useful)
    if is_key_size_reached(bits_useful):
        try:
            n = int(INFO, 2)
            if n%8 != 0:
                s= str(n)
                padding = n%8
                for i in range(padding):
                    s += "0"
                n = int(s)
            test = n%8
            try:
                print binascii.unhexlify('%x' % n)
            except:
                return True
        except:
            return True


def is_key_size_reached(bits_useful):
    global RMS
    RMS -= len(bits_useful)
    if RMS - len(bits_useful) <= 0:
        return True
    return False


def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start + n]


def get_information_from_bits(pixel):
    global INFO,RIGHT
    a = []
    b = []
    for chunk in chunks(pixel, 2):
        a.append(chunk)
    for chunk in chunks(CHANNEL_SELECTION, 1):
        b.append(chunk)

    if RIGHT != 0 :
        if RIGHT == False:
            c = b[:]
            b[0] = c[2]
            b[1] = c[0]
            b[2] = c[1]
        else:
            c = b[:]
            b[0] = c[0]
            b[1] = c[1]
            b[2] = c[2]
    if(int(b[0]) == 0):
        if (int(b[1]) == 1):
            INFO += get_hidden_date(a, b[0])
            RIGHT = True
        else:
            INFO += get_hidden_date(a, b[0])
            RIGHT = False
    if(int(b[0]) == 1):
        if (int(b[1]) == 0):
            INFO += get_hidden_date(a, b[1])
            RIGHT = True
        else:
            INFO += get_hidden_date(a, b[1])
            RIGHT = False
    if(int(b[0]) == 2):
        if (int(b[1]) == 0):
            INFO += get_hidden_date(a, b[2])
            RIGHT = True
        else:
            INFO += get_hidden_date(a, b[2])
            RIGHT = False

def get_hidden_date(channels,indicator_channel):
    indicator = channels[int(indicator_channel)]
    if int(indicator_channel) == 0:
        a,b = 1,2
    elif int(indicator_channel) == 1:
        a,b = 2,1
    else:
        a,b = 0,1
    ret = ""
    if indicator == "00":
        ret = ""
    elif indicator == "01":
        ret = channels[a]
    elif indicator == "10":
        ret = channels[b]
    elif indicator == "11":
        ret = channels[a]+channels[b]

    return ret

def get_channel_selection_criteria():
    if INDICATOR == 0:
        if PARITY == 0 :
            return str("012")
        else:
            return str("021")
    elif INDICATOR == 1:
        if PARITY == 0 :
            return str("102")
        else:
            return str("120")
    elif INDICATOR == 2:
        if PARITY == 0 :
            return str("201")
        else:
            return str("210")


if __name__ == "__main__":
    main()
