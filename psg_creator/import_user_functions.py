import os
import importlib

def import_user_functions():
	path = os.path.join(os.path.expanduser("~"), '.gui', 'user')
	os.chdir(path)
	user_functions = importlib.import_module('user_functions')
	globals()['user_functions'] = user_functions
	return user_functions

