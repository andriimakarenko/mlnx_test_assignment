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
	def __init__(self, command, stderr):
		self.message = ('Could not execute the following command:\n'
		f'{" ".join(command)}\n'
		'Verify that you have enough rights for it and that your OS is POSIX-compliant (i.e. not Windows)\n'
		'The error that the command failed with, was:\n'
		f'{stderr}')
	def __str__(self):
		return self.message