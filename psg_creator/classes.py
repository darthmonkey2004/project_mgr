class element():
	def __init__(self, data={}, **args):
		if data != {}:
			args = data
		for key in args.keys():
			val = args[key]
			self.__dict__[key] = val

class dtype():
	def isint(self, num):
		try:
			_ = int(num)
			return True
		except:
			return False

	def isbool(self, var):
		if var == 1 or var == 0:
			return True
		elif var == 'True' or var == 'False':
			return True
		else:
			return False

	def tobool(self, var):
		if self.isbool(var):
			if var == 'True':
				return True
			elif var == 'False':
				return False
			elif var == 1 or var == 0:
				return bool(var)
			else:
				txt = f"Error - Unknown exception (var={var})"
				raise Exception(txt)
		else:
			txt = f"Error - Argument is not a clear boolean! (var={var})"
			raise Exception(txt)

	def isnone(self, var):
		if var == 'None' or var == 'Null' or var == 'null':
			return True
		else:
			return False

	def tonone(self, var):
		if self.isnone(var):
			return None
		else:
			txt = f"Error - Argument is not recognized as a null value! (var={var})"
			raise Exception(txt)

	def istuple(self, var):
		s = var[len(var) - 1:]
		e = var[:1]
		if e == '(' and s == ')':
			return True
		else:
			return False


	def _to_iterable(self, var):
		if '[' in var and ']' in var:
			ts1 = '['
			ts2 = ']'
			_type = list
		elif '(' in var and ')' in var:
			ts1 = '('
			ts2 = ')'
			_type = tuple
		out = []
		addflag = False
		var = var[1:len(var) - 1]
		if ', ' in var:
			s = ', '
		elif ',' in var and ', ' not in var:
			s = ','
		else:
			s = None
		add = []
		if s is not None:
			for chunk in var.split(s):
				#print(chunk)
				chunk = chunk.replace("'", "").replace('"', '')
				if chunk[0] == ts1:
					chunk = chunk[1:]
					addflag = True
				elif chunk[len(chunk) - 1] == ts2:
					chunk = chunk[:len(chunk) - 1]
					add.append(self._to_type(chunk))
					if _type == tuple:
						t = tuple(add)
					elif _type == list:
						t = add
					out.append(t)
					addflag = False
					add = []
				if addflag:
					add.append(self._to_type(chunk))
					#print(f"addflag:{addflag}, chunk:{chunk}, add:{add}")
				else:
					out.append(self._to_type(chunk))
		else:
			out.append(self._to_type(var))
		if _type == tuple:
			return tuple(out)
		elif _type == list:
			return out

	def _is_dict(self, var):
		s = var[len(var) - 1:]
		e = var[:1]
		if e == '{' and s == '}':
			return True
		else:
			return False

	def _to_dict(self, var):
		d = {}
		chunks = var.split(', ')
		for chunk in chunks:
			print(chunk)
			if ': {' not in chunk:	
				chunk = chunk.replace('{', '').replace('}', '')
				k, v = chunk.replace("'", '').replace('"', '').split(': ')
				if self.isint(v):
					v = int(v)
				d[k] = v
			elif ': {' in chunk:
				d2 = {}
				k = chunk.split(': ')[0]
				k2, v2 = chunk.split(s)[1].replace('{', '').replace('}', '').replace("'", '').replace('"', '').split(': ')
				if creator.isint(v2):
					v2 = int(v2)
				d2[k2] = v2
				d[k] = d2
		return d
			

	def islist(self, var):
		s = var[len(var) - 1:]
		e = var[:1]
		if e == '[' and s == ']':
			return True
		else:
			return False

	def tolist(self, var):
		l = '[1, 2, 3, 4, [5, 6, 7], [None, "this is a string"]]'



	def _to_type(self, var):
		if '{' not in var and '}' not in var:
			var = var.replace("'", "")
		if var == "(('ALL Files', '*.* *'),),":
			return "*.*"
		elif self.istuple(var) or self.islist(var):
			return self._to_iterable(var)
		elif self.isbool(var):
			return self.tobool(var)
		elif self.isint(var):
			return int(var)
		elif self.isnone(var):
			return self.tonone(var)
		else:
			return var
	

def read_loop(win):
	exit = False
	while not exit:
		win.metadata[0]['size'] = win.size
		win.metadata[0]['location'] = win.current_location()
		event, values = win.read()
		print(event)
		try:
			print(values[event])
		except:
			print("no values!")
		if event == sg.WINDOW_CLOSED:
			exit = True
	quit(win)


class layout():
	def __init__(self):
		self.rows = []
		self.row = []
		self.map = []
		self.map_row = []
	def add(self, obj):
		self.map_row.append(obj.key)
		self.row.append(obj)
	def push(self):
		if self.map_row not in self.map and len(self.row) > 0:
			self.rows.append(self.row)
			self.map.append(self.map_row)
			self.map_row = []
			self.row = []
		elif self.map_row in self.map:
			txt = f"Error - row already in map!!"
			print(txt)
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
