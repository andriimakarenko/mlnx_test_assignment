#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process
from functools import wraps
from time import time

# I would separate this in multiple functions if it wasn't for the deadline
def createAndFill(x, y, z):
	if z * y > x:
		raise(Exception("Invalid parameters. Z times Y must be less than X"))

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
		raise(Exception("Could not find a disk with enough free space"))

	while z > 0:
		p = Process(target=createFileViaDD, args=(y, goodMntPoint, z))
		p.start()
		z -= 1

def createFileViaDD(size, dest, nbr):
	command = 'dd if=/dev/zero of=' + dest + str(nbr) + '.dat count=' + str(size) + ' bs=1024'
	print(command)
	p1 = subprocess.run(command, capture_output=True, shell=True)
	# while p1.poll() is None:
	# 	continue

# This should be a function but the deadline is TIGHT
x = y = z = None
while type(x) is not int:
	try:
		x = input("Please specify X (numbers only): ")
		x = int(x)
	except ValueError:
		continue

while type(y) is not int:
	try:
		y = input("Please specify Y (numbers only): ")
		y = int(y)
	except ValueError:
		continue

while type(z) is not int:
	try:
		z = input("Please specify Z (numbers only): ")
		z = int(z)
	except ValueError:
		continue

try:
	createAndFill(x, y, z)
except Exception as e:
	print("Couldn't complete the task: ", e)