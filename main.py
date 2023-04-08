import os
import subprocess
from helper_utils.git import *
from helper_utils.filesystem import filesystem
from editors.idle import *
from helper_utils.log import logger


class project_manager():
	def __init__(self, editor_name='idle', project_path=None, debug=False):
		self.debug = debug
		self.data_dir = os.path.join(os.path.expanduser("~"), '.project_manager')
		self.project_path = project_path
		self.git = git_mgr(path=self.project_path)
		self.logfile = os.path.join(self.data_dir, 'log.txt')
		self.logger = logger(logfile=self.logfile, verbose=self.debug)
		self.log = self.logger.log_msg
		self.editor = self.set_editor(editor_name=editor_name, cwd=self.project_path)
		self.fs = filesystem(cwd=self.project_path)
		self.files = self.get_files()

	def get_files(self, path=None):
		if path is None:
			path = self.project_path
		return self.fs.find(path, pattern="*.py")

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
			log(txt, 'error')
			raise Exception(txt)
		return self.editor

	def new(self, path=None, git_url=None):
		if path is None and git_url is None:
			txt = "TODO: Insert ui driven new repo creator menu"
			log(txt, 'error')
			raise Exception(txt)
		if path is not None:
			self.project_path = path
		if not os.path.existS(self.project_path):
			log(f"project_mgr.main.new():Project path doesn't exist! ({self.project_path}) - Creating...", 'warning')
		self.name = os.path.basename(self.project_path)

		
