#!/usr/bin/env python3

from os import *
import subprocess

def createAndFill(x, y, z):
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

	

# x = input("Please specify X: ")
# y = input("Please specify Y: ")
# z = input("Please specify Z: ")

try:
	# createAndFill(x, y, z)
	createAndFill(5, 5, 5)
except Exception as e:
	print("Couldn't complete the task: ", e)