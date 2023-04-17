import keyring
from psg_creator.gui import *
from psg_creator.classes import *
from helper_utils.git import get_repositories
ui = gui()
default_project_dir = 'var/dev'

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

def get_win():
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
	win = get_win()
	while True:
		event, values = win.read()
		print(event)
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
				name = url.split(f"{user}/")[1].split('.')[0]
				win['-USERNAME-'].update(user)
				win['-NAME-'].update(name)
			except:
				pass
			print("Repository url set:", url)
		elif event == '-NAME-':
			name = values[event]
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

if __name__ == "__main__":
	new_project()	
