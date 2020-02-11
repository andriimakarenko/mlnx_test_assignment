#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process, Pool
from pexpect import pxssh
import pty
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

	def run(self):
		with Pool(processes=len(self.servers)) as pool:
			for n in range(len(self.servers)):
				# print(f'In server #{n}')
				if self.servers[n]['password']:
					result = pool.apply_async(self.execOverSSHPass, (n,))
				else:
					result = pool.apply_async(self.execOverSSHKey, (n,))
				# print(result.get(timeout=20))
			pool.close()
			pool.join()

	# def execOverSSHPass(self, serverNumber):
	# 	server = self.servers[serverNumber]

	# 	connection = pxssh.pxssh()
	# 	try:
	# 		if not connection.login(server=server['host'], username=server['login'], password=server['password'], port=server['port']):
	# 			print("SSH session failed on login.")
	# 			print(str(connection))
	# 		else:
	# 			print("SSH session login successful")
	# 			connection.sendline(server['command'])
	# 			connection.prompt()
	# 			print(connection.before)
	# 			connection.logout()
	# 	except Exception as e:
	# 		print(e)

	# def execOverSSHPass(self, serverNumber):
	# 	server = self.servers[serverNumber]

	# 	command = [
	# 			'ssh', '-t',
	# 			f'{server["login"]}:{server["password"]}@{server["host"]}:{server["port"]}',
	# 			'-o', 'NumberOfPasswordPrompts=1',
	# 			self.command
	# 	]
	# 	pid, child_fd = pty.fork()
	# 	print(command)
	# 	if not pid:
	# 		execv(command[0], command)

	# 	while True:
	# 		try:
	# 			output = read(child_fd, 1024).strip()
	# 		except:
	# 			print('Output reading fail')
	# 			break
	# 		lower = output.lower()
	# 		# Write the password
	# 		if b'password:' in lower:
	# 			write(child_fd, server['password'] + b'\n')
	# 			break
	# 		elif b'are you sure you want to continue connecting' in lower:
	# 			# Adding key to known_hosts
	# 			write(child_fd, b'yes\n')
	# 		else:
	# 			print('Error:', output.decode())

	# 	output = []
	# 	while True:
	# 		try:
	# 			output.append(read(child_fd, 1024).strip())
	# 		except:
	# 			break

	# 	waitpid(pid)
	# 	print(''.join(output))

	def execOverSSHPass(self, serverNumber):
		print('Servers with login-password authentication are not yet supported')

	def execOverSSHKey(self, serverNumber):
		print("in there")

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
		# print(job)
	except Exception as e:
		if args.debug:
			traceback.print_exc()
		else:
			print('Could not set up the job. Here\'s why:', e)

	try:
		job.run()
	except Exception as e:
		if args.debug:
			traceback.print_exc()
		else:
			print('Could not set up the job. Here\'s why:', e)