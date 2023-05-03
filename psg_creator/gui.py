from psg_creator.xrandr import *
from helper_utils import filesystem
import os
import pickle
from collections import OrderedDict
import PySimpleGUI as sg
from psg_creator.element_data import *
#from create import *
from psg_creator.xrandr import *
default_project_dir = 'var/dev'

VLC_VIDEO_FILTERS = ['video:adjust', 'video:alphamask', 'video:anaglyph', 'video:antiflicker', 'video:audiobargraph_v', 'video:ball', 'video:blendbench', 'video:bluescreen', 'video:canvas', 'video:chain', 'video:colorthres', 'video:croppadd', 'video:deinterlace', 'video:edgedetection', 'video:erase', 'video:extract', 'video:fps', 'video:freeze', 'video:gaussianblur', 'video:gradfun', 'video:gradient', 'video:grain', 'video:hqdn3d', 'video:invert', 'video:logo', 'video:magnify', 'video:mirror', 'video:motionblur', 'video:motiondetect', 'video:oldmovie', 'video:posterize', 'video:postproc', 'video:psychedelic', 'video:puzzle', 'video:ripple', 'video:rotate', 'video:scene', 'video:sepia', 'video:sharpen', 'video:transform', 'video:vaapi_filters', 'video:vaapi_filters', 'video:vaapi_filters', 'video:vaapi_filters', 'video:vaapi_filters', 'video:vdpau_adjust', 'video:vdpau_deinterlace', 'video:vdpau_sharpen', 'video:vhs', 'video:wave']
VLC_AUDIO_FILTERS = ['audio:audiobargraph_a', 'audio:chorus_flanger', 'audio:compressor', 'audio:equalizer', 'audio:gain', 'audio:headphone', 'audio:karaoke', 'audio:mono', 'audio:normvol', 'audio:param_eq', 'audio:remap', 'audio:scaletempo', 'audio:scaletempo_pitch', 'audio:spatialaudio', 'audio:spatializer', 'audio:stereo_widen']
file_items = ['-&Load Directory-', '-&Load Playlist-', '-&Save Playlist-', 'E&xit', 'Add To &Favorites']
tools_items = ['&Resort Database Ids', '&PBDL Lite UI', '-&Database Editor-', '-ID3 Tag Editor-']
scan_items = ['Scan Movies', 'Scan Series', 'Scan Music', 'Scan All', 'Clean Database']
fs = filesystem.filesystem()

def _unwrap_(l):
	out = []
	for i in l:
		out.append(i)
	return out

def _unwrap(l):
	out = []
	for i in l:
		if type(i) == list:
			i = _unwrap_(i)
			out += i
		else:
			out.append(i)
	return out

def unwrap(l):
	while type(l) == list:
		old = l
		l = _unwrap(l)
		if old == l:
			break
	if len(l) == 1:
		l = l[0]
	return l

def drill(l):
	while type(l) == list:
		l = l[0]
	return l

class menu():
	def __init__(self):
		self.menu_data = {}
		self.menu_parents = []
	def add_to_submenu(self, parent, name, items):
		if parent not in self.menu_parents:
			self.menu_parents.append(parent)
			self.menu_data[parent] = []
		self.menu_data[parent].append(name)
		self.menu_data[parent].append(items)
	def add_to_menu(self, parent, items):
		if parent not in self.menu_parents:
			self.menu_parents.append(parent)
			self.menu_data[parent] = []
		self.menu_data[parent].append(items)
	def get_menu(self):
		l = []
		for key in self.menu_data.keys():
			l.append([key, self.menu_data[key]])
		return l

class layout_object():
	def __init__(self):
		self.rows = []
		self.row = []
		self.map = []
		self.map_row = []
		self.layout = []
	def add(self, obj):
		if obj.key is None:
			raise Exception("key for object is None!")
		isframe = 'Frame' in str(obj)
		iscolumn = 'Column' in str(obj)
		istab = 'Tab' in str(obj)
		istg = 'TabGroup' in str(obj)
		self.row.append(obj)
		if iscolumn:
			#print("column", str(obj))
			rows = unwrap(obj.Rows)
			if type(rows) == list:
				for row in rows:
					if type(row) == list:
						l = []
						l2 = []
						for i in unwrap(row):
							l.append(i.key)
							l2.append(i)
						self.map_row.append([obj.key, l])
					else:
						self.map_row.append([obj.key, row.key])
			else:
				self.map_row.append(obj.key)
		if isframe:
			#print("frame", str(obj))
			rows = unwrap(obj.Rows)
			if type(rows) == list:
				for row in rows:
					l = []
					l2 = []
					for i in unwrap(row):
						l.append(i.key)
						l2.append(i)
					self.map_row.append([obj.key, l])
			else:
				self.map_row.append(obj.key)
		elif istg:
			#print("tabgroup", str(obj))
			for tab in unwrap(obj.Rows):
				l = []
				l2 = []
				for i in unwrap(tab.Rows):
					l.append(i.key)
					l2.append(i)
				self.map_row.append([obj.key, l])
		else:
			self.map_row.append(obj.key)

	def push(self):
		if self.map_row not in self.map and len(self.row) > 0:
			self.rows.append(self.row)
			self.map.append(self.map_row)
			self.map_row = []
			self.row = []
		elif self.map_row in self.map:
			txt = f"Error - row already in map!!"
			#print(txt)
		elif len(self.row) == 0:
			pass
	def get(self):
		if len(self.row) > 0:
			self.push()
		return self.rows
	def get_map(self):
		if len(self.map_row) > 0:
			self.push()
		return self.map
	def clear(self):
		self.rows = []
		self.row = []
		self.map = []
		self.map_row = []

class gui():
	def __init__(self, menu_def=None, container_type="frame"):
		self.preview_img = os.path.join(os.path.expanduser("~"), '.gui', 'preview.png')
		self.menu_obj = menu()
		self.defaults = elements_defaults
		path = os.path.join(os.path.expanduser("~"), '.gui')
		if not os.path.exists(path):
			fs.mkdir(path)
		self.location = self.init_location()
		sg.set_options(window_location=self.location)
		self.layout_obj = layout_object()
		self.type = container_type
		if self.type != "frame" and self.type != "column" and self.type != "tabs":
			txt = f"Error - bad container type ({self.type})! Valid options: 'frame', 'column', 'tab'"
			raise Exception(txt)
		self .container = None
		self.container_data = {}
		self._init_win_defaults()
		self.menu_def = menu_def
		self.menu_data = {}
		self.menu_parents = []
		self.tabs = []
		self.element_data = {}
		self.child_windows = {}
		filename = os.path.join(os.path.expanduser("~"), '.gui', 'gui.settings')
		self.settings = sg.UserSettings(filename=filename)
		self.restart = False
		self.options = {'icon': None, 'button_color': None, 'element_size': (None, None), 'button_element_size': (None, None), 'margins': (None, None), 'element_padding': (None, None), 'auto_size_text': None, 'auto_size_buttons': None, 'font': None, 'border_width': None, 'slider_border_width': None, 'slider_relief': None, 'text_justification': None, 'background_color': None, 'element_background_color': None, 'text_element_background_color': None, 'input_elements_background_color': None, 'input_text_color': None, 'scrollbar_color': None, 'text_color': None, 'element_text_color': None, 'debug_win_size': (None, None), 'window_location': (None, None), 'error_button_color': (None, None), 'tooltip_time': None, 'tooltip_font': None, 'use_ttk_buttons': None, 'ttk_theme': None, 'suppress_error_popups': None, 'suppress_raise_key_errors': None, 'suppress_key_guessing': None, 'warn_button_key_duplicates': False, 'enable_treeview_869_patch': None, 'enable_mac_notitlebar_patch': None, 'use_custom_titlebar': None, 'titlebar_background_color': None, 'titlebar_text_color': None, 'titlebar_font': None, 'titlebar_icon': None, 'user_settings_path': None, 'pysimplegui_settings_path': None, 'pysimplegui_settings_filename': None, 'keep_on_top': None, 'dpi_awareness': None, 'scaling': None, 'disable_modal_windows': None, 'force_modal_windows': None, 'tooltip_offset': (None, None)}
		

	def build_layout(self, map_data=None, element_data=None):
		if map_data is not None:
			self.map_data = map_data
		if element_data is not None:
			self.element_data = element_data
		for row in map_data:
			for key in row:
				data = element_data[key]
				#print(key, data)
				element = data['element_type']
				self.layout_obj.add(self._element(element, data=data))
			self.layout_obj.push()
		self.window = self.generate()
		return self.window

	def init_location(self):
		screens = get_connected()
		if len(screens) > 1:
			screen = 1
		else:
			screen = 0
		location = screens[screen]['pos_x'], screens[screen]['pos_y']
		return location
		
	
	def store_location(self, location=None):
		if location is None:
			location = self.locationo
		self.settings.set('location', location)
		self.settings.save()

	def load_settings(self, filename=None):
		if filename is None:
			filename = os.path.join(os.path.expanduser("~"), '.gui', 'gui.settings')
		if os.path.exists(filename):
			settings = sg.UserSettings(filename=filename, autosave=True)
		else:
			settings = self.init_settings(filename=filename)
		return settings

	def init_settings(self, filename=None):
		if filename is None:
			filename = os.path.join(os.path.expanduser("~"), '.gui', 'gui.settings')
		#print(filename)
		settings = sg.UserSettings(filename=filename, autosave=True)
		screens = get_connected()
		settings.set('screens', screens)
		if len(screens) > 1:
			settings.set('screen', 1)
		else:
			settings.set('screen', 0)
		settings.set('title', 'UI Creator')
		settings.save()
		return set

	def save(self, win=None, data=None, filepath=None):
		if data is None:
			element_data = self.element_data
			map_data = self.layout_obj.map
			data = element_data, map_data
		if filepath is None:
			filepath = os.path.join(os.path.expanduser("~"), '.gui', "creator.default.dat")
		with open(filepath , 'wb') as f:
			pickle.dump(data, f)
			f.close()

	def set_element_default(self, element, key, val):
		try:
			self.defaults[element][key] = val
			string = f"self.defaults = {self.defaults}"
			with open('element_data.py', 'w') as f:
				f.write(string)
				f.close()
		except Exception as e:
			print(e)

	def list_saved(self, path=None):
		if path is None:
			path = os.path.join(os.path.expanduser("~"), '.gui')
		return fs.ls(path)

	def load(self, filepath=None):
		if filepath is None:
			files = self.list_saved()
			if len(files) == 0:
				filepath = os.path.join(os.path.expanduser("~"), '.gui', "creator.default.dat")
			else:
				filepath = files[0]
		with open(filepath, 'rb') as f:
			data = pickle.load(f)
			f.close()
		return data

	def add_to_submenu(self, parent, name, items):
		if parent not in self.menu_parents:
			self.menu_parents.append(parent)
			self.menu_data[parent] = []
		self.menu_data[parent].append(name)
		self.menu_data[parent].append(items)

	def add_to_menu(self, parent, items):
		if parent not in self.menu_parents:
			self.menu_parents.append(parent)
			self.menu_data[parent] = []
		self.menu_data[parent].append(items)

	def build_menu(self):
		# DELETE ME????
		l = []
		for key in self.menu_data.keys():
			l.append([key, self.menu_data[key]])
		return l

	def menu(self):
		parent = 'File'
		items = ['Save', 'Save As..', 'Load', 'New', 'Clear', 'Preview', 'Export']
		self.menu_obj.add_to_menu(parent=parent, items=items)
		parent = 'Layout'
		items = ['Clear', 'Add', 'Push', 'Del']
		self.menu_obj.add_to_menu(parent=parent, items=items)
		parent = 'Menu'
		items = ['Editor', 'Build Menu', 'Clear']
		self.menu_obj.add_to_menu(parent=parent, items=items)
		parent = 'Edit'
		items = ['Settings']
		self.menu_obj.add_to_menu(parent=parent, items=items)
		parent = 'Help'
		items = ['About', 'Version', 'Contact Us']
		self.menu_obj.add_to_menu(parent=parent, items=items)
		self.menu_def = self.menu_obj.get_menu()
		return self._element('MenubarCustom', menu_definition=self.menu_def, tearoff=True, key='-menubar_key-')


	def _init_win_defaults(self):
		self.title='NPlayer Main'
		self.default_element_size=None
		self.default_button_element_size=(None, None)
		self.auto_size_text=None
		self.auto_size_buttons=None
		self.location=(None, None)
		self.relative_location=(None, None)
		self.size=(None, None)
		self.element_padding=None
		self.margins=(None, None)
		self.button_color=None
		self.font=None
		self.progress_bar_color=(None, None)
		self.background_color=None
		self.border_depth=None
		self.auto_close=False
		self.auto_close_duration=3
		self.icon=None
		self.force_toplevel=False
		self.alpha_channel=None
		self.return_keyboard_events=False
		self.use_default_focus=True
		self.text_justification=None
		self.no_titlebar=False
		self.grab_anywhere=False
		self.grab_anywhere_using_control=True
		self.keep_on_top=None
		self.resizable=True
		self.disable_close=False
		self.disable_minimize=False
		self.right_click_menu=None
		self.transparent_color=None
		self.debugger_enabled=True
		self.right_click_menu_background_color=None
		self.right_click_menu_text_color=None
		self.right_click_menu_disabled_text_color=None
		self.right_click_menu_selected_colors=(None, None)
		self.right_click_menu_font=None
		self.right_click_menu_tearoff=False
		self.finalize=False
		self.element_justification="left"
		self.ttk_theme=None
		self.use_ttk_buttons=None
		self.modal=False
		self.enable_close_attempted_event=False
		self.titlebar_background_color=None
		self.titlebar_text_color=None
		self.titlebar_font=None
		self.titlebar_icon=None
		self.use_custom_titlebar=None
		self.scaling=None
		self.sbar_background_color=None
		self.sbar_arrow_color=None
		self.sbar_width=None
		self.sbar_arrow_width=None
		self.sbar_frame_color=None
		self.sbar_relief=None
		self.metadata=None

	def _win_main(self, win=False):
		self.layout_obj = layout_object()
		l = [[self._element('Image', source=self.preview_img, key='-PREVIEW_IMG-', expand_x=True, expand_y=True)]]
		self.layout_obj.add(self._element('Frame', layout=l, key='-PREVIEW_IMG_FRAME-', expand_x=True, expand_y=True))
		self.layout_obj.push()
		l1 = [[self._element('Listbox', values=list(elements_defaults.keys()), size=(30, 30), key='-ELEMENTS-', expand_x=False, expand_y=True)]]
		self.layout_obj.add(self._element('Frame', layout=l1, key='-LIST_FRAME-'))
		l2 = [[self._element('Listbox', values=[], size=(30, 10), key='-ELEMENTS_LIST-', expand_x=False, expand_y=False)],
			[self._element('Listbox', values=[], size=(30, 10), key='-LAYOUT_ROWS-', expand_x=False, expand_y=False)],
			[self._element('Listbox', values=[], size=(30, 10), key='-LAYOUT_ROW_ITEMS-', expand_x=False, expand_y=False)]]
		self.layout_obj.add(self._element('Column', layout=l2, scrollable=True, expand_x=True, expand_y=True, key='-ELEMENT_ADD_COLUMN-'))
		self.layout_obj.push()
		self.layout_obj.add(self._element('Button', button_text='Add Element', key='-ADD_ELEMENT-'))
		self.layout_obj.add(self._element('Button', button_text='Push Row', key='-PUSH-'))
		self.layout_obj.add(self._element('Button', button_text='Remove Element', key='-RM_ELEMENT-'))
		self.layout_obj.push()
		self.layout_obj.layout = self.layout_obj.rows
		if win:
			self.main_window = self.pack()
			self.layout_obj.row = []
			return self.main_window
		else:
			return self.layout_obj


	def win_project_master(self, win=False):
		layout_obj = layout_object()
		layout_obj.add(self._element('Listbox', expand_y=True, expand_x=True, select_mode='multiple', values=[], key='-PROJECT_FILES-'))
		layout_obj.push()
		layout_obj.add(self._element('Button', button_text='Push', key='-BTN_PUSH-'))
		layout_obj.add(self._element('Button', button_text='Pull', key='-BTN_PULL-'))
		layout_obj.add(self._element('Button', button_text='Status', key='-BTN_STATUS-'))
		layout_obj.add(self._element('Button', button_text='Open in Editor', key='-BTN_EDIT-'))
		layout_obj.add(self._element('Button', button_text='Select All', key='-BTN_SELECT_ALL-'))
		layout_obj.add(self._element('Button', button_text='Clear All', key='-BTN_CLEAR_ALL-'))
		layout_obj.push()
		layout_obj.add(self._element('Button', button_text='Save', key='-BTN_SAVE-'))
		layout_obj.add(self._element('Button', button_text='Save As...', key='-BTN_SAVE_AS-'))
		layout_obj.add(self._element('Button', button_text='Add File...', key='-BTN_ADD_FILE-'))
		layout_obj.add(self._element('Button', button_text='Remove file...', key='-BTN_REMOVE_FILE-'))
		layout_obj.add(self._element('Button', button_text='Quit!', key='-BTN_QUIT-'))
		layout_obj.add(self._element('Button', button_text='Main Menu', key='-BTN_MAIN_MENU-'))
		layout_obj.push()
		if not win:
			return layout_obj
		else:
			return self.child_window(layout_obj=layout_obj, title='Add Menu Item', run=False)



	def pack(self, title='Main', finalize=True):
		layout1 = self.win_main_menu().get()
		layout2 = self.win_project_master().get()
		layout3 = self.win_new_project().get()
		layout4 = self._win_main().get()
		uictls = []
		uictls.append([self.menu(),
			self._element('Button', button_text='Hide UI', key='-Hide UI'),
			self._element('Button', button_text="Close", key='-Close-'),
			self._element(element='Button', button_text='store window location', key='-store window location-'),
			self._element(element='Button', button_text='Recenter UI', key='-Recenter UI-')])
		uictl_frame = ([self._element('Frame', title='UI Controls', layout=uictls)])
		tab = self._element('Tab', title='Project Manager: Main Menu', layout=layout1, key='-MAIN_MENU_TAB-', expand_x=True, expand_y=True)
		tab2 = self._element('Tab', title=f"Project Details", layout=layout2, key='-PROJECT_DETAILS_TAB-', expand_x=True, expand_y=True)
		tab3 = self._element('Tab', title='Repo Setup', layout=layout3, key='-REPO_SETUP_TAB-', expand_x=True, expand_y=True)
		tab4 = self._element('Tab', title='UI Creator', layout=layout4, key='-UI_CREATOR_TAB-', expand_x=True, expand_y=True)
		tab_grp = self._element('TabGroup', layout=[[tab], [tab2], [tab3], [tab4]], expand_x=True, expand_y=True, key='-UI_TABGROUP-')
		tab_frame = self._element('Frame', title=None, layout=[[tab_grp]], expand_x=True, expand_y=True)
		newlayout = []
		newlayout.append([uictl_frame])
		newlayout.append([tab_frame])
		metadata = self.element_data, self.layout_obj.map
		#print(newlayout, title, finalize, metadata)
		self.window = self._window(layout=newlayout, title=title, finalize=finalize, metadata=metadata)
		self.size = self.window.size
		self.location = self.window.current_location()
		self.element_data['size'] = self.size
		self.element_data['location'] = self.location
		self.layout_obj.rows = []
		#self.save(win=self.window)
		return self.window

	def win_main_menu(self, win=False):
		layout_obj = layout_object()
		layout_obj.add(self._element('Button', button_text='New Project', expand_x=True, expand_y=True, key='-BUTTON_NEW_PROJECT-'))
		layout_obj.push()
		layout_obj.add(self._element('Button', button_text='Load Project...', expand_x=True, expand_y=True, key='-BUTTON_LOAD_PROJECT-'))
		layout_obj.push()
		layout_obj.add(self._element('Button', button_text='Settings', expand_x=True, expand_y=True, key='-BUTTON_SETTINGS-'))
		layout_obj.push()
		layout_obj.add(self._element('Checkbox', text='Auto-Load Last Project', key='-AUTO_LOAD-'))
		layout_obj.add(self._element('Checkbox', text='Debug Mode (Verbose)', key='-DEBUG-'))
		layout_obj.push()
		if not win:
			return layout_obj
		else:
			return self.child_window(layout_obj=layout_obj, title='Add Menu Item', run=False)

	def win_new_project(self, win=False):
		layout_obj = layout_object()
		layout_obj.add(self._element('Listbox', values=[], expand_x=True, expand_y=True, key='-LISTBOX_REPOS-'))
		layout_obj.push()
		layout_obj.add(self._element('Button', button_text='Update Repos', key='-BTN_UPDATE_REPOS-'))
		layout_obj.push()
		layout_obj.add(self._element('Text', text='Project Name:', key='-TEXT_NAME-'))
		layout_obj.add(self._element('Input', default_text=None, key='-NAME-'))
		layout_obj.add(self._element('Button', button_text='New Repository...', key='-NEW_REPO-'))
		layout_obj.push()
		layout_obj.add(self._element('Text', text='Local Project Directory:', key='-PROJECT_PATH_TEXT-'))
		layout_obj.add(self._element('Input', default_text=default_project_dir, key='-INPUT_PROJECT_PATH-'))
		layout_obj.add(self._element('Button', button_text='Select project location...', key='-PROJECT_PATH-'))
		layout_obj.push()
		layout_obj.add(self._element('Text', text='Git URL:', key='-TEXT_URL-'))
		layout_obj.add(self._element('Input', key='-URL-'))
		layout_obj.push()
		layout_obj.add(self._element('Text', text='Email:', key='-TEXT_EMAIL-'))
		layout_obj.add(self._element('Input', key='-EMAIL-'))
		layout_obj.add(self._element('Button', button_text='Load Token', key='-BTN_LOAD_TOKEN-'))
		layout_obj.add(self._element('Button', button_text='Store Token', key='-BTN_STORE_TOKEN-'))
		layout_obj.push()
		layout_obj.add(self._element('Text', text='Git Username:', key='-TEXT_USERNAME-'))
		layout_obj.add(self._element('Input', key='-USERNAME-'))
		layout_obj.push()
		layout_obj.add(self._element('Text', text='Token:', key='-TEXT_TOKEN-'))
		layout_obj.add(self._element('Input', key='-TOKEN-'))
		layout_obj.push()
		layout_obj.add(self._element('Button', button_text='Ok', key='-OK-'))
		layout_obj.add(self._element('Button', button_text='Cancel', key='-CANCEL-'))
		layout_obj.add(self._element('Button', button_text='Break', key='-BREAK-'))
		layout_obj.push()
		if not win:
			return layout_obj
		else:
			return self.child_window(layout_obj=layout_obj, title='Add Menu Item', run=False)

	def generate(self, **args):
		for key in args.keys():
			self.__dict__[key] = args[key]
		layout = self.layout_obj.rows
		if self.type == 'Frame':
			self.container = self._element('Frame', title=None, layout=layout, expand_x=True, expand_y=True)
			return self._window(layout=[self.container], data=args) 
		elif self.type == 'tab':
			self.container = self._get_tabs()
			return self._window(layout=[self.container], data=args) 
		elif self.type == 'column':
			self.container = self._element('Column', layout=layout, scrollable=True, vertical_scroll_only=True, justification="top", element_justification="top", vertical_alignment="top", expand_x=True, expand_y=False)
			return self._window(layout=[self.container], data=args) 
		else:
			#skip container, pack in window if self.type is None
			self.container = None
			return self._window(layout=layout, data=args) 
       
	def add_tab(self, title, layout=None):
		if layout is None:
			self.layout_obj.rows = layout
		key = f"-{title.upper()}-"
		self.tabs.append(self._element('Tab', title=title, layout=self.layout_obj.rows, key=key, expand_x=True, expand_y=True))
		self.layout_obj.rows = []
	def _get_tab_container(self, tabs=None):
		if tabs is None:
			tabs = self.tabs
		tab_grp = self._element('TabGroup', layout=tabs, expand_x=True, expand_y=True, key='-UI_TABGROUP-')
		return self._element('Frame', title=None, layout=[[tab_grp]], expand_x=True, expand_y=True)
		
		

	def child_window(self, layout_obj=None, title=None, run=True, location=(None, None), size=(None, None), finalize=True):
		if layout_obj is None:
			#layout_obj = self.layout_obj
			raise Exception("No layout object provided to child window!")
		if title is None:
			txt = "Error - title is None"
			raise Exception(txt)
		frame = self._element('Frame', title=title, layout=layout_obj.rows, expand_x=True, expand_y=True)
		self.child_windows[title] = self._window(layout=[[frame]], title=title, finalize=True, size=size, location=location)
		#layout_obj.clear()
		if run:
			_ = self.child_windows[title].read()
		return self.child_windows[title]

	def _window(self, layout=None, data=None, **args):
		if data is not None:
			args = data
		#print(f"metadata={self.metadata}")
		if layout is None:
			layout = self.layout_obj.rows
		for key in args.keys():
			val = args[key]
			self.__dict__[key] = val
		return sg.Window(title=self.title, layout=layout, default_element_size=self.default_element_size, default_button_element_size=self.default_button_element_size, auto_size_text=self.auto_size_text, auto_size_buttons=self.auto_size_buttons, location=self.location, relative_location=self.relative_location, size=self.size, element_padding=self.element_padding, margins=self.margins, button_color=self.button_color, font=self.font, progress_bar_color=self.progress_bar_color, background_color=self.background_color, border_depth=self.border_depth, auto_close=self.auto_close, auto_close_duration=self.auto_close_duration, icon=self.icon, force_toplevel=self.force_toplevel, alpha_channel=self.alpha_channel, return_keyboard_events=self.return_keyboard_events, use_default_focus=self.use_default_focus, text_justification=self.text_justification, no_titlebar=self.no_titlebar, grab_anywhere=self.grab_anywhere, grab_anywhere_using_control=self.grab_anywhere_using_control, keep_on_top=self.keep_on_top, resizable=self.resizable, disable_close=self.disable_close, disable_minimize=self.disable_minimize, right_click_menu=self.right_click_menu, transparent_color=self.transparent_color, debugger_enabled=self.debugger_enabled, right_click_menu_background_color=self.right_click_menu_background_color, right_click_menu_text_color=self.right_click_menu_text_color, right_click_menu_disabled_text_color=self.right_click_menu_disabled_text_color, right_click_menu_selected_colors=self.right_click_menu_selected_colors, right_click_menu_font=self.right_click_menu_font, right_click_menu_tearoff=self.right_click_menu_tearoff, finalize=self.finalize, element_justification=self.element_justification, ttk_theme=self.ttk_theme, use_ttk_buttons=self.use_ttk_buttons, modal=self.modal, enable_close_attempted_event=self.enable_close_attempted_event, titlebar_background_color=self.titlebar_background_color, titlebar_text_color=self.titlebar_text_color, titlebar_font=self.titlebar_font, titlebar_icon=self.titlebar_icon, use_custom_titlebar=self.use_custom_titlebar, scaling=self.scaling, metadata=self.metadata)

	def file_browser(self, browse_type='save', cwd=None):
		types = ['save', 'folder', 'file', 'files']
		if browse_type not in types:
			txt = f"Error - Unknown browse type: {browse_type}!"
			raise Exception(txt)
		if cwd == None:
			cwd = os.getcwd()
		path = None
		if browse_type == 'folder':
			browser_layout = [[sg.T("")], [sg.Text("Choose directory: "), sg.Input(cwd, key='-path-', enable_events=True), sg.FolderBrowse(initial_folder=cwd, key="-SAVE_PATH-")], [sg.Button("Submit")]]
		elif browse_type == 'save':
			browser_layout = [[sg.T("")], [sg.Text("Save as: "), sg.Input(cwd, key='-path-', enable_events=True), sg.FileSaveAs(initial_folder=cwd, key="-SAVE_PATH-")], [sg.Button("Submit")]]
		elif browse_type == 'file':
			browser_layout = [[sg.T("")], [sg.Text("Select file: "), sg.Input(cwd, key='-path-', enable_events=True), sg.FileBrowse(initial_folder=cwd, key="-SAVE_PATH-")], [sg.Button("Submit")]]
		elif browse_type == 'files':
			browser_layout = [[sg.T("")], [sg.Text("Choose directory: "), sg.Input(cwd, key='-path-', enable_events=True), sg.FilesBrowse(initial_folder=cwd, key="-SAVE_PATH-")], [sg.Button("Submit")]]
		win = sg.Window(f"Pick {browse_type.title()} path...", browser_layout)
		while True:
			event, values = win.read(timeout=1)
			if event == '__TIMEOUT__':
				pass
			if event == sg.WIN_CLOSED or event=="Exit":
				path = None
				return None
			elif event == "Submit":
				try:
					path = values["-SAVE_PATH-"]
					win.close()
					if path == '':
						path = cwd
					break
				except:
					path = values['-path-']
					win.close()
					if path == '':
						path = cwd
					break
		if ';' in path:
			path = path.split(';')
		return path

	def _element(self, element, data={}, **args):
		if data != {}:
			args = data
		d = {}
		defaults = self.defaults[element]
		for k in defaults.keys():
			val = defaults[k]
			d[k] = val
			globals()[k] = val
		for k in args.keys():
			d[k] = args[k]
			globals()[k] = args[k]
		d['element_type'] = element
		if element != 'Tab' and element != 'Frame' and element != 'TabGroup' and element != 'Column':	
			self.element_data[key] = d
		else:
			d['layout'] = []
			self.element_data[key] = d
		if element == 'Button':
			return sg.Button(button_text=button_text, button_type=button_type, target=target, tooltip=tooltip, file_types=file_types, initial_folder=initial_folder, default_extension=default_extension, disabled=disabled, change_submits=change_submits, enable_events=enable_events, image_filename=image_filename, image_data=image_data, image_size=image_size, image_subsample=image_subsample, image_source=image_source, border_width=border_width, size=size, auto_size_button=auto_size_button, button_color=button_color, disabled_button_color=disabled_button_color, highlight_colors=highlight_colors, mouseover_colors=mouseover_colors, use_ttk_buttons=use_ttk_buttons, font=font, bind_return_key=bind_return_key, focus=focus, pad=pad, key=key, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'ButtonMenu':
			return sg.ButtonMenu(button_text=button_text, menu_def=menu_def, tooltip=tooltip, disabled=disabled, image_source=image_source, image_filename=image_filename, image_data=image_data, image_size=image_size, image_subsample=image_subsample, border_width=border_width, size=size, auto_size_button=auto_size_button, button_color=button_color, text_color=text_color, background_color=background_color, disabled_text_color=disabled_text_color, font=font, item_font=item_font, pad=pad, expand_x=expand_x, expand_y=expand_y, key=key, tearoff=tearoff, visible=visible, metadata=metadata)
		elif element == 'Canvas':
			return sg.Canvas(canvas=canvas, background_color=background_color, size=size, pad=pad, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, border_width=border_width, metadata=metadata)
		elif element == 'Checkbox':
			return sg.Checkbox(text=text, default=default, size=size, auto_size_text=auto_size_text, font=font, background_color=background_color, text_color=text_color, checkbox_color=checkbox_color, change_submits=change_submits, enable_events=enable_events, disabled=disabled, key=key, pad=pad, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'Column':
			return sg.Column(layout=layout, background_color=background_color, size=size, pad=pad, scrollable=scrollable, vertical_scroll_only=vertical_scroll_only, right_click_menu=right_click_menu, key=key, visible=visible, justification=justification, element_justification=element_justification, vertical_alignment=vertical_alignment, grab=grab, expand_x=expand_x, expand_y=expand_y, metadata=metadata)
		elif element == 'Combo':
			return sg.Combo(values=values, default_value=default_value, size=size, auto_size_text=auto_size_text, background_color=background_color, text_color=text_color, button_background_color=button_background_color, button_arrow_color=button_arrow_color, bind_return_key=bind_return_key, change_submits=change_submits, enable_events=enable_events, disabled=disabled, key=key, pad=pad, expand_x=expand_x, expand_y=expand_y, tooltip=tooltip, readonly=readonly, font=font, visible=visible, metadata=metadata)
		elif element == 'Frame':
			return sg.Frame(title=title, layout=layout, title_color=title_color, background_color=background_color, title_location=title_location, relief=relief, size=size, font=font, pad=pad, border_width=border_width, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, grab=grab, visible=visible, element_justification=element_justification, vertical_alignment=vertical_alignment, metadata=metadata)
		elif element == 'Graph':
			return sg.Graph(canvas_size=canvas_size, graph_bottom_left=graph_bottom_left, graph_top_right=graph_top_right, background_color=background_color, pad=pad, change_submits=change_submits, drag_submits=drag_submits, enable_events=enable_events, motion_events=motion_events, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, float_values=float_values, border_width=border_width, metadata=metadata)
		elif element == 'HorizontalSeparator':
			return sg.HorizontalSeparator(color=color, pad=pad, key=key)
		elif element == 'Image':
			return sg.Image(source=source, filename=filename, data=data, background_color=background_color, size=size, pad=pad, key=key, tooltip=tooltip, subsample=subsample, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, enable_events=enable_events, metadata=metadata)
		elif element == 'Input':
			return sg.Input(default_text=default_text, size=size, disabled=disabled, password_char=password_char, justification=justification, background_color=background_color, text_color=text_color, font=font, tooltip=tooltip, border_width=border_width, change_submits=change_submits, enable_events=enable_events, do_not_clear=do_not_clear, key=key, focus=focus, pad=pad, use_readonly_for_disable=use_readonly_for_disable, readonly=readonly, disabled_readonly_background_color=disabled_readonly_background_color, disabled_readonly_text_color=disabled_readonly_text_color, expand_x=expand_x, expand_y=expand_y, right_click_menu=right_click_menu, visible=visible, metadata=metadata)
		elif element == 'Listbox':
			return sg.Listbox(values=values, default_values=default_values, select_mode=select_mode, change_submits=change_submits, enable_events=enable_events, bind_return_key=bind_return_key, size=size, disabled=disabled, auto_size_text=auto_size_text, font=font, no_scrollbar=no_scrollbar, horizontal_scroll=horizontal_scroll, background_color=background_color, text_color=text_color, highlight_background_color=highlight_background_color, highlight_text_color=highlight_text_color, key=key, pad=pad, tooltip=tooltip, expand_x=expand_x, expand_y=expand_y, right_click_menu=right_click_menu, visible=visible, metadata=metadata)
		elif element == 'Menu':
			return sg.Menu(menu_definition=menu_definition, background_color=background_color, text_color=text_color, disabled_text_color=disabled_text_color, size=size, tearoff=tearoff, font=font, pad=pad, key=key, visible=visible, metadata=metadata)
		elif element == 'MenubarCustom':
			return sg.MenubarCustom(menu_definition=menu_definition, disabled_text_color=disabled_text_color, bar_font=bar_font, font=font, tearoff=tearoff, pad=pad, background_color=background_color, text_color=text_color, bar_background_color=bar_background_color, bar_text_color=bar_text_color, key=key)
		elif element == 'Multiline':
			return sg.Multiline(default_text=default_text, enter_submits=enter_submits, disabled=disabled, autoscroll=autoscroll, border_width=border_width, size=size, auto_size_text=auto_size_text, background_color=background_color, text_color=text_color, horizontal_scroll=horizontal_scroll, change_submits=change_submits, enable_events=enable_events, do_not_clear=do_not_clear, key=key, write_only=write_only, auto_refresh=auto_refresh, reroute_stdout=reroute_stdout, reroute_stderr=reroute_stderr, reroute_cprint=reroute_cprint, echo_stdout_stderr=echo_stdout_stderr, focus=focus, font=font, pad=pad, tooltip=tooltip, justification=justification, no_scrollbar=no_scrollbar, expand_x=expand_x, expand_y=expand_y, rstrip=rstrip, right_click_menu=right_click_menu, visible=visible, metadata=metadata)
		elif element == 'OptionMenu':
			return sg.OptionMenu(values=values, default_value=default_value, size=size, disabled=disabled, auto_size_text=auto_size_text, expand_x=expand_x, expand_y=expand_y, background_color=background_color, text_color=text_color, key=key, pad=pad, tooltip=tooltip, visible=visible, metadata=metadata)
		elif element == 'Output':
			return sg.Output(size=size, background_color=background_color, text_color=text_color, pad=pad, echo_stdout_stderr=echo_stdout_stderr, font=font, tooltip=tooltip, key=key, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'Pane':
			return sg.Pane(pane_list=pane_list, background_color=background_color, size=size, pad=pad, orientation=orientation, show_handle=show_handle, relief=relief, handle_size=handle_size, border_width=border_width, key=key, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'ProgressBar':
			return sg.ProgressBar(max_value=max_value, orientation=orientation, size=size, size_px=size_px, auto_size_text=auto_size_text, bar_color=bar_color, style=style, border_width=border_width, relief=relief, key=key, pad=pad, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'Radio':
			return sg.Radio(text=text, group_id=group_id, default=default, disabled=disabled, size=size, auto_size_text=auto_size_text, background_color=background_color, text_color=text_color, circle_color=circle_color, font=font, key=key, pad=pad, tooltip=tooltip, change_submits=change_submits, enable_events=enable_events, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'Sizer':
			return sg.Sizer(h_pixels=h_pixels, v_pixels=v_pixels)
		elif element == 'Sizegrip':
			return sg.Sizegrip(background_color=background_color, pad=pad, key=key)
		elif element == 'Slider':
			return sg.Slider(range=range, default_value=default_value, resolution=resolution, tick_interval=tick_interval, orientation=orientation, disable_number_display=disable_number_display, border_width=border_width, relief=relief, change_submits=change_submits, enable_events=enable_events, disabled=disabled, size=size, font=font, background_color=background_color, text_color=text_color, trough_color=trough_color, key=key, pad=pad, expand_x=expand_x, expand_y=expand_y, tooltip=tooltip, visible=visible, metadata=metadata)
		elif element == 'Spin':
			return sg.Spin(values=values, initial_value=initial_value, disabled=disabled, change_submits=change_submits, enable_events=enable_events, readonly=readonly, size=size, auto_size_text=auto_size_text, bind_return_key=bind_return_key, font=font, background_color=background_color, text_color=text_color, key=key, pad=pad, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'StatusBar':
			return sg.StatusBar(text=text, size=size, auto_size_text=auto_size_text, click_submits=click_submits, enable_events=enable_events, relief=relief, font=font, text_color=text_color, background_color=background_color, justification=justification, pad=pad, key=key, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, tooltip=tooltip, visible=visible, metadata=metadata)
		elif element == 'Tab':
			return sg.Tab(title=title, layout=layout, title_color=title_color, background_color=background_color, font=font, pad=pad, disabled=disabled, border_width=border_width, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, element_justification=element_justification, image_source=image_source, image_subsample=image_subsample, metadata=metadata)
		elif element == 'TabGroup':
			return sg.TabGroup(layout=layout, tab_location=tab_location, title_color=title_color, tab_background_color=tab_background_color, selected_title_color=selected_title_color, selected_background_color=selected_background_color, background_color=background_color, focus_color=focus_color, font=font, change_submits=change_submits, enable_events=enable_events, pad=pad, border_width=border_width, tab_border_width=tab_border_width, theme=theme, key=key, size=size, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'Table':
			return sg.Table(values=values, headings=headings, visible_column_map=visible_column_map, col_widths=col_widths, def_col_width=def_col_width, auto_size_columns=auto_size_columns, max_col_width=max_col_width, select_mode=select_mode, display_row_numbers=display_row_numbers, num_rows=num_rows, row_height=row_height, font=font, justification=justification, text_color=text_color, background_color=background_color, alternating_row_color=alternating_row_color, selected_row_colors=selected_row_colors, header_text_color=header_text_color, header_background_color=header_background_color, header_font=header_font, header_border_width=header_border_width, header_relief=header_relief, row_colors=row_colors, vertical_scroll_only=vertical_scroll_only, hide_vertical_scroll=hide_vertical_scroll, border_width=border_width, size=size, change_submits=change_submits, enable_events=enable_events, enable_click_events=enable_click_events, right_click_selects=right_click_selects, bind_return_key=bind_return_key, pad=pad, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'Text':
			return sg.Text(text=text, size=size, auto_size_text=auto_size_text, click_submits=click_submits, enable_events=enable_events, relief=relief, font=font, text_color=text_color, background_color=background_color, border_width=border_width, justification=justification, pad=pad, key=key, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, grab=grab, tooltip=tooltip, visible=visible, metadata=metadata)
		elif element == 'Titlebar':
			return sg.Titlebar(title=title, icon=icon, text_color=text_color, background_color=background_color, font=font, key=key)
		elif element == 'Tree':
			return sg.Tree(data=data, headings=headings, visible_column_map=visible_column_map, col_widths=col_widths, col0_width=col0_width, col0_heading=col0_heading, def_col_width=def_col_width, auto_size_columns=auto_size_columns, max_col_width=max_col_width, select_mode=select_mode, show_expanded=show_expanded, change_submits=change_submits, enable_events=enable_events, font=font, justification=justification, text_color=text_color, border_width=border_width, background_color=background_color, selected_row_colors=selected_row_colors, header_text_color=header_text_color, header_background_color=header_background_color, header_font=header_font, header_border_width=header_border_width, header_relief=header_relief, num_rows=num_rows, row_height=row_height, pad=pad, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)
		elif element == 'FolderBrowse':
			return sg.FolderBrowse(button_text=button_text, target=target, initial_folder=initial_folder, tooltip=tooltip, size=size, auto_size_button=auto_size_button, button_color=button_color, disabled=disabled, change_submits=change_submits, enable_events=enable_events, font=font, pad=pad, key=key, visible=visible, metadata=metadata)
		elif element == 'FilesBrowse':
			return sg.FilesBrowse(button_text=button_text, target=target, file_types=file_types, disabled=disabled, initial_folder=initial_folder, tooltip=tooltip, size=size, auto_size_button=auto_size_button, button_color=button_color, change_submits=change_submits, enable_events=enable_events, font=font, pad=pad, key=key, visible=visible, files_delimiter=files_delimiter, metadata=metadata, expand_x=expand_x, expand_y=expand_y)
		elif element == 'FileSaveAs':
			return sg.FileSaveAs(button_text=button_text, target=target, file_types=file_types, initial_folder=initial_folder, default_extension=default_extension, disabled=disabled, tooltip=tooltip, size=size, auto_size_button=auto_size_button, button_color=button_color, change_submits=change_submits, enable_events=enable_events, font=font, pad=pad, key=key, visible=visible, metadata=metadata, expand_x=expand_x, expand_y=expand_y)
		elif element == 'FileBrowse':
			return sg.FileBrowse(button_text=button_text, target=target, file_types=file_types, initial_folder=initial_folder, tooltip=tooltip, size=size, auto_size_button=auto_size_button, button_color=button_color, change_submits=change_submits, enable_events=enable_events, font=font, disabled=disabled, pad=pad, key=key, visible=visible, metadata=metadata, expand_x=expand_x, expand_y=expand_y)

	def set_option(self, data={}, **args):
		if data != {}:
			args = data
		for key in args.keys():
			if key in args.keys():
				val = args[key]
				self.options[key] = val
			else:
				print("Bad key:", key)
		for key in self.options.keys():
			val = self.options[key]
			globals()[key] = val
		return sg.set_options(icon=icon, button_color=button_color, element_size=element_size, button_element_size=button_element_size, margins=margins, element_padding=element_padding, auto_size_text=auto_size_text, auto_size_buttons=auto_size_buttons, font=font, border_width=border_width, slider_border_width=slider_border_width, slider_relief=slider_relief, text_justification=text_justification, background_color=background_color, element_background_color=element_background_color, text_element_background_color=text_element_background_color, input_elements_background_color=input_elements_background_color, input_text_color=input_text_color, scrollbar_color=scrollbar_color, text_color=text_color, element_text_color=element_text_color, debug_win_size=debug_win_size, window_location=window_location, error_button_color=error_button_color, tooltip_time=tooltip_time, tooltip_font=tooltip_font, use_ttk_buttons=use_ttk_buttons, ttk_theme=ttk_theme, suppress_error_popups=suppress_error_popups, suppress_raise_key_errors=suppress_raise_key_errors, suppress_key_guessing=suppress_key_guessing, warn_button_key_duplicates=warn_button_key_duplicates, enable_treeview_869_patch=enable_treeview_869_patch, enable_mac_notitlebar_patch=enable_mac_notitlebar_patch, use_custom_titlebar=use_custom_titlebar, titlebar_background_color=titlebar_background_color, titlebar_text_color=titlebar_text_color, titlebar_font=titlebar_font, titlebar_icon=titlebar_icon, user_settings_path=user_settings_path, pysimplegui_settings_path=pysimplegui_settings_path, pysimplegui_settings_filename=pysimplegui_settings_filename, keep_on_top=keep_on_top, dpi_awareness=dpi_awareness, scaling=scaling, disable_modal_windows=disable_modal_windows, force_modal_windows=force_modal_windows, tooltip_offset=tooltip_offset)
		

	def _win_insert_code(self):
		self.layout_obj.add(self._element('Multiline', default_text=self.code, expand_x=True, expand_y=True, key='-TXT_EDITOR-'))
		self.layout_obj.push()
		self.layout_obj.add(self._element('Button', button_text='Save', key='-SAVE_TEXT-'))
		self.layout_obj.add(self._element('Button', button_text='Import', key='-IMPORT_TEXT-'))
		self.layout_obj.add(self._element('Button', button_text='Close', key='-CLOSE_EDITOR-'))
		self.layout_obj.push()
		return self.child_window(title='Insert Python Function:', layout_obj=self.layout_obj)

	def get_user_code(self):
		self.code = self.load_text()
		self.win = self._win_insert_code()
		run = True
		data = None
		while run:
			event, values = self.win.read()
			if event == sg.WINDOW_CLOSED:
				sg.WINDOW_CLOSED
			else:
				#print(f"Event:{event}")
				#try:
				#	print(values[event])
				#except:
				#	print("no values!")
				if event == '-CLOSE_EDITOR-':
					break
				elif event == '-TXT_EDITOR-':
					data = values[event]
				elif event == '-SAVE_TEXT-':
					self.save_text(data)
					print("text saved! Changges made, restarting...")
					self.restart = True
					break
		self.win.close()
		if self.restart:
			return 'RESTART'
		else:
			return data

	def save_text(self, data, filepath=None):
		if filepath is None:
			self.filepath = os.path.join(os.path.expanduser("~"), '.gui', 'user', 'user_functions.py')
		else:
			self.filepath = filepath
		if not os.path.exists(self.filepath):
			fs.touch(self.filepath)
		with open(self.filepath, 'w') as f:
			f.write(data)
			f.close()

	def load_text(self, filepath=None):
		if filepath is None:
			self.filepath = os.path.join(os.path.expanduser("~"), '.gui', 'user', 'user_functions.py')
		else:
			self.filepath = filepath
		if not os.path.exists(self.filepath):
			fs.touch(self.filepath)
		with open(self.filepath, 'r') as f:
			data = f.read()
			f.close()
		return data

#	def _tree(self, td, headings=['Added Elements'], auto_size_columns=True):
#		return sg.Tree(data=td, headings=headings, auto_size_columns=True, select_mode=sg.TABLE_SELECT_MODE_EXTENDED, num_rows=10, col0_width=5, key='-TREE-', show_expanded=False, enable_events=True, expand_x=True, expand_y=True,)


#	def _frame(self, layout, title=None, size=(None, None), key=None):
#		title_color=None
#		background_color=None
#		title_location=None
#		relief="groove"
#		font=None
#		pad=None
#		border_width=None
#		tooltip=None
#		right_click_menu=None
#		expand_x=True
#		expand_y=True
#		grab=None
#		visible=True
#		element_justification="left"
#		vertical_alignment=None
#		metadata=None
#		return sg.Frame(title=title, layout=layout, title_color=title_color, background_color=background_color, title_location=title_location, relief=relief, size=size, font=font, pad=pad, border_width=border_width, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, grab=grab, visible=visible, element_justification=element_justification, vertical_alignment=vertical_alignment, metadata=metadata)

#	def _column(self, layout, size=(None, None), key=None):
#		background_color=None
#		pad=None
#		scrollable=False
#		vertical_scroll_only=False
#		right_click_menu=None
#		visible=True
#		justification=None
#		element_justification=None
#		vertical_alignment=None
#		grab=None
#		expand_x=None
#		expand_y=None
#		metadata=None
#		return sg.Column(layout=layout, background_color=background_color, size=size, pad=pad, scrollable=scrollable, vertical_scroll_only=vertical_scroll_only, right_click_menu=right_click_menu, key=key, visible=visible, justification=justification, element_justification=element_justification, vertical_alignment=vertical_alignment, grab=grab, expand_x=expand_x, expand_y=expand_y, metadata=metadata)

#	def _tab(self, layout, title=None, key=None):
#		title_color=None
#		background_color=None
#		font=None
#		pad=None
#		disabled=False
#		border_width=None
#		key=None
#		tooltip=None
#		right_click_menu=None
#		expand_x=True
#		expand_y=True
#		visible=True
#		element_justification="left"
#		image_source=None
#		image_subsample=None
#		metadata=None
#		return sg.Tab(title=title, layout=layout, title_color=title_color, background_color=background_color, font=font, pad=pad, disabled=disabled, border_width=border_width, key=key, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, element_justification=element_justification, image_source=image_source, image_subsample=image_subsample, metadata=metadata)

#	def _tab_group(self, layout, key=None, size=(None, None)):
#		tab_location=None
#		title_color=None
#		tab_background_color=None
#		selected_title_color=None
#		selected_background_color=None
#		background_color=None
#		focus_color=None
#		font=None
#		change_submits=False
#		enable_events=False
#		pad=None
#		border_width=None
#		tab_border_width=None
#		theme=None
#		tooltip=None
#		right_click_menu=None
#		expand_x=True
#		expand_y=True
#		visible=True
#		metadata=None
#		return sg.TabGroup(layout=layout, tab_location=tab_location, title_color=title_color, tab_background_color=tab_background_color, selected_title_color=selected_title_color, selected_background_color=selected_background_color, background_color=background_color, focus_color=focus_color, font=font, change_submits=change_submits, enable_events=enable_events, pad=pad, border_width=border_width, tab_border_width=tab_border_width, theme=theme, key=key, size=size, tooltip=tooltip, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)

#	def _add_tab(self, tab_object):
#		self.tabs.append([tab_object])

#	def build_tabs(self, key=None, size=(None, None)):
#		self.container = self._tab_group(layout=self.tabs, key=key, size=size)
#		return self.container

if __name__ == "__main__":
	ui = gui()
