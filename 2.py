#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process, Pool
import argparse
import getpass
from exceptions import *

class Job:
	command = ''
	defaultUsername = ''
	defaultPassword = ''
	servers = []

	def __init__(self):
		self.defaultUsername = getpass.getuser()
		# print(f'Default username set to {self.defaultUsername}')

	def __str__(self):
		result = f'Command: {self.command}\nServers:'
		for idx, server in enumerate(self.servers):
			serverStr = f'\nServer #{idx}:\n Login: {server.login}\n'
			if server.password:
				serverStr += f'Password: {server.password}\n'
			serverStr += f'Host: {server.password}\n Port: {server.port}\n'
			result += serverStr
		return result

	def setCommand(self, commandStr):
		self.command = commandStr

	def setDefaultCredentials(self, logpassStr):
		credentials = logpassStr.split(':')
		self.defaultUsername = credentials[0]
		if len(credentials) == 2:
			defaultPassword = credentials[1]
		if len(credentials) > 2:
			raise(InvalidCredentialsFormatException)

	def setServers(self, serversStr):
		pass


###################################################################################################################################

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run a command provided by user on multiple server, collect and print the output')
	parser.add_argument('-c', '--command',
						type=str, metavar='', required=True,
						help='Command to execute on servers')
	parser.add_argument('-s', '--servers',
						type=str, metavar='', required=True,
						help=('A comma-separated collection of USER:PASSWORD@HOST:PORT arguments. '
							'Example: --servers=admin@192.168.1.47,andy:p4ssw0rd@192.168.1.80,master@andymac.space. '
							'USER, if not specified defaults to the current username. '
							'PASSWORD, if not specified, defaults to none (i.e. public key based authentication). '
							'PORT, if not specified, defaults to 22.'))
	parser.add_argument('-u', '--logpass',
						type=str, metavar='', required=False,
						help=('Username for all servers. Does not override --servers directive, only adds '
							'the specified username (with or without password) to the servers where none was specified before. '
							'Designed to use if some or all of your server accounts share the same username. '
							'Examples: --username=admin:password, --username=johndoe '))
	args = parser.parse_args()

	job = Job()
	job.setCommand(args.command)
	if args.logpass:
		job.setDefaultCredentials(args.logpass)
	job.setServers(args.servers)
	print(job)