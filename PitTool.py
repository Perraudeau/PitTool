#!/usr/bin/python
import os,sys
import Image

def main(argv):
	try:
		jpgfile = Image.open("picture.jpg")
		print jpgfile.bits, jpgfile.size, jpgfile.format
	except getopt.GetoptError:
		print 'PitResolver.py inputfile'
		sys.exit(2)
if __name__ == "__main__":
   main(sys.argv[1:])