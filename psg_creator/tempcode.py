import PySimpleGUI as sg

def window():
	layout = []
	layout.append([sg.Listbox(values=['val1', 'val2', 'val3'], default_values='val1', select_mode=None, change_submits=True, enable_events=True, bind_return_key=False, disabled=False, auto_size_text=None, font=None, no_scrollbar=False, horizontal_scroll=False, background_color=None, text_color=None, highlight_background_color=None, highlight_text_color=None, key='-LISTBOX_ITEMS-', pad=None, tooltip=None, expand_x=False, expand_y=False, right_click_menu=None, visible=True, metadata=(False, None))])
	layout.append([sg.Input(default_text=None, disabled=False, password_char='', justification=None, background_color=None, text_color=None, font=None, tooltip=None, border_width=None, change_submits=True, enable_events=True, do_not_clear=True, key='-INPUT_ADD_ITEM-', focus=False, pad=None, use_readonly_for_disable=True, readonly=False, disabled_readonly_background_color=None, disabled_readonly_text_color=None, expand_x=False, expand_y=False, right_click_menu=None, visible=True, metadata=(False, None))])
	layout.append([sg.Button(button_text='Add', button_type=7, target=(None, None), tooltip=None, file_types=(), initial_folder=None, default_extension='', disabled=False, change_submits=True, enable_events=True, image_filename=None, image_data=None, image_size=(None, None), image_subsample=None, image_source=None, border_width=None, auto_size_button=None, button_color=None, disabled_button_color=None, highlight_colors=None, mouseover_colors=(None, None), use_ttk_buttons=None, font=None, bind_return_key=False, focus=False, pad=None, key='-Add-', right_click_menu=None, expand_x=False, expand_y=False, visible=True, metadata=(True, ['-INPUT_ADD_ITEM-', '-LISTBOX_ITEMS-'])),
		sg.Button(button_text='Rm', button_type=7, target=(None, None), tooltip=None, file_types=('',), initial_folder=None, default_extension='', disabled=False, change_submits=True, enable_events=True, image_filename=None, image_data=None, image_size=(None, None), image_subsample=None, image_source=None, border_width=None, auto_size_button=None, button_color=None, disabled_button_color=None, highlight_colors=None, mouseover_colors=(None, None), use_ttk_buttons=None, font=None, bind_return_key=False, focus=False, pad=None, key='-Rm-', right_click_menu=None, expand_x=False, expand_y=False, visible=True, metadata=(True, '-LISTBOX_ITEMS-'))])
	frame = sg.Frame(layout=layout, title='creator.Preview Frame', title_color=None, background_color=None, title_location=None, relief='groove', size=(None, None), font=None, pad=None, border_width=None, key=None, tooltip=None, right_click_menu=None, expand_x=False, expand_y=False, grab=None, visible=True, element_justification='top', vertical_alignment=None, metadata=None)
	return sg.Window(layout=[[frame]], title='creator.Preview', finalize=True, size=(None, None), location=(None, None))

def add(data, val):
	data.append(val)
	return data

def rm(data, val):
	idx = data.index(val)
	del data[idx]
	return data

def main():
	win = window()
	while True:
		event, values = win.read()
		if event == sg.WIN_CLOSED:
			break
		else:
			has_function, fdata = win[event].metadata
			if has_function:
				f = event.split('-')[1].lower()
				if f in list(globals().keys()):
					function = globals()[f]
				else:
					function = None
				if type(fdata) == list or type(fdata) == tuple:
					src, target = fdata
				else:
					src = None
					target = fdata
				if src is not None:
					print("TODO: add helper window to select source/destination from registered element keys.")
					val = win[src].get() # get value from window object
					print("val:", val, "src:", src, "target:", target)
				elif src is None and val is None:# if element has no value and no source listed, complain loudly...
					pass
				try:
					if target is not None:
						data = win[target].__dict__['Values']# get any data in target element
					else:
						data = None
				except Exception as e:
					data = None
				if type(val) == list and len(val) == 1:
					val = val[0]
				if val is None and data is None:
					try:
						ret = function()
						win[target].update(ret)
					except Exception as err:
						print(f"Unable to run target function ({function}, event={e}, val={val})! {err}")
				elif val is not None and data is not None:
					print(f"Function running (args=(data={data},val={val})):function:{function}, event:{event}")
					try:
						ret = function(data=data, val=val)
						win[target].update(ret)
						print(f"function results:{ret}, target key:{target}")
					except Exception as err:
						print(f"Unable to run target function ({function})! {err}")			
				elif val is not None and data is None:
					#print(f"Function running (arg:{val})):function:{function}, event:{event}")
					try:
						ret = function(val=val)
						win[target].update(ret)
					except Exception as err:
						print(f"Unable to run target function ({function}, value={val})! {err}")


if __name__ == "__main__":
	main()
