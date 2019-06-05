import imageio
import datetime
import os
import sys
import re

from argparse import ArgumentParser

import numpy as np


def create_gif(files, durations, outfile):
	""" Creates a gif from multiple images.

	<param: files (array [str])> - A list of file paths.
	<param: durations (array or float)> - The durations between frames.
	<param: outputFile (str)> - The path of the output filename.
	
	<return: None>
	"""

	images = []
	for file in files:
		if (file.split('/')[-1][0] != '.'): # Ensure that file is not a hidden file (thanks Soheil!)
			if (vrb>1): print(file)
			images.append(imageio.imread(file))

	imageio.mimsave(outfile, images, duration=durations)


def sort_alphanum(strs):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanumKey = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    
    return sorted(strs, key=alphanumKey)



def main():

	# Define Argument Parser
	parser = ArgumentParser()
	intervalGroup = parser.add_mutually_exclusive_group()
	parser.add_argument('-f', '--files',
						action='store',dest='files',type=str,nargs='*',default=None,
						help="A list of image files to combine into a single gif.",metavar="FILE")
	parser.add_argument('-d', '--dir',
						action='store',dest='dir',type=str,default=None,
						help="A directory containing multiple image files to combine into a single gif.",metavar="DIR")
	parser.add_argument('-s', '--sort-by',
						action='store',dest='sortby',type=str,choices=['alphanum','name','date','size',None],default='alphanum',
						help="A directory containing multiple image files to combine into a single gif.",metavar="[*alphanum|name|date|size|None]")
	parser.add_argument('--descending',
						action='store_true',dest='descending',default=False,
						help="If --descending is specified, the list of files will be sorted in descending order rather than the default ascending.")
	parser.add_argument('-o', '--output',
						action='store',dest='outputfile',type=str,default=None,
						help="The file destination for the gif image.",metavar="OUTPUT")
	intervalGroup.add_argument('-i', '--intervals',
						action='store',dest='intervals',type=float,nargs='*',default=0.1,
						help="The interval(s) (in seconds) between image frames. Either a single interval to be applied to all or a list of intervals for each frame transition (Defualt: 5).",metavar="INTERVAL")
	intervalGroup.add_argument('-p', '--pattern', 
						action='store',dest='pattern',type=float,nargs='*',default=None,
						help="Specifies a single pattern of intervals which can be repeated using the --reps argument. Cannot be used with --intervals.",metavar="INTERVAL")
	parser.add_argument('-r','--reps',
						action='store',dest='reps',type=int,default=1,required='-p' in sys.argv or '--pattern' in sys.argv,
						help="The number of repetitions of --pattern.",metavar="REPS")
	parser.add_argument('-e','--examples',
						action='store_true',dest='examples',default=False,
						help="Shows some example usages and exits.")
	parser.add_argument('-v',
						action='count', dest='verbosity', default=0,
						help="The level of verbosity to print to stdout.")

	args = parser.parse_args()

	global vrb
	vrb = args.verbosity


	if (args.examples):
		print("INFO: Example usages for \"MakeGif.py\":\n")

		print("### Make a simple .gif file from multiple files:\n"
			  ">> python MakeGif.py --files foo1.png foo2.png foo3.png foo4.png --output bar.gif\n")

		print("### Use files within a directory to create .gif file:\n"
			  ">> python MakeGif.py --dir mydir --output bar.gif\n")

		print("### Sort the files in some order:\n"
			  ">> python MakeGif.py --dir mydir --sort-by alphanum --output bar_sorted.gif  # (Default) Sort alphanumerically as a human would. (e.g. bar1, bar2, bar15, bar121, foo1, ...)\n"
			  ">> python MakeGif.py --dir mydir --sort-by name --output bar_by_name.gif  # Sort by name only (e.g. bar1, bar121, bar15, bar2, foo1, ...)\n"
			  ">> python MakeGif.py --dir mydir --sort-by size --output bar_by_size.gif  # Sort by file size.\n"
			  ">> python MakeGif.py --dir mydir --sort-by date --output bar_by_date.gif  # Sort by modified date.\n\n"
			  ">> python MakeGif.py --dir mydir --sort-by alphanum --descending --output bar_descending.gif  # Sort in descending order.\n")

		print("### Set intervals (i.e. delays) between frames:\n"
			  ">> python MakeGif.py --dir mydir --intervals 0.5 --output bar_slow.gif  # Adjust all intervals by a set amount.\n"
			  ">> python MakeGif.py --dir mydir --intervals 0.6 0.5 0.4 0.3 0.2 0.1 --output bar_varied.gif # Set each interval individually.\n"
			  ">> python MakeGif.py --dir mydir --pattern 0.1 0.5 --reps 3 --output bar_pattern.gif  # Repeat --pattern a total of --reps times (i.e. 0.1,0.5,0.1,0.5,0.1,0.5) \n")

		exit()


	# Get list of file paths
	if (args.files is not None):
		files = []
		for f in args.files:
			if (os.path.exists(f)):
				files.append(f)
			else:
				print("\nWARNING: Ignoring file: \"{0}\" as it does not exist!\n".format(f))

	elif (args.dir is not None):
		if (os.path.exists(args.dir)):
			files = ["{0}/{1}".format(args.dir,f) for f in os.listdir(args.dir)]			
		else:
			print("\nERROR: The directory: \"{0}\" does not exist!\n  -- ABORTING --\n"); exit()



		if (args.sortby == 'alphanum'):
			files = sort_alphanum(files)

		elif (args.sortby == 'name'):
			files = sorted(files)

		elif (args.sortby == 'date'):
			dates = [os.path.getmtime(f) for f in files]
			files = [f for _,f in sorted(zip(dates,files))]

		elif (args.sortby == 'size'):
			sizes = [os.path.getsize(f) for f in files]
			files = [f for _,f in sorted(zip(sizes,files))]

		if (args.descending == True):
			files.reverse()

	else:
		print("\nERROR: No --files or --dir specified.\n  -- ABORTING --\n"); exit()


	# Validate output file
	if (args.outputfile == None):
		print("\nERROR: No --output file specified.\n  -- ABORTING --\n"); exit()


	# Get frame intervals
	if (args.pattern != None):
		intervals = list(np.tile(args.pattern,args.reps))
	else:
		intervals = args.intervals

	create_gif(files=files, durations=intervals, outfile=args.outputfile)



if __name__ == "__main__":
	main()
