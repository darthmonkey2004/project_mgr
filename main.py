import os
import subprocess
from helper_utils.git import *
from editors.idle import *
from helper_utils.log import logger
from helper_utils.filesystem import *
logfile = os.path.join(os.path.expanduser("~"), '.project_manager', 'log.txt')
#log = logger().log_msg
log = logger.log_msg

class project_mgr():
	def __init__(self, new=False, editor_name='idle', project_path=None, debug=False, default_project_dir='/var/dev', git_url=None, auto_load_last=True):
		self.auto_load_last = auto_load_last
		self.data_dir = os.path.join(os.path.expanduser("~"), '.project_manager')
		self.url = git_url
		self.default_project_dir = default_project_dir
		self.debug = debug
		self.project_path = project_path
		self.logfile = os.path.join(self.data_dir, 'log.txt')
		self.log = log
		self.editor_name = editor_name
		self.files = []
		self.settings_file = os.path.join(self.project_path, 'settings.dat')
		self.ignore = ['__init__', '.git', 'README']
		if new:
			self.new(path=self.project_path, git_url=self.url)
			self.save_settings()
		else:
			if os.path.exists(self.settings_file):
				self.settings = self.load_settings()
				self._init()
			else:
				self._init()
				self.save_settings()

	def _init(self, path=None):
		if path is not None:
			self.project_path = path
		self.fs = filesystem(cwd=self.project_path)
		if self.project_path is None:
			projects = self.fs.find(path=self.default_project_dir)
			self.name = f"new_project_{len(projects)}"
			self.project_path = os.path.join(self.default_project_dir, self.name)
		if os.path.exists(self.project_path):
			self.git = git_mgr(path=self.project_path)
		else:
			if self.url is None or self.new:
				self.settings = new_project()
				self.git = git_mgr(path=self.settings['project_path'])
			else:
				self.git = git_mgr(url=self.url)
		#self.logger = logger(logfile=self.logfile, verbose=self.debug)
		#self.log = self.logger.log_msg
		self.editor = self.set_editor(editor_name=self.editor_name, cwd=self.project_path)
		self.files = self.get_files()
		self.name = self.git.name.replace('_', ' ').title()

	def load_settings(self):
		with open(self.settings_file, 'rb') as f:
			self.settings = pickle.load(f)
			f.close()
		for k in self.settings.keys():
			v = self.settings[k]
			self.__dict__[k] = v
		return self.settings

	def save_settings(self, settings=None):
		if settings is not None:
			self.settings = settings
		elif settings is None:
			settings = {}
			settings['url'] = self.url
			settings['default_project_dir'] = self.default_project_dir
			settings['debug'] = self.debug
			settings['project_path'] = self.project_path
			settings['url'] = self.url
			settings['logfile'] = self.logfile
			settings['editor_name'] = self.editor_name
			settings['files'] = self.files
			settings['auto_load_last'] = True
			self.settings = settings
		if settings['url'] is None:
			settings['url'] = self.git.url
		with open(self.settings_file, 'wb') as f:
			pickle.dump(settings, f)
			f.close()


	def get_files(self, path=None):
		if path is None:
			path = self.project_path
		files = self.fs.find(path, pattern="*.py")
		l = []
		exc = []
		for filepath in files:
			for ignore in self.ignore:
				if ignore not in filepath:
					if filepath not in exc and filepath not in l:
						l.append(filepath)
				else:
					exc.append(filepath)
		if l != []:
			self.files = l
			return self.files
		else:
			raise Exception("Files list empty!")
			

	def set_editor(self, editor_name=None, cwd=None):
		if cwd is not None:
			self.project_path = cwd
		if editor_name is None:
			editor_name = 'idle'
		self.editor_name = editor_name
		if self.editor_name == 'idle':
			self.editor = idle(cwd=self.project_path, debug=self.debug)
		else:
			txt = f"TODO: add additional editor classes!"
			self.log(txt, 'error')
			raise Exception(txt)
		return self.editor

	def _add_existing_repo(self, path):
		print("Adding existing repo at:", path)
		self.project_path = path
		self.settings = new_project()


	def new(self, user=None, path=None, git_url=None):
		self._init(path=path)
		if user is None:
			user = self.git.user
		if path is None:
			if os.path.exists(path):
				self.project_path = path
				os.chdir(self.project_path)
				self.git = git_mgr(path=self.project_path)
				self.url = self.git.url
				self.name = self.git.name
			else:
				if git_url is None:
					old_repos = self.git.get_repositories()
					self.git._browse_create_repo()
					repo_name = input("Enter repo name: (blank to auto detect):")
					if repo_name == '':
						new_repos = self.git.get_repositories()
						for repo in new_repos:
							if repo not in old_repos:
								repo_name = repo
								break
					self.url = f"https://github.com/{user}/{repo_name}.git"
				else:
					self.url = git_url
				self.git = git_mgr(url=self.url)
				self.project_path = self.git.path
				self.name = self.git.name
		elif path is not None:
			self.name = os.path.basename(path)
			if not os.path.exists(path):
				self.url = f"https://github.com/{user}/{self.name}.git"
				self.git = git_mgr(url=self.url)
				self.project_path = self.git.path
			else:
				try:
					self.git = git_mgr(path=self.project_path)
				except Exception as e:
					txt = f"project_mgr.main.new():Error - Couldn't init git at {self.project_path}!"
					self.log(txt, 'error')
					raise Exception(txt)

		
