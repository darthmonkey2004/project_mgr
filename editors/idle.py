import os
import subprocess

class idle():
	def __init__(self, startup_file=None, cwd=None, command=None, args=None, debug=False, script=None, include_environ=True, title='PMEditor - Idle'):
		if cwd is None:
			self.cwd = os.getcwd()
		else:
			self.cwd = cwd
		if startup_file is None:
			startup_file = os.path.join(os.getcwd(), 'project_mgr_config.py')
			
		self.startup_file = startup_file
		self.com = None
		self.command = command
		self.args = args
		self.debug = debug
		self.script = script
		self.include_environ = include_environ
		self.title = title
		self.files = []

	def editor(self, files=None):
		if files is None:
			if self.files != []:
				files = self.files
			else:
				files = []
		if len(files) > 0:
			fl = []
			for filepath in files:
				fl.append(f"'{filepath}'")
			files = " ".join(fl)
			self.com = f"idle -e {files}"
		else:
			self.com = "idle -e"
		self.com = f"{self.com}&"
		self.run(self.com)


	def shell(self, command=None, args=None, debug=False, script=None, include_environ=True, title='PMEditor - Idle'):
		if debug is None:
			debug = self.debug
		if debug:
			if self.include_environ:
				self.com = f"idle -t \'{self.title}\' -s -d"
			else:
				self.com = f"idle -t \'{self.title}\' -d"
		else:
			if self.include_environ:
				self.com = f"idle -t \'{self.title}\' -s"
			else:
				self.com = f"idle -t \'{self.title}\'"
		print(f"com:\'{self.com}\'")
		if command is None and self.args is None and debug is None and self.script is None:
			if self.include_environ:
				self.com = f"{self.com} -is"
			else:
				self.com = f"{self.com} -i"
		elif command is not None:
			if self.args is None:
				self.com = f"{self.com} -c {command}"
			else:
				if type(self.args) == list:
					self.args = " ".join(self.args)
				self.com = f"{self.com} -c \"{command} {self.args}\""
		elif self.script is not None:
			if self.args is None:
					self.com = f"{self.com} -r {self.script}"
			else:
				if type(self.args) == list:
					self.args = " ".join(self.args)
				self.com = f"{self.com} -r {self.script} {self.args}"
		self.com = f"{self.com}&"
		self.run(self.com)


	def ckcom(self, com):
		opts = ['-e', '-s', '-d', '-t', '-is', '-i', '-c', '-r']
		ok = False
		if com[:4] == 'idle':
			if com[:5] == 'idle ':
				for opt in opts:
					if opt in com:
						ok = True
			else:
				ok = True
		else:
			ok = False
		return ok

	def run(self, com=None):
		if not self.ckcom(com):
			raise Exception(f"Bad command: {com}")
			self.com = None
		else:
			self.com = com
		print("Running:", self.com)
		if os.path.exists(self.startup_file):
			subprocess.call(f"export IDLESTARTUP=\"{self.startup_file}\"; {self.com}", shell=True)
		else:
			subprocess.call(self.com, shell=True)
