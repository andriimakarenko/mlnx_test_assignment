class DangerousArgsCombinationException(Exception):
	def __init__(self):
		self.message = """
The combination of arguments you provided is dangerous.
The amount of free space required should be at least enough to fit the files that will be written.
Therefore, minimum required free space must be equal to or more than amount of files times each file's size.
"""
	def __str__(self):
		return self.message

class InsufficientFreeSpaceException(Exception):
	def __init__(self):
		self.message = """
Could not find a mounted partition with enough free space.
Try setting a smaller minimum required free space. 
"""
	def __str__(self):
		return self.message