import keyring
import os
import subprocess
from helper_utils.git import *
from editors.idle import *
from helper_utils.log import logger
from helper_utils.filesystem import *
from psg_creator.classes import *
from psg_creator.gui import *
from helper_utils.tar import *
logfile = os.path.join(os.path.expanduser("~"), '.project_manager', 'log.txt')
#log = logger().log_msg
log = logger.log_msg
ui = gui()
default_project_dir = 'var/dev'

get_git_file_adds_command = "data=\"$(git status | grep \"new file:\" | cut -d ':' -f 2)\"; data=\"${data// /}"


def select_all(win):
	lb = win.Rows[0][0].Rows[0][0]
	l = [i for i in range(0, len(lb.Values))]
	s = l[0]
	e = len(l)
	lb.widget.selection_set(first=s, last=e)
	return lb.Values

def clear_all(win):
	lb = win.Rows[0][0].Rows[0][0]
	l = [i for i in range(0, len(lb.Values))]
	s = l[0]
	e = len(l)
	lb.widget.selection_clear(first=s, last=e)
	return []

def win_main_menu():
	layout_obj = layout()
	layout_obj.add(ui._element('Button', button_text='New Project', expand_x=True, expand_y=True, key='-BUTTON_NEW_PROJECT-'))
	layout_obj.push()
	layout_obj.add(ui._element('Button', button_text='Load Project...', expand_x=True, expand_y=True, key='-BUTTON_LOAD_PROJECT-'))
	layout_obj.push()
	layout_obj.add(ui._element('Button', button_text='Settings', expand_x=True, expand_y=True, key='-BUTTON_SETTINGS-'))
	layout_obj.push()
	layout_obj.add(ui._element('Checkbox', text='Auto-Load Last Project', key='-AUTO_LOAD-'))
	layout_obj.add(ui._element('Checkbox', text='Debug Mode (Verbose)', key='-DEBUG-'))
	layout_obj.push()
	win = ui.child_window(layout_obj=layout_obj, title='Project Manager: Main Menu', run=False)
	return win

def win_project_master(pm=None):
	if pm is None:
		pm = get_pm()
	layout_obj = layout()
	layout_obj.add(ui._element('Listbox', expand_y=True, select_mode='multiple', values=pm.files, key='-PROJECT_FILES-'))
	layout_obj.push()
	layout_obj.add(ui._element('Button', button_text='Push', key='-BTN_PUSH-'))
	layout_obj.add(ui._element('Button', button_text='Pull', key='-BTN_PULL-'))
	layout_obj.add(ui._element('Button', button_text='Status', key='-BTN_STATUS-'))
	layout_obj.add(ui._element('Button', button_text='Open in Editor', key='-BTN_EDIT-'))
	layout_obj.add(ui._element('Button', button_text='Select All', key='-BTN_SELECT_ALL-'))
	layout_obj.add(ui._element('Button', button_text='Clear All', key='-BTN_CLEAR_ALL-'))
	layout_obj.push()
	layout_obj.add(ui._element('Button', button_text='Save', key='-BTN_SAVE-'))
	layout_obj.add(ui._element('Button', button_text='Save As...', key='-BTN_SAVE_AS-'))
	layout_obj.add(ui._element('Button', button_text='Add File...', key='-BTN_ADD_FILE-'))
	layout_obj.add(ui._element('Button', button_text='Remove file...', key='-BTN_REMOVE_FILE-'))
	layout_obj.add(ui._element('Button', button_text='Quit!', key='-BTN_QUIT-'))
	layout_obj.add(ui._element('Button', button_text='Main Menu', key='-BTN_MAIN_MENU-'))
	layout_obj.push()
	title = pm.name
	win = ui.child_window(layout_obj=layout_obj, title=title, run=False)
	return win


	


def win_settings(pm):
	layout_obj = layout()
	for k in pm.settings.keys():
		v = pm.settings[k]
		key = f"-{k.upper()}-"
		layout_obj.add(ui._element('Input', default_text=v, key=key))
		layout_obj.push()
	title = f"{pm.name} Settings"
	win = ui.child_window(layout_obj=layout_obj, title=title, run=False)
	return win

def add_file(pm, filepath):
	if os.path.exists(filepath):
		data = pm.fs.cat(filepath)
		fname = os.path.basename(filepath)
		newname = os.path.join(pm.project_path, fname)
		pm.fs.write(data=data, filepath=newname)
		log(f"ui.menus.add_file():Added file to project ({filepath} > {newname})!", 'info')
	else:
		log(f"ui.menus.add_file():Error - File doesn't exist ({filepath})!", 'error')


def get_pm(auto_load=True):
	win = win_main_menu()
	quit = False
	debug = True
	pm = None
	if auto_load:
		pm = load_project()
		if pm is not None:
			win.close()
			return pm
	while True:
		event, values = win.read()
		if event == sg.WIN_CLOSED or quit:
			if not win.was_closed():
				win.close()
			break
		elif event == '-BUTTON_NEW_PROJECT-':
			data = new_project()
			name = data['name']
			project_path = data['project_path']
			if not os.path.exists(project_path):
				filesystem().mkdir(project_path)
				os.chdir(project_path)
			default_project_dir = data['default_project_dir']
			url = data['url']
			email = data['email']
			user = data['user']
			token = data['token']
			pm = project_mgr(debug=debug, editor_name='idle', project_path=project_path, default_project_dir=default_project_dir, git_url=url, settings=data)
			break
		elif event == '-BUTTON_LOAD_PROJECT-':
			project_path = ui.file_browser(browse_type='folder', cwd='/var/dev/')
			pm = project_mgr(debug=debug, editor_name='idle', project_path=project_path)
			break
		elif event == '-BUTTON_SETTINGS-':
			pass
		elif event == '-AUTO_LOAD-':
			pm = load_project()
			log(f"Poject loaded: {pm.name}", 'info')
			break
		elif event == '-DEBUG-':
			pass
	if not win.was_closed():
		win.close()
	return pm

def load_project(debug=True):
	try:
		settings_file = 'settings.dat'
		data = None
		if os.path.exists(settings_file):
			with open(settings_file, 'rb') as f:
				data = pickle.load(f)
				f.close()
		else:
			log(f"menus.load_settings():Error - no settings file found ({settings_file})!", 'error')
		pm = project_mgr(debug=debug, editor_name='idle', project_path=data['project_path'])
		return pm
	except Exception as e:
		log(f"ui.menus.load_project():Error - {e}", 'error')
		return None

def save_settings(pm):
	settings = pm.settings
	with open(pm.settings_file, 'wb') as f:
		pickle.dump(settings, f)
		f.close()

def get_token(email):
	try:
		token = keyring.get_password(service_name="git_token", username=email)
	except Exception as e:
		print("Error getting token:", e)
		token = None
	return token

def store_token(token=None, user=None, email=None):# user is git Name, email is git email(for login)
	keyring.set_password(service_name="git_token", username=email, password=token)

def browse_new_repo():
	url = "https://github.com/new"
	ret = subprocess.check_output(f"xdg-open \"{url}\"", shell=True).decode().strip()
	if ret != '':
		print("Error openin browser:", ret)

def win_new_project():
	layout_obj = layout()
	layout_obj.add(ui._element('Listbox', values=[], expand_x=True, expand_y=True, key='-LISTBOX_REPOS-'))
	layout_obj.push()
	layout_obj.add(ui._element('Button', button_text='Update Repos', key='-BTN_UPDATE_REPOS-'))
	layout_obj.push()
	layout_obj.add(ui._element('Text', text='Project Name:', key='-TEXT_NAME-'))
	layout_obj.add(ui._element('Input', default_text=None, key='-NAME-'))
	layout_obj.add(ui._element('Button', button_text='New Repository...', key='-NEW_REPO-'))
	layout_obj.push()
	layout_obj.add(ui._element('Text', text='Local Project Directory:', key='-PROJECT_PATH_TEXT-'))
	layout_obj.add(ui._element('Input', default_text=default_project_dir, key='-INPUT_PROJECT_PATH-'))
	layout_obj.add(ui._element('Button', button_text='Select project location...', key='-PROJECT_PATH-'))
	layout_obj.push()
	layout_obj.add(ui._element('Text', text='Git URL:', key='-TEXT_URL-'))
	layout_obj.add(ui._element('Input', key='-URL-'))
	layout_obj.push()

	layout_obj.add(ui._element('Text', text='Email:', key='-TEXT_EMAIL-'))
	layout_obj.add(ui._element('Input', key='-EMAIL-'))
	layout_obj.add(ui._element('Button', button_text='Load Token', key='-BTN_LOAD_TOKEN-'))
	layout_obj.add(ui._element('Button', button_text='Store Token', key='-BTN_STORE_TOKEN-'))
	layout_obj.push()
	layout_obj.add(ui._element('Text', text='Git Username:', key='-TEXT_USERNAME-'))
	layout_obj.add(ui._element('Input', key='-USERNAME-'))
	layout_obj.push()
	layout_obj.add(ui._element('Text', text='Token:', key='-TEXT_TOKEN-'))
	layout_obj.add(ui._element('Input', key='-TOKEN-'))
	layout_obj.push()
	layout_obj.add(ui._element('Button', button_text='Ok', key='-OK-'))
	layout_obj.add(ui._element('Button', button_text='Cancel', key='-CANCEL-'))
	layout_obj.add(ui._element('Button', button_text='Break', key='-BREAK-'))
	layout_obj.push()
	win = ui.child_window(layout_obj=layout_obj, title='Add Menu Item', run=False)
	return win

def new_project(name=None, project_path=None, default_project_dir='/var/dev', url=None, email=None, user=None, token=None):
	win = win_new_project()
	if project_path is not None:
		win['-INPUT_PROJECT_PATH-'].update(project_path)
	if name is not None:
		name = name.replace('_', ' ').title()
		win['-NAME-'].update(name)
	if default_project_dir is not None:
		win['-INPUT_PROJECT_PATH-'].update(default_project_dir)
	if url is not None:
		win['-URL-'].update(url)
	if user is not None:
		win['-USERNAME-'].update(user)
	if email is not None:
		win['-EMAIL-'].update(email)
	while True:
		event, values = win.read()
		if event == sg.WIN_CLOSED or event == '-BREAK-':
			break
		elif event == '-PROJECT_PATH-':
			default_project_dir = ui.file_browser(browse_type='folder', cwd='/var/dev')
			print("set project directory:", default_project_dir)
			win['-INPUT_PROJECT_PATH-'].update(default_project_dir)
		elif event == '-INPUT_PROJECT_PATH-':
			default_project_dir = values[event]
		elif event == '-URL-':
			url = values[event]
			try:
				user = url.split('com/')[1].split('/')[0]
				name = url.split(f"{user}/")[1].split('.')[0].replace('_', ' ').title()
				win['-USERNAME-'].update(user)
				win['-NAME-'].update(name)
			except:
				pass
			print("Repository url set:", url)
		elif event == '-NAME-':
			name = values[event].replace(' ', '_').lower()
			project_path = os.path.join(default_project_dir, name)
			if user is None:
				try:
					user = email.split('@')[0]
					win['-USERNAME-'].update(user)
				except:
					print("Please set username or email first!")
			url = f"https://github.com/{user}/{name}.git"
			win['-URL-'].update(url)
			print("Repository name set:", name)
		elif event == '-EMAIL-':
			email = values[event]
			if '@' in email:
				user = email.split('@')[0]
				win['-USERNAME-'].update(user)
				url = f"https://github.com/{user}/{name}.git"
				win['-URL-'].update(url)
			if '.com' in email:
				token = get_token(email)
				win['-TOKEN-'].update(token)
		elif event == '-BTN_UPDATE_REPOS-':
			if user is None:
				print("Set email or username first!")
			else:
				win['-LISTBOX_REPOS-'].update(get_repositories(user))
				url = f"https://github.com/{user}/{name}.git"
				win['-URL-'].update(url)
		elif event == '-BTN_LOAD_TOKEN-':
			try:
				token = get_token(email)
				win['-TOKEN-'].update(token)
			except:
				print("set email or user first!")
		elif event == '-BTN_STORE_TOKEN-':
			try:
				store_token(token)
				print("Token stored!")
			except:
				print("set token first!")
		elif event == '-NEW_REPO-':
			browse_new_repo()
		elif event == '-OK-':
			d = {}
			d['default_project_dir'] = default_project_dir
			d['project_path'] = project_path
			d['name'] = name
			d['url'] = url
			d['email'] = email
			d['user'] = user
			d['token'] = token
			win.close()
			return d
		elif event == '-CANCEL-':
			win.close()
			return {}


class project_mgr():
	def __init__(self, new=False, editor_name='idle', project_path=None, debug=False, default_project_dir='/var/dev', git_url=None, auto_load_last=True, settings=None):
		self.backup_file = None
		self.settings = settings
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
		if not os.path.exists(self.data_dir):
			self.fs.mkdir(self.data_dir)

	def track_changes(self):
		patterns = ["new file", "modified", "deleted"]
		l = []
		for pattern in patterns:
			com = f'git status | grep "{pattern}:" | cut -d ":" -f 2'
			try:
				for i in subprocess.check_output(com, shell=True).decode().strip().splitlines():
					l.append(f"{pattern}:{i.strip()}")
			except Exception as e:
				self.log(f"Error - git status check failed! ({e})", 'error')
		return l


	def _init(self, path=None):
		if path is not None:
			self.project_path = path
		self.fs = filesystem.filesystem(cwd=self.project_path)
		if self.project_path is None:
			projects = self.fs.find(path=self.default_project_dir)
			self.name = f"new_project_{len(projects)}"
			self.project_path = os.path.join(self.default_project_dir, self.name)
		if os.path.exists(self.project_path):
			self.git = git_mgr(path=self.project_path)
		else:
			if self.url is None or self.new:
				if self.settings is None:
					print("self.settings:", self.settings)
					self.settings = new_project()
				self.git = git_mgr(init=True, path=self.settings['project_path'])
			else:
				self.git = git_mgr(url=self.url)
		#self.logger = logger(logfile=self.logfile, verbose=self.debug)
		#self.log = self.logger.log_msg
		self.editor = self.set_editor(editor_name=self.editor_name, cwd=self.project_path)
		self.files = self.get_files()
		self.name = self.git.name.replace('_', ' ').title()
		self.tar = tar(target_dir=self.project_path, compression='gz')

	def backup(self, path=None):
		if path is None:
			path = self.project_path
		fname = f"{self.name.replace(' ', '_').lower()}.{self.get_backups(path=self.data_dir, ct=True)}"
		filepath = self.tar.add_directory(target_dir=self.project_path, archive_name=fname)
		fname = os.path.basename(filepath)
		self.backup_file = os.path.join(self.data_dir, fname)
		self.fs.mv(filepath, self.backup_file)
		return 

	def get_backups(self, path=None, ct=False):
		if path is None:
			path = self.data_dir
		files = self.fs.find(path=path, pattern=[f"*.{self.tar.compression}*"])
		if ct:
			return len(files) + 1
		else:
			return files


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
		files = self.fs.find(path=path, pattern=["*.py", "*todo*", "*TODO*"])
		l = []
		exc = []
		for filepath in files:
			for ignore in self.ignore:
				if ignore not in filepath:
					if filepath not in exc and filepath not in l:
						l.append(filepath)
				else:
					exc.append(filepath)
		self.files = l
		return self.files
			

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

	def _get_added_files(self):
		ret = subprocess.check_output('git status | grep "new file:" | cut -d ":" -f 2', shell=True).decode()
		added_files = ret.replace(' ', '').strip().splitlines()
		return added_files


	def new(self, user=None, path=None, git_url=None):
		self._init(path=path)
		if user is None:
			user = self.git.user
		if path is None:
			if os.path.exists(path):
				self.project_path = path
				os.chdir(self.project_path)
				self.git = git_mgr(path=self.project_path, email=self.email, name=self.name, token=self.token)
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
				self.git = git_mgr(url=self.url, email=self.email, name=repo_name, token=self.token)
				self.project_path = self.git.path
				self.name = self.git.name
		elif path is not None:
			self.name = os.path.basename(path)
			if not os.path.exists(path):
				self.url = f"https://github.com/{user}/{self.name}.git"
				self.git = git_mgr(url=self.url, email=self.email, name=repo_name, token=self.token)
				self.project_path = self.git.path
			else:
				try:
					self.git = git_mgr(path=self.project_path, email=self.email, name=self.name, token=self.token)
				except Exception as e:
					txt = f"project_mgr.main.new():Error - Couldn't init git at {self.project_path}!"
					self.log(txt, 'error')
					raise Exception(txt)

