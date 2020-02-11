#!/usr/bin/env python3

from os import *
import subprocess
from multiprocessing import Process, Pool
import pty
import paramiko
import argparse
import getpass
import traceback
from exceptions import *

class Job:
	command = ''
	defaultUsername = ''
	defaultPassword = ''
	servers = []
	output = []

	def __init__(self):
		self.defaultUsername = getpass.getuser()

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

	def getResults(self):
		output = ''
		for result in self.output:
			output += f'Server at {result["host"]}:\n\n'
			output += f'stdout:\n{result["stdout"]}\n'
			output += f'stderr:\n{result["stderr"]}\n'
			output += f'{"—" * 80}\n\n'
		return output

	def run(self):
		with Pool(processes=len(self.servers)) as pool:
			for n in range(len(self.servers)):
				result = pool.apply_async(self.execOverSSH, (n,))
				out = result.get(timeout=100)
				self.output.append({
					'host': self.servers[n]['host'],
					'stdout': out[0],
					'stderr': out[1]
					})
			pool.close()
			pool.join()
		print(job.getResults())

	def execOverSSH(self, serverNumber):
		server = self.servers[serverNumber]

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(
			server['host'],
			port = server['port'],
			username = server['login'],
			password = server['password'] if server['password'] else None
		)
		stdin, stdout, stderr = ssh.exec_command(self.command)
		result = (stdout.read().decode(), stderr.read().decode())
		return result

	


	# def execOverSSHKey(self, serverNumber):
	# 	server = self.servers[serverNumber]
	# 	command = [
	# 			'ssh', '-t', '-p', f'{server["port"]}',
	# 			f'{server["login"]}@{server["host"]}',
	# 			# '-o', 'NumberOfPasswordPrompts=1',
	# 			f"\'/usr/bin/{self.command}\'"
	# 	]
	# 	try: 
	# 		p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	# 		p1.wait()
	# 		if p1.returncode != 0:
	# 			print(p1.stdout.read())
	# 			raise(CommandExecutionException(command, p1.stderr.read()))
	# 		self.output.append(p1.stdout.read())
	# 		print(self.output)
	# 		print(self.getResults())
	# 	except CommandExecutionException as e:
	# 		if args.debug:
	# 			traceback.print_exc()
	# 		else:
	# 			print(e)

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
			print('Could not execute the job. Here\'s why:', e)