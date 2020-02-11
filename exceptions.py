class DangerousArgsCombinationException(Exception):
	def __init__(self):
		self.message = """
The combination of arguments you provided is dangerous.
The amount of free space required should be at least enough to fit the files that will be written.
Therefore, minimum required free space must be equal to or more than amount of files times each file's size."""
	def __str__(self):
		return self.message

class InsufficientFreeSpaceException(Exception):
	def __init__(self):
		self.message = """
Could not find a mounted partition with enough free space.
Try setting a smaller minimum required free space. """
	def __str__(self):
		return self.message

# Turns out, subpocess.run handles such exception on its own, so this exception is unneeded for now
class CommandExecutionException(Exception):
	def __init__(self, command):
		self.message = ('Could not execute the following command:\n'
		f'\'{command}\'\n'
		'You are probably running this script on a non POSIX-compliant OS (like, maybe, MS Windows)\n'
		'That is not da wae')
	def __str__(self):
		return self.message