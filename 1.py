#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process
import argparse
import time
from exceptions import *

def createAndFill(x, y, z):
	startTime = time.perf_counter()

	if z * y > x:
		raise(DangerousArgsCombinationException)

	p1 = subprocess.run(['df', '-l', '-BM'], capture_output=True, text=True)
	if p1.stderr != "":
		raise(CommandExecutionException('df -l -BM'))
	goodMntPoint = findMntPoint(p1.stdout, x)

	processes = []
	for n in range(z):
		p = Process(target=createFileViaDD, args=(y, goodMntPoint, n))
		p.start()
		processes.append(p)

	for process in processes:
		process.join()

	endTime = time.perf_counter()
	print(f'The entire process took {round(endTime - startTime, 2)} second(s).')


def createFileViaDD(size, dest, nbr):
	command = ['dd', 'if=/dev/zero', f'of={dest}{str(nbr)}.dat', f'count={str(size)}', 'bs=1024']
	# Uncomment next line for debug mode
	# command = ['sleep', '10']
	p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p1.wait()

def findMntPoint(dfout, x):
	goodArr = []
	goodMntPoint = ""
	linesArr = dfout.split("\n")
	linesArr = linesArr[1:] # remove column names
	for line in linesArr:
		if line[:5] == "/dev/":
			goodArr.append(line)

	for line in goodArr:
		stats = line.split()
		mntPoint = stats[-1]
		freeSpace = int(stats[-3][:-1])
		if freeSpace > x:
			return mntPoint
	
	raise(InsufficientFreeSpaceException)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Creates FILEAMOUNT files of FILESIZE megabytes each on the first mounted local partition that has at least MINSPACE megabytes of free space')
	parser.add_argument('-s', '--minspace',
						type=int, metavar='', required=True,
						help='Minimum free space required on a target partition in Megabytes')
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