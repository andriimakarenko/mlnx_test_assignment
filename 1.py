#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process
import argparse
from time import time
from exceptions import *

# I would separate this in multiple functions if it wasn't for the deadline
def createAndFill(x, y, z):
	if z * y > x:
		raise(DangerousArgsCombinationException)

	p1 = subprocess.run(['df', '-l', '-BM'], capture_output=True, text=True)
	if p1.returncode != 0:
		raise(Exception("Couldn't complete 'df -l -BM'"))

	goodArr = [] # now this is just ungodly
	goodMntPoint = "" # but I lack time to clean array properly in-place
	linesArr = p1.stdout.split("\n")
	linesArr = linesArr[1:] # remove column names
	for line in linesArr:
		if line[:5] == "/dev/":
			goodArr.append(line)

	for line in goodArr:
		stats = line.split()
		mntPoint = stats[-1]
		freeSpace = int(stats[-3][:-1])
		if freeSpace > x:
			goodMntPoint = mntPoint
			break
	if goodMntPoint == "":
		raise(InsufficientFreeSpaceException)

	while z > 0:
		p = Process(target=createFileViaDD, args=(y, goodMntPoint, z))
		p.start()
		z -= 1

def createFileViaDD(size, dest, nbr):
	command = f"dd if=/dev/zero of={dest}{str(nbr)}.dat count={str(size)} bs=1024"
	# Comment out next line to go out of debug mode
	commant = "sleep 10"
	print(command)
	p1 = subprocess.run(command, capture_output=True, shell=True)
	# while p1.poll() is None:
	# 	continue

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Creates FILEAMOUNT files of FILESIZE megabytes each on the first mounted local partition that has at least MINSPACE megabytes of free space')
	parser.add_argument('-s', '--minspace',
						type=int, metavar='', required=True,
						help='Minimum free space required on a target partition')
	parser.add_argument('-S', '--filesize',
						type=int, metavar='', required=True,
						help='Size of each file to be created')
	parser.add_argument('-a', '--fileamount',
						type=int, metavar='', required=True,
						help='Amount of files to create')
	args = parser.parse_args()

	try:
		createAndFill(args.minspace, args.filesize, args.fileamount)
	except Exception as e:
		print("Couldn't complete the task: ", e)