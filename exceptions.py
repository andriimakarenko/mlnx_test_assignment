
###############################
#                             #
# Exceptions for assignment 1 #
#                             #
###############################

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

###############################
#                             #
# Exceptions for assignment 2 #
#                             #
###############################

class InvalidCredentialsFormatException(Exception):
	def __init__(self):
		self.message = """
The specified credentials are in an invalid format. Valid formats are:
1. -u USERNAME
2. -u USERNAME:PASSWORD"""
	def __str__(self):
		return self.message

class InvalidServerFormatException(Exception):
	def __init__(self):
		self.message = """
At least one of the servers is specified in an invalid format. The correct format is:
USERNAME:PASSWORD@HOST:PORT
That means there can be at most one '@' and at most one colon (':') to each side of it.
USERNAME: Optional. If not specified, user from -u / --login key is used. If that key isn't set, defaults to your username
PASSWORD: Optional. If omitted, public key based authentication is assumed. Cannot be specified without the USERNAME, as
	if the part to the left from '@' has no delimiters, it will be treated as a USERNAME
HOST: Obligatory. If there are no delimiters in the server target, everything provided will be treated as a HOST
PORT: Optional. Must be numeric"""
	def __str__(self):
		return self.message