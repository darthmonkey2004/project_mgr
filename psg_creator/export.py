import os
from psg_creator import creator
creator = creator.ui_creator()

def build_layout_section(data):
	code = []
	txt = """#!/usr/env python3

import PySimpleGUI as sg

def win():
	layout = []"""
	out = []
	for element_name, element_data in data:
		print("element:", element_name)
		if element_name == 'push':
			out = "\n\t\t".join(out)
			line = f"	layout.append([{out}])"
			out = []
			code.append(line)
		else:
			target_function = element_data['target_function']
			target_key = element_data['target_key']
			del element_data['target_function']
			del element_data['target_key']
			del element_data['element_type']
			element_data['metadata'] = (target_function, target_key)
			l = []
			for key in element_data.keys():
				val = element_data[key]
				if type(val) == str:
					if "'" not in val:
						l.append(f"{key}='{val}'")
					else:
						l.append(f"{key}={val}")
				else:
					l.append(f"{key}={val}")
			l = ", ".join(l)
			string = f"sg.{element_name}({l}),"
			out.append(string)
	return "\n".join(code)


def get_main_code():
	main = """def main():
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
"""
	return main


def export(filepath='/home/monkey/.gui/creator.Preview.dat', size=(None, None), location=(None, None)):
	code = []
	txt = """import PySimpleGUI as sg

def window():
	layout = []"""
	code.append(txt)
	data = creator.load_ui(filepath)
	title = os.path.basename(filepath).split('.dat')[0]
	code.append(build_layout_section(data))
	frame_defs = creator.defaults['Frame']
	frame_defs['title'] = f"{title} Frame"
	l = []
	#l.append(f"layout=layout")
	try:
		del frame_defs['element_type']
		del frame_defs['layout']
	except:
		pass
	for key in frame_defs.keys():
		if key == 'layout':
			pass
		else:
			val = frame_defs[key]
			if type(val) == str:
				if "'" not in val:
					string = f"{key}='{val}'"
				else:
					string = f"{key}={val}"
			else:
				string = f"{key}={val}"
			l.append(string)
	l = ", ".join(l)
	txt = f"	frame = sg.Frame(layout=layout, {l})"
	code.append(txt)
	string = f"	return sg.Window(layout=[[frame]], title='{title}', finalize=True, size={size}, location={location})"
	code.append(string)
	code = "\n".join(code)
	code = code.replace(')],])', ')]])')
	code = code.replace(')],)', ')])')
	code = code.replace(')),])', '))])')
	usercode_file = os.path.join(os.path.expanduser("~"), '.gui', 'user', 'user_functions.py')
	with open(usercode_file, 'r') as f:
		usercode = f.read()
		f.close()
	code = f"""{code}

{usercode}

{get_main_code()}"""
	return code

if __name__ == "__main__":
	with open('/var/dev/psg_creator/tempcode.py', 'w') as f:
		f.write(export())
		f.close()
	print(export())

		
