from ui.menus import *
from psg_creator.creator import *

def update(pm=None, win=None):
	if win is None and pm is None:
		raise Exception("whoops, window is None!")
	if pm is None:
		pm = get_pm()
	#update repo details section
	pm.win.Element('-PROJECT_DETAILS_TAB-').Select()
	pm.win['-PROJECT_FILES-'].update(pm.files)
	pm.win['-NAME-'].update(pm.name)
	pm.win['-INPUT_PROJECT_PATH-'].update(pm.default_project_dir)
	pm.win['-URL-'].update(pm.url)
	pm.win['-EMAIL-'].update(pm.git.email)
	pm.win['-USERNAME-'].update(pm.git.user)
	pm.win['-TOKEN-'].update(pm.git.token)
	pm.win['-LISTBOX_REPOS-'].update(pm.git.get_repositories())
	#update UI Creator
	if os.path.exists(pm.ui_file):
		pm.preview_data = pm.load_ui_data(pm.ui_file)
	else:
		pm.preview_data = pm.creator.preview_data
	if pm.preview_data != []:
		pm.win['-PREVIEW_IMG-'].update(pm.creator.get_preview_img(pm.preview_data))
	if pm.creator.elements != {}:
		pm.win['-ELEMENTS_LIST-'].update(list(pm.creator.elements.keys()))
	if pm.creator.map.map != []:
		pm.win['-LAYOUT_ROWS-'].update(pm.creator.map.map)
	pm.win['-LAYOUT_ROW_ITEMS-'].update(pm.creator.map.map_row)
	pm.creator.update_preview_img()


def test_for_ui(pm=None):
	datfile = os.path.join(pm.project_path, f"{pm.name}.ui.dat")
	if os.path.exists(datfile):
		pass



def run(debug=True, pm=None):
	if pm is None:
		pm = get_pm()
	#win2 = pm.creator.ui.win_project_master()
	pm.creator.main_window = ui._win_main(win=True)
	pm.win = pm.creator.main_window
	update(pm)
	exit = False
	event = None
	while not exit:
		if exit:
			break
		win, event, values = sg.read_all_windows(timeout=1)
		if event == '__TIMEOUT__':
			pass
		elif event == sg.WIN_CLOSED:
			print("window closed, breaking....")
			break
		else:
			print("Event:", event)
			if event == '-PROJECT_FILES-':
				try:
					selected_files = values[event]
				except:
					selected_files = []
			elif event == '-BTN_EDIT-':
				if selected_files != []:
					pm.editor.editor(files=selected_files)
				else:
					log(f"ui.main.run():Error - No files selected!", 'error')
			elif event == '-BTN_SELECT_ALL-':
				selected_files = select_all(win)
			elif event == '-BTN_CLEAR_ALL-':
				selected_files = clear_all(win)
			elif event == '-BTN_SAVE-':
				save_settings(pm)
				log(f"ui.main.run(): Settings saved! ({pm.settings_file})", 'info')
			elif event == '-BTN_SAVE_AS-':
				pm.settings_file = f"{ui.file_browser(cwd=pm.project_path, browse_type='folder')}/settings.dat"
				pm.settings['settings_file'] = pm.settings_file
				save_settings(pm)
				log(f"ui.main.run(): Settings saved! ({pm.settings_file})", 'info')
			elif event == '-BTN_ADD_FILE-':
				filepath = ui.file_browser(cwd=pm.project_path, browse_type='file')
				add_file(pm=pm, filepath=filepath)
				pm.files.append(filepath)
				update(pm=pm)
			elif event == '-BTN_QUIT-':
				win.close()
				print("breaking: BTN_QUIT clicked...")
				break
			elif event == '-BTN_PUSH-':
				log(f"ui.main.run():Pushing changes to repository ({pm.url})...", 'info')
				pm.git.push()
			elif event == '-BTN_PULL-':
				log(f"ui.main.run():Pulling latest data from repository ({pm.url})...", 'info')
				pm.git.pull()
			elif event == '-BTN_STATUS-':
				#print(pm.git._status())
				files = pm.track_changes()
				print("Added: ", files)
				pm.git.status()
			elif event == '-BTN_MAIN_MENU-':
				win.close()
				pm = get_pm(auto_load=False)
				win = pm.creator.ui.win_project_master()
			elif event == '-BTN_REMOVE_FILE-':
				if selected_files == []:
					selected_files = [ui.file_browser(cwd=pm.project_path, browse_type='file')]
				for filepath in selected_files:
					log(f"ui.main.run(): removing file from local repo..", 'warning')
					try:
						pm.fs.rm(filepath)
					except Exception as e:
						raise Exception(e)
			elif event == '-BTN_UI_CREATOR-':
				pm.creator.main()
			elif event == '-ELEMENTS-':
				try:
					selected = values[event][0]
				except:
					selected = None
				print("Element selected:", selected)
			elif event == '-LAYOUT_ITEMS-' or event == '-LAYOUT_ROW_ITEMS-' or event == '-ELEMENTS_LIST-':
				try:
					selected = values[event][0]
				except:
					selected = None
				print("Element selected:", selected)
			elif event == '-ADD_ELEMENT-' or event == 'Add':
				print("selected:", selected)
				data = pm.creator._win_add_element(selected)
				if data is not None:
					pm.creator.element_data = data
					pm.creator._add_element_data(pm.creator.element_data)
					update(pm=pm)
				pm.creator.update_preview_img()
			elif event == 'Update Preview Image':
				pm.creator.update_preview_img()
			elif event == '-RM_ELEMENT-' or event == 'Remove':
				if selected is not None:
					pm.creator.rm_element(selected)
				pm.creator.update_preview_img()
			elif event == '-PUSH-' or event == 'Push':
				pm.creator.map.push()
				pm.creator.preview_data.append(('push', None))
				update(pm=pm)

			elif event == 'Close':
				pm.creator.ui.save()
				win.close()
				exit = True
				print("Exit set True, breaking...")
			elif event == 'Preview':
				pm.preview_win = pm.creator._preview()
			elif event == 'Save':
				pm.preview_win = pm.creator._preview()
				#ed, md = pm.preview_win.metadata
				data = pm.creator.preview_data
				title = pm.preview_win.Title
				filepath = os.path.join(pm.project_path, f"{pm.name}.dat")
				#filepath = os.path.join(os.path.expanduser("~"), '.gui', f"pm.creator.{title}.dat")
				pm.creator.ui.save(data=data, filepath=filepath)
				print("Saved!")
			elif event == 'Save As..':
				filepath = pm.creator.ui.file_browser(browse_type='save')
				pm.preview_win = pm.creator._preview()
				data = pm.creator.preview_data
				pm.creator.ui.save(data=data, filepath=filepath)
				print("Saved as:", filepath)
				#pm.creator.save_ui(win=pm.preview_win, filepath=filepath)
			elif event == 'Break':
				print("breaking by event...")
				break
			elif event == 'Load':
				path = pm.project_path
				filepath = pm.creator.ui.file_browser(browse_type='file', cwd=path)
				pm.creator.preview_data = pm.creator.load_ui(filepath=filepath, run=False)
				pm.creator.create_elements_dict()
				update(pm)
			elif event == 'Code Editor':
				pm.creator.ui.get_user_code()
			elif event == 'New':
				pm.creator.new()
			elif event == 'Clear':
				print("TODO: Add 'Clear' method!")
			elif event == 'Export':
				print("TODO: Add 'Export' method!")
			elif event == 'Build Menu':
				print("TODO: Add 'Build Menu' method!")
			elif event == 'Settings':
				print("TODO: Add 'Settings' method!")
			elif event == '-BUTTON_NEW_PROJECT-':
				data = new_project()
				name = data['name']
				project_path = data['project_path']
				if project_path is None:
					log("Whoops!")
					pass
				else:
					if not os.path.exists(project_path):
						filesystem().mkdir(project_path)
						os.chdir(project_path)
					default_project_dir = data['default_project_dir']
					url = data['url']
					git.email = data['email']
					git.user = data['user']
					git.token = data['token']
					pm = project_mgr(debug=pm.debug, editor_name='idle', project_path=pm.project_path, default_project_dir=default_project_dir, git_url=url, settings=data)
					pm.creator.main_window = ui._win_main(win=True)
					pm.win = pm.creator.main_window
					update(pm)
			elif event == '-BUTTON_LOAD_PROJECT-':
				pm.project_path = ui.file_browser(browse_type='folder', cwd='/var/dev/')
				pm = project_mgr(debug=pm.debug, editor_name='idle', project_path=pm.project_path)
			elif event == '-BUTTON_SETTINGS-':
				pass
			elif event == '-AUTO_LOAD-':
				pm = load_project()
				log(f"Poject loaded: {pm.name}", 'info')
			elif event == '-DEBUG-':
				pass
			elif event == '-ELEMENTS-':
				try:
					pm.selected = values[event][0]
				except:
					pm.selected = None
				print("Element selected:", pm.selected)
			elif event == '-LAYOUT_ITEMS-' or event == '-LAYOUT_ROW_ITEMS-' or event == '-ELEMENTS_LIST-':
				try:
					pm.selected = values[event][0]
				except:
					pm.selected = None
				print("Element selected:", pm.selected)
			elif event == '-ADD_ELEMENT-' or event == 'Add':
				data = pm.creator._win_add_element(pm.selected)
				if data is not None:
					pm.creator.element_data = data
					pm.creator._add_element_data(pm.creator.element_data)
					update(pm=pm)
				pm.creator.update_preview_img()
			elif event == 'Update Preview Image':
				pm.creator.update_preview_img()
			elif event == '-RM_ELEMENT-' or event == 'Remove':
				if pm.selected is not None:
					pm.creator.rm_element(pm.selected)
				pm.creator.update_preview_img()
			elif event == '-PUSH-' or event == 'Push':
				pm.creator.map.push()
				pm.creator.preview_data.append(('push', None))
				update(pm=pm)
				pm.creator.update_preview_img()
			elif event == 'Close':
				pm.creator.ui.save()
				win.close()
				exit = True
			elif event == 'Preview':
				pm.creator.preview_win = pm.creator._preview()
			elif event == '-PROJECT_PATH-':
				pm.default_project_dir = ui.file_browser(browse_type='folder', cwd='/var/dev')
				print("set project directory:", default_project_dir)
				win['-INPUT_PROJECT_PATH-'].update(default_project_dir)
			elif event == '-INPUT_PROJECT_PATH-':
				pm.default_project_dir = values[event]
			elif event == '-URL-':
				pm.url = values[event]
				try:
					pm.git.user = url.split('com/')[1].split('/')[0]
					pm.name = url.split(f"{user}/")[1].split('.')[0].replace('_', ' ').title()
					win['-USERNAME-'].update(user)
					win['-NAME-'].update(name)
				except:
					pass
				print("Repository url set:", url)
			elif event == '-NAME-':
				pm.name = values[event].replace(' ', '_').lower()
				pm.project_path = os.path.join(default_project_dir, name)
				if pm.git.user is None:
					try:
						pm.git.user = pm.git.email.split('@')[0]
						win['-USERNAME-'].update(pm.git.user)
					except:
						print("Please set username or email first!")
				pm.url = f"https://github.com/{pm.git.user}/{pm.name}.git"
				win['-URL-'].update(url)
				print("Repository name set:", pm.name)
			elif event == '-EMAIL-':
				pm.git.email = values[event]
				if '@' in pm.git.email:
					pm.git.user = pm.git.email.split('@')[0]
					win['-USERNAME-'].update(user)
					pm.url = f"https://github.com/{user}/{name}.git"
					win['-URL-'].update(url)
				if '.com' in pm.git.email:
					pm.git.token = get_token(pm.git.email)
					win['-TOKEN-'].update(token)
			elif event == '-BTN_UPDATE_REPOS-':
				if pm.git.user is None:
					print("Set email or username first!")
				else:
					if pm.url is None and pm.git.user is not None and pm.git.name is not None:
						pm.url = f"https://github.com/{pm.git.user}/{pm.git.name}.git"
					update(pm=pm)
			elif event == '-BTN_LOAD_TOKEN-':
				try:
					pm.git.token = get_token(pm.git.email)
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


if __name__ == "__main__":
	run()
