#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process, Pool
import argparse
import getpass
import traceback
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
		result = f'Command: {self.command}\n\nServers:\n'
		for idx, server in enumerate(self.servers):
			serverStr = f'\nServer #{idx}:\nLogin: {server["login"]}\n'
			if server["password"]:
				serverStr += f'Password: {server["password"]}\n'
			serverStr += f'Host: {server["host"]}\nPort: {server["port"]}\n'
			result += serverStr
		return result

	def setCommand(self, commandStr):
		self.command = commandStr

	def setDefaultCredentials(self, logpassStr):
		credentials = logpassStr.split(':')
		self.defaultUsername = credentials[0]
		if len(credentials) == 2:
			self.defaultPassword = credentials[1]
		if len(credentials) > 2:
			raise(InvalidCredentialsFormatException)

	def setServers(self, serversStr):
		serverStrArr = serversStr.split(',')
		
		# There definitely is a library that does exactly this validation
		# But I want to demonstrate I can write it from scratch if needed
		for serverStr in serverStrArr:
			server = {}
			detailGroups = serverStr.split('@') # assumed input is either 'destination' or 'credentials@destination'
			if len(detailGroups) > 2: # if there's more than one '@' in the entry
				raise(InvalidServerFormatException)

			destination = detailGroups[-1]
			destinationGroup = destination.split(':')
			if len(destinationGroup) > 2: # if there's more than one ':' in the destination part
				raise(InvalidServerFormatException)
			server['host'] = destinationGroup[0]
			if len(destinationGroup) == 2: # i.e. if there is a ':' in the destination part
				if not destinationGroup[1].isnumeric(): # if port is non-numeric
					raise(InvalidServerFormatException)
				server['port'] = destinationGroup[1]
			else:
				server['port'] = 22
			
			if len(detailGroups) == 2: # i.e. if the entry has '@' in it
				credentials = detailGroups[0]
				credentialsGroup = credentials.split(':')
				if len(credentialsGroup) > 2: # if there's more than one ':' in the credentials part
					raise(InvalidServerFormatException)
				server['login'] = credentialsGroup[0]
				if len(credentialsGroup) == 2: # i.e. if there is a ':' in the credentials part
					server['password'] = credentialsGroup[1]
				else:
					server['password'] = ''
			else:
				server['login'] = self.defaultUsername
				server['password'] = self.defaultPassword

			self.servers.append(server)

###################################################################################################################################

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run a command provided by user on multiple server, collect and print the output')
	parser.add_argument('-c', '--command',
						type=str, metavar='', required=True,
						help='Command to execute on servers')
	parser.add_argument('-s', '--servers',
						type=str, metavar='', required=True,
						help=('A comma-separated collection of USER:PASSWORD@HOST:PORT arguments. '
							'Example: --servers=admin@192.168.1.47,andy:p4ssw0rd@192.168.1.80,master@andymac.space:44. '
							'USER, if not specified defaults to the current username. '
							'PASSWORD, if not specified, defaults to none (i.e. public key based authentication). '
							'PORT, if not specified, defaults to 22.'))
	parser.add_argument('-u', '--logpass',
						type=str, metavar='', required=False,
						help=('Username for all servers. Does not override --servers directive, only adds '
							'the specified username (with or without password) to the servers where none was specified before. '
							'Designed to use if some or all of your server accounts share the same username. '
							'Examples: --username=admin:password, --username=johndoe '))
	parser.add_argument('-d', '--debug',
						type=bool, nargs='?', metavar='',
						const=True, default=False,
						help='Run the script in debug mode (verbose fails, stacktraces on)')
	args = parser.parse_args()

	job = Job()
	try:
		job.setCommand(args.command)
		if args.logpass:
			job.setDefaultCredentials(args.logpass)
		job.setServers(args.servers)
		print(job)
	except Exception as e:
		if args.debug:
			traceback.print_exc()
		else:
			print('Could not set up the job. Here\'s why:', e)