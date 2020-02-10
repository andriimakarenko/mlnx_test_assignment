#!/usr/bin/env python3

def createAndFill(x, y, z):
	pass

x = input("Please specify X")
y = input("Please specify Y")
z = input("Please specify Z")

try:
	createAndFill(x, y, z)
except Error as err:
	print("Couldn't complete the task: ", err)