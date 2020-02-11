#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process, Pool
import argparse
import time
from exceptions import *

def stopwatch(func):
	def inner(*args):
		startTime = time.perf_counter()
		func(*args)
		endTime = time.perf_counter()
		print(f'The entire process took {round(endTime - startTime, 2)} second(s).')
	return inner

@stopwatch
def createAndFill(minFreeSpace, fileSize, fileAmount, randomSrc):

	if fileAmount * fileSize > minFreeSpace:
		raise(DangerousArgsCombinationException)

	p1 = subprocess.run(['df', '-l', '-BM'], capture_output=True, text=True)
	if p1.stderr != "":
		raise(CommandExecutionException('df -l -BM'))
	goodMntPoint = findMntPoint(p1.stdout, minFreeSpace)

	inputSrc = '/dev/urandom' if randomSrc else '/dev/zero'

	# processes = []
	# for n in range(fileAmount):
	# 	p = Process(target=createFileViaDD, args=(fileSize, goodMntPoint, n))
	# 	p.start()
	# 	processes.append(p)

	# for process in processes:
	# 	process.join()

	# The above solution works too. The below is, IMHO, more elegant.
	# concurrent.futures.ProcessPoolExecutor() could be even more elegant...
	# ... but on some machines it causes sub 2 second processes take 
	# up to 3 times as long to execute, and that's a big NOPE from me.
	with Pool(processes=fileAmount) as pool:
		for n in range(fileAmount):
			result = pool.apply_async(createFileViaDD, (inputSrc, fileSize, goodMntPoint, n))
		pool.close()
		pool.join()


def createFileViaDD(inputSrc, size, dest, nbr):
	command = ['dd', f'if={inputSrc}', f'of={dest}{str(nbr)}.dat', f'count={str(size)}', 'bs=1024']
	# Uncomment next line for debug mode
	# command = ['sleep', '10']
	try: 
		p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
		p1.wait()
		if p1.stderr:
			raise(CommandExecutionException(command, p1.stderr.read()))
	except CommandExecutionException as e:
		print(e)

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
	parser.add_argument('-r', '--random',
						type=bool, nargs='?',
						const=True, default=False,
						help='Use random data rather then zeros')
	args = parser.parse_args()

	try:
		createAndFill(args.minspace, args.filesize, args.fileamount, args.random)
	except Exception as e:
		print("Couldn't complete the task: ", e)