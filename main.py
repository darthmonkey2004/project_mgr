from ui.menus import *


def run(pm=None):
	if pm is None:
		pm = get_pm()
	win = win_project_master(pm)
	while True:
		event, values = win.read()
		if event == sg.WIN_CLOSED:
			break
		elif event == '-PROJECT_FILES-':
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
			win['-PROJECT_FILES-'].update(pm.files)
		elif event == '-BTN_QUIT-':
			win.close()
			break
		elif event == '-BTN_PUSH-':
			log(f"ui.main.run():Pushing changes to repository ({pm.url})...", 'info')
			pm.git.push()
		elif event == '-BTN_PULL-':
			log(f"ui.main.run():Pulling latest data from repository ({pm.url})...", 'info')
			pm.git.pull()
		elif event == '-BTN_STATUS-':
			print(pm.git._status())
			files = pm.track_changes()
			print("Added: ", files)
			pm.git.status()
		elif event == '-BTN_MAIN_MENU-':
			win.close()
			pm = get_pm(auto_load=False)
			win = win_project_master(pm)
		elif event == '-BTN_REMOVE_FILE-':
			if selected_files == []:
				selected_files = [ui.file_browser(cwd=pm.project_path, browse_type='file')]
			for filepath in selected_files:
				log(f"ui.main.run(): removing file from local repo..", 'warning')
				try:
					pm.fs.rm(filepath)
				except Exception as e:
					raise Exception(e)
				

if __name__ == "__main__":
	run()
