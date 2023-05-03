from helper_utils import filesystem
from psg_creator.gui import *
import importlib
import os
import inspect
import sys
sys.path.append(os.path.join(os.path.expanduser("~"), '.gui', 'user'))

def import_user_functions():
	user_functions = importlib.import_module('user_functions')
	globals()['user_functions'] = user_functions
	return user_functions

class target_obj():
	def __init__(self, key, target_key, name=None, filepath=None):
		if target_key is None:
			print("WARNING: target key is None!")
		print("target_key (usercode.target_obj):", target_key)
		self.target_key = target_key
		self.user_functions = import_user_functions()
		if name is None:
			self.name = key.split('-')[1].lower()
		else:
			self.name = name

		self.key = key
		print("Usercode.py - name and key set!", self.name, self.key)
		self.restart = False
		self.fs = filesystem.filesystem()
		self.ui = gui()
		self.path = os.path.join(os.path.expanduser("~"), '.gui', 'user')
		self.user_functions_file = os.path.join(self.path, 'user_functions.py')
		self.user_functions_data = self.get_user_functions()
		init_py = os.path.join(self.path, '__init__.py')
		if not os.path.exists(self.path):
			self.fs.mkdir(self.path)
		if not os.path.exists(init_py):
			self.fs.touch(init_py)
		try:
			self.code = self.ui.load_text()
		except Exception as e:
			print("Error loading function data:", e)
			self.code = None
		self.target = self.get_target()
		if self.target is None and self.name not in list(self.user_functions_data.keys()):
			self.code = self.ui.get_user_code()
			self.restart = True
			print("Changes made won't reflect until next restart! Please restart now before continuing...")
		elif self.target is None and self.name in list(self.user_functions_data.keys()):
			self.restart = True
			print(f"Unable to set target on object (User code data has changed, Restart required!)")

	def get_user_functions(self, user_functions_file=None):
		if user_functions_file is None:
			user_functions_file = self.user_functions_file
		with open(user_functions_file, 'r') as f:
			text = f.read().splitlines()
			f.close()
		funcs = {}
		for line in text:
			if 'def ' in line:
				#print("line:", line)
				name = line.split('def ')[1].split('(')[0]
				args = line.split('(')[1].split(')')[0]
				#print("args:", args)
				arglist = []
				if ', ' in args:
					s = ', '
				elif ',' in args and ', ' not in args:
					s = ','
				else:
					s = None
				if s is not None:
					chunks = args.split(', ')
					for chunk in chunks:
						if '=' in chunk:
							arg = chunk.split('=')[0]
							default = chunk.split('=')[1]
						else:
							arg = chunk
							default = None
						arglist.append((arg, default))
				funcs[name] = arglist
		return funcs
		


	def get_arguments(self, target=None):
		if target is None:
			target = self.target
		self.args = inspect.getfullargspec(target)[0]
		return self.args


	def get_target(self, name=None):
		if name is None:
			name = self.name
		print(f"get_target(name={name})")
		try:
			self.target = self.user_functions.__dict__[name]
		except Exception as e:
			print("Error setting target: ", e, "name:", name)
			return None
	#	try:
		self.args = self.get_arguments(self.target)
	#	except Exception as e:
	#		print("Error setting arguments for target ({name}): {e}")
	#		self.args = None
		return self.target

if __name__ == "__main__":
	data = get_user_code()
	print(data)
