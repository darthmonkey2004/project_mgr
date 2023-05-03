from preview_png import write_default_preview, preview_img_path
from gui import *
from classes import *
from element_data import *
from gui import *
from helper_utils import filesystem
from usercode import *
fs = filesystem.filesystem()
ui = gui()

todo = """
_preview(): Modify on event if targets[key].target_key is not None, pass window object to given user code, perform action on window, and return window object.
	If that doesn't work, get current window value (self.preview_win.get()) and include as data, with val=values[event], then update window with result (return modified data)
modify main event loop for target execution dependant on if element has a target set. Else, use main event loop (break, close, etc)
"""
print(todo)

class ui_creator():
	def __init__(self, auto_save=True):
		self.auto_save = auto_save
		self.target_obj = target_obj
		self.preview_data = []
		self.preview_img = os.path.join(os.path.expanduser("~"), '.gui', 'preview.png')
		self.defaults = elements_defaults
		self.ui = gui()
		if not os.path.exists(preview_img_path):
			write_default_preview()
		self.elements = {}
		self.map = layout()
		self.dtype = dtype()
		self.preview_win = None
		self.settings = None
		self.location = None
		self.screen = None
		self.run_preview = True
		self.functions = {}
		self.menu_obj = menu()


	def _menu_main_window(self):
		layout_obj = layout()
		layout_obj.add(self.ui._element('Button', button_text='Add Menu Item', key='-ADD_MENU_ITEM-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Button', button_text='Add Sub-Menu Item', key='-ADD_SUB_ITEM-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Button', button_text='Ok', key='-OK-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Button', button_text='Cancel', key='-CANCEL-'))
		layout_obj.push()
		self.menu_creator_win = ui.child_window(layout_obj=layout_obj, title='Menu Creator', run=False)
		return self.menu_creator_win

	def _add_menu_item_win(self):
		layout_obj = layout()
		layout_obj.add(self.ui._element('Text', text='Parent Item:', key='-TEXT_PARENT-'))
		layout_obj.add(self.ui._element('Input', key='-INPUT_PARENT-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Text', text='Items:', key='-TEXT_ITEMS-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Listbox', values=[], expand_x=True, expand_y=True, key='-LISTBOX_ITEMS-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Input', key='-INPUT_ADD_ITEM-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Button', button_text='Add', key='-BTN_ADD_ITEM-'))
		layout_obj.add(self.ui._element('Button', button_text='Remove', key='-BTN_REMOVE_ITEM-'))
		layout_obj.add(self.ui._element('Button', button_text='Ok', key='-OK-'))
		layout_obj.add(self.ui._element('Button', button_text='Cancel', key='-CANCEL-'))
		layout_obj.push()
		win = ui.child_window(layout_obj=layout_obj, title='Add Menu Item', run=False)
		return win

	def _add_menu_item(self):
		win = self._add_menu_item_win()
		item = None
		parent = None
		while True:
			e, v = win.read()
			if e == '-INPUT_PARENT-':
				parent = v[e]
				print("Parent set:", parent)
			elif e == '-INPUT_ADD_ITEM-':
				item = v[e]
				print("Item string set:", item)
			elif e == '-LISTBOX_ITEMS-':
				item = v[e][0]
				print("Item in items list selected:", item)
			elif e == '-BTN_ADD_ITEM-':
				if item is not None:
					vals = win['-LISTBOX_ITEMS-'].Values
					vals.append(item)
					win['-LISTBOX_ITEMS-'].update(vals)
					print("Items list updated!", vals)
				else:
					print("item not yet set!")
			elif e == '-BTN_REMOVE_ITEM-':
				if item is not None:
					vals = win['-LISTBOX_ITEMS-'].Values
					idx = vals.index(item)
					del vals[idx]
					win['-LISTBOX_ITEMS-'].update(vals)
					print("item removed:", item)
				else:
					print("no item selected!")
			elif e == '-OK-':
				if parent is not None:
					items = win['-LISTBOX_ITEMS-'].Values
					self.menu_obj.add_to_menu(parent=parent, items=items)
					win.close()
					break

	def create_menu(self, menu_type='Menu'):
		menu_types = ['MenubarCustom', 'ButtonMenu', 'OptionMenu', 'Menu']
		if menu_type not in menu_types:
			print("Bad type:", menu_type)
			return None
		k = f"-{menu_type.upper()}-"
		menu_def = self.menu_def_creator_main()
		return self.ui._element(menu_type, enable_events=True, menu_definition=menu_def, tearoff=True, key=k)
		


	def _add_sub_item(self):
		layout_obj = layout()
		layout_obj.add(self.ui._element('Text', text='Parent Item:', key='-TEXT_PARENT-'))
		layout_obj.add(self.ui._element('Input', key='-INPUT_PARENT-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Text', text='Sub Item:', key='-TEXT_SUB_ITEM-'))
		layout_obj.add(self.ui._element('Input', key='-INPUT_SUB_ITEM-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Text', text='Items:', key='-TEXT_ITEMS-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Listbox', values=[], expand_x=True, expand_y=True, key='-LISTBOX_ITEMS-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Input', key='-INPUT_ADD_ITEM-'))
		layout_obj.push()
		layout_obj.add(self.ui._element('Button', button_text='Add', key='-BTN_ADD_ITEM-'))
		layout_obj.add(self.ui._element('Button', button_text='Remove', key='-BTN_REMOVE_ITEM-'))
		layout_obj.add(self.ui._element('Button', button_text='Ok', key='-OK-'))
		layout_obj.add(self.ui._element('Button', button_text='Cancel', key='-CANCEL-'))
		layout_obj.push()
		win = ui.child_window(layout_obj=layout_obj, title='Add Menu Item', run=False)
		item = None
		parent = None
		while True:
			e, v = win.read()
			if e == '-INPUT_PARENT-':
				parent = v[e]
				print("Parent set:", parent)
			elif e == '-INPUT_ADD_ITEM-':
				item = v[e]
				print("Item string set:", item)
			elif e == '-LISTBOX_ITEMS-':
				item = v[e][0]
				print("Item in items list selected:", item)
			elif e == '-BTN_ADD_ITEM-':
				if item is not None:
					vals = win['-LISTBOX_ITEMS-'].Values
					vals.append(item)
					win['-LISTBOX_ITEMS-'].update(vals)
					print("Items list updated!", vals)
				else:
					print("item not yet set!")
			elif e == '-BTN_REMOVE_ITEM-':
				if item is not None:
					vals = win['-LISTBOX_ITEMS-'].Values
					idx = vals.index(item)
					del vals[idx]
					win['-LISTBOX_ITEMS-'].update(vals)
					print("item removed:", item)
				else:
					print("no item selected!")
			elif e == '-INPUT_SUB_ITEM-':
				subitem = v[e]
				print("Menu sub-item set:", subitem)
			elif e == '-OK-':
				if parent is not None and subitem is not None:
					items = win['-LISTBOX_ITEMS-'].Values
					self.menu_obj.add_to_submenu(parent=parent, name=subitem, items=items)
					win.close()
					break
					
	def menu_def_creator_main(self):
		self.menu_def = []
		self.menu_creator_win = self._menu_main_window()
		while True:
			e, v = self.menu_creator_win.read()
			if e == sg.WIN_CLOSED:
				break
			elif e == '-ADD_MENU_ITEM-':
				self._add_menu_item()
			elif e == '-ADD_SUB_ITEM-':
				self._add_sub_item()
			elif e == '-OK-':
				self.menu_def = self.menu_obj.get_menu()
				self.menu_creator_win.close()
				break
			elif e == '-CANCEL-':
				self.menu_def = []
				print("Cancelling menu creation...")
		return self.menu_def


	def cap(self, win_id):
		imgpath = os.path.join(os.path.expanduser("~"), '.gui', 'preview.png')
		com = f"convert x:{win_id} \"{imgpath}\""
		try:
			ret = subprocess.check_output(com, shell=True).decode().strip()
			if ret == '':
				self.preview_img = imgpath
				return imgpath
			else:
				return ret
		except Exception as e:
			print("error: ", e)
			return None

	def win_info(self):
		com = "xwininfo -root -all"
		try:
			return subprocess.check_output(com, shell=True).decode().strip().splitlines()
		except Exception as e:
			print("error: ", e)
			return None

	def get_preview_win_id(self):
		info = self.win_info()
		title = "Preview"
		for line in info:
			if f"!toplevel" in line and title in line:
				return line.strip().split(' ')[0]

	def get_preview_img(self, map_data=None):
		if map_data is None:
			map_data = self.map
		self.main_window.keep_on_top_set()
		self.preview_win = self._preview(data=self.preview_data, run=False)
		win_id = self.get_preview_win_id()
		self.preview_img = self.cap(win_id)
		self.main_window['-PREVIEW_IMG-'].update(self.preview_img)
		self.preview_win.close()
		self.main_window.keep_on_top_clear()
		return self.preview_img


	def create_ui_fromFile(self, preview=True, filepath=None):
		self.data = self.ui.load(filepath)
		self.filepath = filepath
		self.create_ui(data=self.data)

	def create_ui(self, preview=True, data=None):
		if data is None:
			data = self.data
		if preview:
			self.preview_data = data
		for element, d in data:
			print("create_ui:", element, d)
			if element == 'push':
				print("pushing!", element, d)
				self.ui.layout_obj.push()
			else:
				print("add to row:", element, d)
				self.ui.layout_obj.add(self.ui._element(element=element, data=d))
		self.ui.layout_obj.push()
		self.window = self.ui.child_window(title='Add Element', layout_obj=self.ui.layout_obj)
		_ = self.window.read(timeout=1)
		self.window.metadata = data
		return self.window

	def save_ui(self, data=None, filepath=None):
		if data is not None:
			self.preview_data = data
		if filepath is None:
			filepath = os.path.join(os.path.expanduser("~"), '.gui', f"creator.Preview.dat")
		self.ui.save(filepath=filepath, data=self.preview_data)

	def load_ui(self, filepath=None, run=False):
		if filepath is None:
			path = os.path.join(os.path.expanduser("~"), '.gui')
			filepath = os.path.join(os.path.expanduser("~"), '.gui', "creator.Preview.dat")
		self.preview_data = self.ui.load(filepath)
		if run:
			self._preview(data=self.preview_data, run=True)
		return self.preview_data

	def quit(self, win=None):
		if win is None:
			win = self.window
		path = os.path.join(os.path.expanduser("~"), '.gui')
		filepath = os.path.join(os.path.expanduser("~"), '.gui', f"{win.Title}.dat")
		if not os.path.exists(path):
			fs.mkdir(path)
		save_ui(win)
		win.close()

	def _add_element_read_data(self, element_name):
		win = self.ui.child_windows['Add Element']
		self.element_data = self.defaults[element_name]
		keys = list(self.element_data.keys())
		out = {}
		for key in keys:
			if key == 'target_function':
				v = self.dtype._to_type(win['-TARGET_FUNCTION-'].get())
				val = win['-KEY-'].get()
				print("function:", val, v)
				if v:
					target_key = self.dtype._to_type(win['-TARGET_KEY-'].get())
					self.functions[val] = target_obj(key=val, target_key=target_key)
					print("target_key:", self.functions[val].target_key)
				
			if "-" in key:
				key = key.split('-')[1].lower()
			if key == 'element_type':
				out['element_type'] = element_name
			else:
				k = f"-{key.upper()}-"
				if k != '-SIZE-':
					out[key] = self.dtype._to_type(win[k].get())
		element_object = element(data=out)
		return out, element_object

	def _add_element_data(self, element_data=None):
		if element_data is not None:
			self.element_data = element_data
		key = self.element_data['key']
		element_type = self.element_data['element_type']
		keys = list(self.elements.keys())
		if key in keys:
			txt = f"Duplicate key found! ({key})! adding suffix.."
			key = f"{key}_2"
		self.elements[key] = self.element_data
		self.preview_data.append((element_type, self.element_data))
		self.map.add(self.ui._element(element_type, data=self.element_data))
		if self.auto_save and self.preview_data != []:
			self.save_ui(self.preview_data)

	def _win_add_element(self, element):
		if element is None:
			print("No element selected!")
			return None			
		self.ui.layout_obj.clear()
		data = {}
		self.element_data = self.defaults[element]
		if element == 'MenubarCustom' or element == 'OptionMenu' or element == 'ButtonMenu' or element == 'Menu':
			self.menu_def = self.menu_def_creator_main()
		else:
			self.menu_def = None
		self.element_data['target_function'] = False
		self.element_data['target_key'] = None
		keys = list(self.element_data.keys())
		vals = list(self.element_data.values())
		for key in keys:
			idx = keys.index(key)
			val = vals[idx]
			if key == 'size':
				w, h = val
				if w is None:
					w = 'None'
				if h is None:
					h = 'None'
				self.ui.layout_obj.add(self.ui._element('Text', text='Width:'))
				self.ui.layout_obj.add(self.ui._element('Input', default_text=w, key=f"-WIDTH-"))
				self.ui.layout_obj.push()
				self.ui.layout_obj.add(self.ui._element('Text', text='Height:'))
				self.ui.layout_obj.add(self.ui._element('Input', default_text=h, key=f"-HEIGHT-"))
				self.ui.layout_obj.push()
			else:
				val = str(val)
				self.ui.layout_obj.add(self.ui._element('Text', text=key.title()))
				self.ui.layout_obj.add(self.ui._element('Input', default_text=val, key=f"-{key.upper()}-"))
				self.ui.layout_obj.push()
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Ok', key='-OK-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Break', key='-BREAK-'))
		self.ui.layout_obj.push()
		win = self.ui.child_window(title='Add Element', layout_obj = self.ui.layout_obj)
		self.ui.layout_obj.rows = []
		self.ui.layout_obj.row = []
		map_data = self.ui.layout_obj.map
		self.element_data['element_type'] = element
		self.element_data['target_function'] = False
		while True:
			self.key, values = win.read()
			if self.key is not None and '-' in self.key:
				k = self.key.split('-')[1].lower()
			if self.key == sg.WINDOW_CLOSED:
				break
			elif self.key == '-OK-':
				self.element_data, element_obj = self._add_element_read_data(element)
				win.close()
			elif self.key == '-BREAK-':
				self.element_data, element_obj = self._add_element_read_data(element)
				self.elements[element_obj.key] = element_obj
				break
			else:
				try:
					self.value = self.dtype._to_type(values[self.key])
				except:
					try:
						self.value = values[key]
					except:
						self.value = None
				if self.key == '-WIDTH-':
					self.key = '-SIZE-'
					self.element_data[k] = self.value, self.element_data['-HEIGHT-']
				elif self.key == '-HEIGHT-':
					self.key = '-SIZE-'
					self.element_data[k] = self.element_data['-WIDTH-'], self.value
				elif self.key == '-BUTTON_TEXT-' or self.key == '-DEFAULT_TEXT-' or self.key == '-TEXT-':
					win['-KEY-'].update(f"-{values[self.key]}-")
				#if self.key == '-ADD_TARGET_FUNCTION-':
				#	self.functions[element_data[k]['key']] = self.new_target(key=element_data[k]['key'])
				#	element_data['target_function'] = True
				self.element_data[k] = val
				#print(f"set key {key} to {val}!")
		self.ui.layout_obj.clear()
		if self.menu_def is not None:
			self.element_data['menu_definition'] = self.menu_def
		if self.element_data != self.defaults[element]:
			return self.element_data
		else:
			return None


	def _preview(self, data=None, title='Preview', run=True):
		#read provided data. if None, get from class instance
		if data is None:
			if self.preview_data == []:
				self.preview_data
			data = self.preview_data
		self.run_preview = run # set run flag
		layout_obj = layout() # create new layout object (avoid re-use layout error)
		print(data)
		for e, d in data:#iterate through elements and add to layout
			if e == 'push':
				layout_obj.push()
			else:
				layout_obj.add(self.ui._element(e, data=d))
				if d['target_function']:
					#print(f"adding target ({e}): {d['key']}")
					key = d['key']
					self.functions[key] = target_obj(key=key, target_key=d['target_key'])

		layout_obj.push()
		self.preview_win = self.ui.child_window(layout_obj=layout_obj, title=title, run=False, location=self.main_window.current_location())
		self.preview_win.metadata = {'targets': self.functions} # store function objects to window metadata
		while self.run_preview:
			e, v = self.preview_win.read() #get event and values dictionary
			print(f"run:{self.run_preview}, event:{e}, values:{v}, targets:{self.functions.keys()}")
			if e == sg.WINDOW_CLOSED:
				break # break loop if window closed
			else:
				try:
					val = v[e] # try to set value from current element.
					globals()[e] = val
				except Exception as err:
					globals()[e] = None # if no value, set as None
				if e in self.functions.keys(): # if element has a registered function object...
					function = self.functions[e].target # set function to variable
					key = self.functions[e].key # set key of triggering element
					target_key = self.functions[e].target_key
					if target_key is not None:
						tdata = self.dtype._to_type() # grab source and destination element keys (convert type from string)
					else:
						tdata = None
						src = None
						target = None
					if type(tdata) == tuple: # if more than one key provided, set src and target
						src, target = tdata
					elif type(tdata) == str: # if only one key, set target (src=None)
						src = None
						target = tdata
					if src is not None:
						print("TODO: add helper window to select source/destination from registered element keys.")
						val = self.preview_win[src].get() # get value from window object
						print("val:", val, "src:", src, "target:", target)
					elif src is None and val is None:# if element has no value and no source listed, complain loudly...
						#print(f"Warning - element {e} has no source or value! (No arguments or elements for function)")
						pass
					try:
						if target is not None:
							data = self.preview_win[target].__dict__['Values']# get any data in target element
						else:
							data = None
					except Exception as e:
						#print(f"Couldn't get data from element {target}: {e}. Setting as None...")
						data = None
					#print(f"target:{target}, key:{key}, data:{data}, value:{val}")
					if type(val) == list and len(val) == 1:
						val = val[0]
					if val is None and data is None:
						#print("Function running (no arguments):", function, e)
						try:
							ret = function()
							self.preview_win[target].update(ret)
							#print(f"result:{ret}")
						except Exception as err:
							print(f"Unable to run target function ({function}, event={e}, val={val})! {err}")
					elif val is not None and data is not None:
						print(f"Function running (args=(data={data},val={val})):function:{function}, event:{e}")
						try:
							ret = function(data=data, val=val)
							self.preview_win[target].update(ret)
							print(f"function results:{ret}, target key:{target}")
						except Exception as err:
							print(f"Unable to run target function ({function})! {err}")
							
					elif val is not None and data is None:
						#print(f"Function running (arg:{val})):function:{function}, event:{e}")
						try:
							ret = function(val=val)
							self.preview_win[target].update(ret)
							#print(f"result:{ret}")
						except Exception as err:
							print(f"Unable to run target function ({function}, value={val})! {err}")	
		return self.preview_win

	def _win_main(self):
		self.ui.layout_obj.clear()
		l = [[self.ui._element('Image', source=self.preview_img, key='-PREVIEW_IMG-', expand_x=True, expand_y=True)]]
		self.ui.layout_obj.add(self.ui._element('Frame', layout=l, key='-PREVIEW_IMG_FRAME-', expand_x=True, expand_y=True))
		self.ui.layout_obj.push()
		l1 = [[self.ui._element('Listbox', values=list(elements_defaults.keys()), size=(30, 30), key='-ELEMENTS-', expand_x=False, expand_y=True)]]
		self.ui.layout_obj.add(self.ui._element('Frame', layout=l1, key='-LIST_FRAME-'))
		l2 = [[self.ui._element('Listbox', values=[], size=(30, 10), key='-ELEMENTS_LIST-', expand_x=False, expand_y=False)],
			[self.ui._element('Listbox', values=[], size=(30, 10), key='-LAYOUT_ROWS-', expand_x=False, expand_y=False)],
			[self.ui._element('Listbox', values=[], size=(30, 10), key='-LAYOUT_ROW_ITEMS-', expand_x=False, expand_y=False)]]
		self.ui.layout_obj.add(self.ui._element('Column', layout=l2, scrollable=True, expand_x=True, expand_y=True, key='-ELEMENT_ADD_COLUMN-'))
		self.ui.layout_obj.push()
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Add Element', key='-ADD_ELEMENT-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Break', key='-BREAK-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Push Row', key='-PUSH-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Remove Element', key='-RM_ELEMENT-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Preview...', key='-PREVIEW-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Save!', key='-SAVE-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Save As...', key='-SAVE_AS-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Load...', key='-LOAD-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Update Preview', key='-UPDATE_PREVIEW-'))
		self.ui.layout_obj.add(self.ui._element('Button', button_text='Code Editor', key='-CODE_EDITOR-'))
		self.ui.layout_obj.push()
		self.ui.layout_obj.layout = self.ui.layout_obj.rows
		self.main_window = self.ui.pack()
		self.ui.layout_obj.row = []
		return self.main_window

	def rm_element(self, selected=None):
		if selected is not None:
			self.selected = selected
		l = []
		for item in self.map.map_row:
			if item == self.selected:
				pass
			else:
				l.append(newrow)

		self.map.map_row = l
		l = []
		for row in self.map.map:
			newrow = []
			for item in row:
				if item == self.selected:
					pass
				else:
					newrow.append(item)
			l.append(newrow)

		self.map.map = l

		l = []
		for e, d in self.preview_data:
			if d['key'] == self.selected:
				pass
			else:
				l.append((e, d))
		try:
			del self.elements[self.selected]
		except:
			pass
		self.preview_data = l
		self.main_window['-ELEMENTS_LIST-'].update(list(self.elements.keys()))
		self.main_window['-LAYOUT_ROWS-'].update(self.map.map)
		self.main_window['-LAYOUT_ROW_ITEMS-'].update(self.map.map_row)
		self.selected = None

	def update_preview_img(self):
		print("updating preview image")
		img = self.get_preview_img()
		self.main_window['-PREVIEW_IMG-'].update(source=img)


	def main(self):
		exit = False
		self.main_window = self._win_main()
		elements = []
		self.selected = None
		while True:
			if exit:
				break
			event, values = self.main_window.read()
			if event == sg.WINDOW_CLOSED:
				exit = True
			elif event == '-ELEMENTS-':
				try:
					self.selected = values[event][0]
				except:
					self.selected = None
				print("Element selected:", self.selected)
			elif event == '-LAYOUT_ITEMS-' or event == '-LAYOUT_ROW_ITEMS-' or event == '-ELEMENTS_LIST-':
				try:
					self.selected = values[event][0]
				except:
					self.selected = None
				print("Element selected:", self.selected)
			elif event == '-ADD_ELEMENT-':
				data = self._win_add_element(self.selected)
				if data is not None:
					self.element_data = data
					self._add_element_data(self.element_data)
					self.main_window['-ELEMENTS_LIST-'].update(list(self.elements.keys()))
					self.main_window['-LAYOUT_ROWS-'].update(self.map.map)
					self.main_window['-LAYOUT_ROW_ITEMS-'].update(self.map.map_row)
				self.update_preview_img()
			elif event == '-UPDATE_PREVIEW-':
				self.update_preview_img()
			elif event == '-RM_ELEMENT-':
				if self.selected is not None:
					self.rm_element(self.selected)
				self.update_preview_img()
			elif event == '-PUSH-':
				self.map.push()
				self.preview_data.append(('push', None))
				self.main_window['-ELEMENTS_LIST-'].update(list(self.elements.keys()))
				self.main_window['-LAYOUT_ROWS-'].update(self.map.map)
				self.main_window['-LAYOUT_ROW_ITEMS-'].update(self.map.map_row)
				self.update_preview_img()
			elif event == '-CLOSE-':
				self.ui.save()
				self.main_window.close()
				exit = true
			elif event == '-PREVIEW-':
				self.preview_win = self._preview()
			elif event == '-SAVE-':
				self.preview_win = self._preview()
				#ed, md = self.preview_win.metadata
				data = self.preview_data
				title = self.preview_win.Title
				filepath = os.path.join(os.path.expanduser("~"), '.gui', f"creator.{title}.dat")
				self.ui.save(data=data, filepath=filepath)
				print("Saved!")
			elif event == '-SAVE_AS-':
				filepath = self.ui.file_browser(browse_type='save')
				self.preview_win = self._preview()
				data = self.preview_data
				self.ui.save(data=data, filepath=filepath)
				print("Saved as:", filepath)
				#self.save_ui(win=self.preview_win, filepath=filepath)
			elif event == '-BREAK-':
				break
			elif event == '-LOAD-':
				path = os.path.join(os.path.expanduser("~"), '.gui')
				filepath = self.ui.file_browser(browse_type='file', cwd=path)
				#self.create_ui_fromFile(filepath=filepath)
				self.preview_data = self.load_ui(filepath=filepath, run=True)
				self.update_preview_img()
			elif event == '-CODE_EDITOR-':
				self.ui.get_user_code()
			print("Event:", event)

if __name__ == "__main__":
	creator = ui_creator()
	creator.main()
