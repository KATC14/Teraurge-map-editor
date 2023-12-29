import json
import tkinter
import tkinter.colorchooser
from tkinter.ttk import *

#third party import
from PIL import Image, ImageTk

#custom libraries made by KATC14 give or take
#import custom.HoverInfo
#from custom import utilities
from custom import color_picker  # , menu


class map_editor():
	def __init__(self):
		self.root = tkinter.Tk()
		self.root.geometry("1280x720")
		self.root.title("test")
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)
		tkinter.Canvas.create_circle = self._create_circle

		# offset for x and y used in various places to position blips correctly and correct x, y gotten from canvas
		self.pos_number = (1600, 2400)
		self.map_image  = "maps/noih full map.jpg"
		self.map_txt    = "maps/default_data.txt"# around 2000 blips on screen at onces it starts getting framey
		self.config     = "config.json"

		self.delete_confirmation = self.toplevel_open = self.it_rectangle = self.guide_open = False
		#self.shift_held = False
		self.old = set()
		self.item_data = {}
		self.control_set = set()
		self.xs_var             = tkinter.IntVar()# x_spinbox
		self.ys_var             = tkinter.IntVar()# y_spinbox
		self.rs_var             = tkinter.IntVar()# r_spinbox
		self.item_var           = tkinter.Variable()# item selected
		self.name_var           = tkinter.StringVar()# name_entry
		self.type_var           = tkinter.StringVar()# type_entry
		self.raw_var            = tkinter.StringVar()# raw_entry

		self.bg_color    = '#65a8b1'

		# loads everything
		self.load_config('controls')
		self.load_config('colors')
		self.make_canvas()
		self.make_menu()
		self.make_map()
		self.make_other()
		self.draw_locations()
		print('amount of blips', len(self.item_data))

		self.selected_blip_menu  = 1
		self.new_blip_menu       = 2
		self.blip_place_menu     = 3
		self.blip_named_menu     = 4
		self.blip_menu           = 5
		self.blip_encounter_menu = 6
		self.blip_special_menu   = 7
		# default colors
		#selected_blip "#FF5500"
		#new_blip      "#0f0"
		#blip_place    "#f00"
		#blip_named    "#f0f"
		#blip          "#ff0"
		#blip_encounter"#0ff"
		#blip_special  "#00f"
		self.default_colors = {
			"selected_blip": {
				"default": "#FF5500",
				"menu": self.selected_blip_menu},
			"new_blip": {
				"default": "#0f0",
				"menu": self.new_blip_menu},
			"blip_place": {
				"default": "#f00",
				"menu": self.blip_place_menu},
	   		"blip_named": {
				"default": "#f0f",
				"menu": self.blip_named_menu},
			"blip": {
				"default": "#ff0",
				"menu": self.blip_menu},
			"blip_encounter": {
				"default": "#0ff",
				"menu": self.blip_encounter_menu},
			"blip_special": {
				"default": "#00f",
				"menu": self.blip_special_menu}}
		self.save_data = {"custom_color_picker": self.custom_color_picker, 'colors': self.blip_colors['colors'], 'controls': self.controls}

		self.blip_data = {
			'blip_place':     {'visibility': True, 'outline': True},
			'blip_named':     {'visibility': True, 'outline': True},
			'blip':           {'visibility': True, 'outline': True},
			'blip_encounter': {'visibility': True, 'outline': True},
			'blip_special':   {'visibility': True, 'outline': True}}


		self.root.mainloop()

	def json_load(self, file:str):
		with open(file, "r") as file:
			data = json.loads(file.read())
			#file.close()
			return data

	def json_save(self, json_file:str, data:dict|list):
		with open(json_file, "w") as file:
			json.dump(data, file, indent=4)

	def load_config(self, where, data=None):
		if not data:
			data = self.json_load(self.config)
			self.custom_color_picker = data['custom_color_picker']
		if where == 'controls':
			self.controls = data['controls']

			self.map_move_key   = self.controls['map_move']['key']
			self.map_motion_key = self.controls['map_move']['key_1']
			self.move_key       = self.controls['blip_move']['key']
			self.motion_key     = self.controls['blip_move']['key_1']
			self.edit_key       = self.controls['select']['key']
			self.shift_select   = self.controls['shift_select']['key']
			self.shift_move     = self.controls['shift_select']['key_1']
			self.control_select = self.controls['control_select']['key']

		elif where == 'colors':
			self.blip_colors = data
			blip_colors = data['colors']

			self.selected_blip_color  = blip_colors['selected_blip']['color']
			self.new_blip_color       = blip_colors['new_blip']['color']
			self.blip_place_color     = blip_colors['blip_place']['color']
			self.blip_named_color     = blip_colors['blip_named']['color']
			self.blip_color           = blip_colors['blip']['color']
			self.blip_encounter_color = blip_colors['blip_encounter']['color']
			self.blip_special_color   = blip_colors['blip_special']['color']

	def convert_keys(self, key):
		keys = {
			"<Button-1>":         "left click",
			"<Button-2>":         "middle click",
			"<Button-3>":         "right click",

			"<Shift-Button-1>":   "shift left click",
			"<Shift-Button-2>":   "shift middle click",
			"<Shift-Button-3>":   "shift right click",

			"<Control-Button-1>": "control left click",
			"<Control-Button-2>": "control middle click",
			"<Control-Button-3>": "control right click",

			"<Alt-Button-1>":     "alt left click",
			"<Alt-Button-2>":     "alt middle click",
			"<Alt-Button-3>":     "alt right click"
		}
		return keys[key]

	def guide(self):
		if not self.guide_open:
			self.guide_open = tkinter.Toplevel(self.root)
			self.guide_open.transient(self.root)

			Label(self.guide_open, text="you change the value of 'type, x, y, and radius' by using the scrollwheel").grid(sticky='nw', column=0, row=1, columnspan=2)
			Label(self.guide_open, text=f"{self.convert_keys(self.map_move_key)}", font='bold').grid(  sticky='nw', column=0, row=2)
			Label(self.guide_open, text=f"{self.convert_keys(self.move_key)}", font='bold').grid(      sticky='nw', column=0, row=3)
			Label(self.guide_open, text=f"{self.convert_keys(self.edit_key)}", font='bold').grid(      sticky='nw', column=0, row=4)
			Label(self.guide_open, text=f"{self.convert_keys(self.shift_select)}", font='bold').grid(  sticky='nw', column=0, row=5)
			Label(self.guide_open, text=f"{self.convert_keys(self.control_select)}", font='bold').grid(sticky='nw', column=0, row=6)

			Label(self.guide_open, text="drag to move map.").grid(               sticky='nw', column=1, row=2)
			Label(self.guide_open, text="drag to move blips.").grid(             sticky='nw', column=1, row=3)
			Label(self.guide_open, text="on blips for options.").grid(           sticky='nw', column=1, row=4)
			Label(self.guide_open, text="drag on canvas for multi select").grid( sticky='nw', column=1, row=5)
			Label(self.guide_open, text="click on blip to select multiple").grid(sticky='nw', column=1, row=6)

			self.root.wait_window(self.guide_open)
			self.guide_open = False

	def loadfile(self, filename):
		with open(filename, "r") as file:
			return file.read()

	def _create_circle(self, x, y, r, **kwargs):
		return self.canvas.create_oval(x, y, x+r, y+r, **kwargs)
		#return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

	def canvas_start(self, event):
		self.canvas.start_xy = (event.x, event.y)
		self.canvas.scan_mark(event.x, event.y)

	def canvas_end(self, event):
		self.canvas.scan_dragto(event.x, event.y, gain=1)

	# shift select
	def rectangle_start(self, event):
		if self.it_rectangle: self.canvas.delete(self.it_rectangle)
		self.item_var.set('')
		self.warning.config(text="WARNING")
		self.type_entry.config(state='disabled')
		self.delete_button.config(state='disabled')

		x0 = x1 = self.canvas.canvasx(event.x)
		y0 = y1 = self.canvas.canvasy(event.y)
		self.it_rectangle = self.canvas.create_rectangle(x0-10, y0-10, x1, y1, outline='black', width=2)
		self.reset_colors(self.canvas.find_all())

	def rectangle_end(self, event):
		self.delete_confirmation = False

		x, y, x1, y1 = self.canvas.coords(self.it_rectangle)
		temp = [i for i in self.canvas.find_overlapping(x, y, x1, y1)]
		self.item_var.set([i for i in temp if i != 1 and i != self.it_rectangle])

		x2, y2 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		self.canvas.coords(self.it_rectangle, x, y, x2, y2)

		self.name_entry.config(state='disabled')
		self.delete_button.config(state='normal', text='delete', activebackground='#f0f0f0', bg='#f0f0f0')
		self.x_spinbox.config(state='disabled')
		self.y_spinbox.config(state='disabled')
		self.r_spinbox.config(state='disabled')

		if len(self.item_var.get()) > 0:
			self.type_entry.config(state='readonly')
			text = f"WARNING {len(self.item_var.get())} blips selected"
		if len(self.item_var.get()) == 0:
			text = "WARNING"
			self.delete_button.config(state='disabled')
		self.warning.config(text=text)

		for i in self.item_var.get():
			if i != self.it_rectangle and i != 1:
				self.canvas.itemconfig(i, fill='#00d85a')

		set3 = set(self.old).difference(set(self.item_var.get()))
		self.old = self.item_var.get()
		self.reset_colors(set3)

	def item_select(self, event):
			x, y = event.x - self.canvas.start_xy[0], event.y - self.canvas.start_xy[1]
			current = self.canvas.find_withtag("current")[-1]

			if not self.item_var.get() or len(self.item_var.get()) == 1:
				self.canvas.move(current, x, y)
				# if statement: to fix a error where if you have a blip selected and move
				# another the moved blip would not save its coords
				self.save_coords(current, True if self.item_var.get() and self.item_var.get()[-1] != current else False)
			else:
				for i in self.item_var.get():
					self.canvas.move(i, x, y)
					self.save_coords(i, True)
			# keeps position updated with position of mouse
			self.canvas.start_xy = (event.x, event.y)

	def canvas_image(self, xy_coords, file):
		if not 'active_image_dict' in dir(self):
			self.active_image_dict = {}

		with Image.open(file) as img:
			pil_image = ImageTk.PhotoImage(img)
			canvas_image = self.canvas.create_image(xy_coords[0], xy_coords[1], image=pil_image, anchor='nw')
			# keeps the image from getting garbage collected
			self.active_image_dict.update({canvas_image: {"file": file, "image": pil_image}})
			return canvas_image, img

	def get_data(self, item):
		item_data = self.item_data[item]
		item_type = item_data['type']
		name = item_data['name']
		x, y, r = [i for i in item_data['size'].values()]
		return ((x, y, r), item_type, name)

	def motion(self, event):
		# keeps the hover from detecting the map image as a blip
		current = self.canvas.find_withtag("current")
		if current[-1] != 1 and current[-1] != self.it_rectangle:
			# gets the hovered blip
			(x, y, r), item_type, name = self.get_data(current[-1])
			# formats the data to conform to the map formatting
			raw = f'{x}|{y}|{r}|{item_type}|{name}'


			self.location.configure(text=f'name: {name}')
			self.raw_item.configure(text=raw)
		else:
			self.location.configure(text='name:')
			self.raw_item.configure(text='')

		# gets position of mouse cursor for easy positioning of blips
		x = int(self.canvas.canvasx(event.x)) + self.pos_number[0]
		y = int(self.canvas.canvasy(event.y)) + self.pos_number[1]
		#self.tooltip.strVar.set(f'x:{x}, y:{y}\nname: {name}\n{raw}')
		self.mouse.config(text=f'x:{x}, y:{y}')


	def label_configure(self, item):
		(x, y, r), item_type, name = self.get_data(item)
		self.xs_var.set(x)
		self.ys_var.set(y)
		self.raw_var.set(f'{x}|{y}|{r}|{item_type}|{name}')

	# loops over all items in canvas
	def compile_data(self):
		data = []
		for i in self.canvas.find_all():
			# make sure the item is in memory
			if i in self.item_data:
				(x, y, r), item_type, name = self.get_data(i)
				data.append(f'{x}|{y}|{r}|{item_type}|{name}')

		with open('new_map.txt', "w") as file:
			file.write(']['.join(data))

	def new_blip(self):
		x = int(self.canvas.canvasx(650))
		y = int(self.canvas.canvasy(300))
		r = 20

		item_type = 'blip'

		item = self.canvas.create_circle(x, y, r, fill=self.new_blip_color, outline="black", tag=item_type)

		self.canvas.tag_bind(item, self.edit_key, self.edit_blip)
		self.canvas.tag_bind(item, self.move_key, self.canvas_start)
		self.canvas.tag_bind(item, self.motion_key, self.item_select)
		self.canvas.tag_bind(item, self.control_select, self.ctrl_select)

		self.item_data.update({item:{'type': item_type, 'name': 'no_name', 'size':{'x': x+self.pos_number[0], 'y': y+self.pos_number[1], 'r': r}}})

		self.edit_blip(None, item)

	def change_colors(self, tag, menu_item):
		item = self.canvas.itemcget(tag, 'tag')
		if item: item = item.split()[-1]
		fill = self.blip_colors['colors'][tag]['color']

		if self.custom_color_picker:
			color = color_picker.askcolor(self.root, title='Pick a color', color=fill)
		else:
			color = tkinter.colorchooser.askcolor(title='Pick a color', color=fill)[1]

		# saves to memory and config file
		if color:
			self.blip_colors['colors'][tag]['color'] = color
			self.json_save(self.config, self.save_data)

			# changes menu background color
			self.menubar.winfo_children()[-1].winfo_children()[0].entryconfigure(menu_item, background=color)

			self.canvas.itemconfig(item, fill=color)
			self.canvas.itemconfig(self.item_var.get()[-1], fill=self.selected_blip_color)

	def blip_outlines(self, tag):
		outline = self.blip_data[tag]['outline']
		data, outline = (False, '') if outline else (True, 'black')

		self.blip_data[tag]['outline'] = data
		self.canvas.itemconfig(tag, outline=outline)

	def blip_visibility(self, tag):
		if tag == 'all':
			for i in self.blip_data:
				self.blip_visibility(i)
		else:
			visibility = self.blip_data[tag]['visibility']
			data, state = (False, 'hidden') if visibility else (True, 'normal')

			self.blip_data[tag]['visibility'] = data
			self.canvas.itemconfig(tag, state=state)

	def make_map(self):
		x1, y1 = (-self.pos_number[0], -self.pos_number[1])
		world_map = self.canvas_image((x1, y1), self.map_image)
		x2, y2 = world_map[1].size
		self.max_x, self.max_y = x2-26, y2-24


		self.canvas.configure(scrollregion=(x1, y1, x2+x1, y2+y1))
		# moves the visible area closer to the center of the map
		self.canvas.scan_dragto(100, -250, gain=1)

	def edit_name(self, args):
		name = args[2]

		# only allow spaces if its deleting
		if args[4] == ' ' and int(args[0]):
			return False

		for i in self.item_var.get():
			self.item_data[i]['name'] = name
			self.label_configure(i)

		return True

	def edit_coords(self, args) -> bool:
		if not args[2].isdigit():
			return False
		# checks if value is above max
		if int(args[2]) > self.max_x or int(args[2]) > self.max_y:
			return False
		# why does args return everything as a string?
		# have to use nametowidget to get the widget from the string
		# why the hell does cget return textvariable as a string...
		text_var = self.root.getvar(self.root.nametowidget(args[-1]).cget('textvariable'))
		new_coords = int(args[2])
		if text_var == self.xs_var.get(): self.move_blip(x=new_coords)
		if text_var == self.ys_var.get(): self.move_blip(y=new_coords)
		if text_var == self.rs_var.get(): self.move_blip(r=new_coords)
		return True

	def type_edit(self, event):
		text = event.widget.get()

		for i in self.item_var.get():
			self.item_data[i]['type'] = text
			self.canvas.itemconfig(i, tag=text)
			self.label_configure(i)

	# moves the blip from the spin boxes
	def move_blip(self, x=None, y=None, r=None):
		#(x, y, r), _, _ = self.get_data(item)
		if not x: x = self.xs_var.get()
		if not y: y = self.ys_var.get()
		if not r: r = self.rs_var.get()
		# remove offset because the x, y from the map file does not match the visual coords
		x = x-self.pos_number[0]
		y = y-self.pos_number[1]

		for i in self.item_var.get():
			self.canvas.coords(i, x, y, x+r, y+r)
			self.save_coords(i)

	def item_delete(self):
		self.delete_button.config(text='are you sure?', activebackground='#f00', bg='#f00')

		# confirmation you want to delete
		if self.delete_confirmation:
			self.xs_var.set('')
			self.ys_var.set('')
			self.rs_var.set('')
			self.name_var.set('')
			self.type_var.set('')
			self.raw_var.set('')

			self.name_entry.config(state='disabled')
			self.type_entry.config(state='disabled')
			self.delete_button.config(state='normal', text='delete', activebackground='#f0f0f0', bg='#f0f0f0')
			self.x_spinbox.config(state='disabled')
			self.y_spinbox.config(state='disabled')
			self.r_spinbox.config(state='disabled')
			self.warning.config(text="WARNING")

			for i in self.item_var.get():
				if i in self.item_data:
					self.canvas.delete(i)
					del self.item_data[i]
			self.canvas.delete(self.it_rectangle)

		self.delete_confirmation = True

	def ctrl_select(self, event):
		self.delete_confirmation = False
		state  = event.state
		item   = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))[-1]
		if self.it_rectangle:
			self.canvas.delete(self.it_rectangle)

		if item != 1:
			if state == 12:
				if isinstance(self.item_var.get(), str):
					self.control_set.add(item)
					self.item_var.set(tuple(self.control_set))

					text = "WARNING 1 blips selected"
				else:
					thing = set(self.item_var.get())
					if not item in thing:
						thing.add(item)
					else:
						thing.remove(item)
					self.item_var.set(tuple(thing))

					text = f"WARNING {len(self.item_var.get())} blips selected"

				self.type_entry.config(state='readonly')
				self.name_entry.config(state='disabled')
				self.x_spinbox.config(state='disabled')
				self.y_spinbox.config(state='disabled')
				self.r_spinbox.config(state='disabled')
				self.warning.config(text=text)
				for i in self.canvas.find_all():
					if str(i) in [str(x) for x in self.item_var.get()]:
						self.canvas.itemconfig(i, fill=self.selected_blip_color)
					else:
						self.reset_colors((i, ))
			else:
				self.control_set = set()

	def edit_blip(self, event, fake=False):
		self.control_set = set()
		self.reset_colors(self.canvas.find_all())
		if self.it_rectangle:
			self.canvas.delete(self.it_rectangle)

		# spoofing for adding a new blip
		if fake: item = fake
		else:    item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))[-1]

		self.name_entry.config(state='normal')
		self.type_entry.config(state='readonly')
		self.delete_button.config(state='normal', text='delete', activebackground='#f0f0f0', bg='#f0f0f0')
		self.x_spinbox.config(state='normal')
		self.y_spinbox.config(state='normal')
		self.r_spinbox.config(state='normal')
		self.warning.config(text="WARNING 1 blip selected")

		if item != 1:
			# changes delete confirmation back
			self.delete_confirmation = False

			(x, y, r), item_type, name = self.get_data(item)

			self.xs_var.set(x)
			self.ys_var.set(y)
			self.rs_var.set(r)
			self.item_var.set((item, ))
			self.name_var.set(name)
			self.type_var.set(item_type)
			self.raw_var.set(f'{x}|{y}|{r}|{item_type}|{name}')

			self.canvas.itemconfig(item, fill=self.selected_blip_color)

	def draw_locations(self):
		try:
			# tries to load map_txt if there is one
			map_file = self.loadfile(self.map_txt).replace('][', '\n')

			for i in map_file.split():
				x, y, r, item_type, name = i.replace('[', '').replace(']', '').split('|')# utilities.dict_replace(i, {'[':'', ']':''}).split('|')

				# need to float then int because its stored in a string and not using float first throws a ValueError
				x, y, r = [int(float(i)) for i in (x, y, r)]

				match item_type:
					case 'blip_place':     color = self.blip_place_color
					case 'blip_named':     color = self.blip_named_color
					case 'blip':           color = self.blip_color
					case 'blip_encounter': color = self.blip_encounter_color
					case 'blip_special':   color = self.blip_special_color
				item = self.canvas.create_circle(x + -self.pos_number[0], y + -self.pos_number[1], r, fill=color, outline="black", tags=item_type)

				self.item_data.update({item:{'type': item_type, 'name': name, 'size': {'x': x, 'y': y, 'r': r}}})


				self.canvas.tag_bind(item, self.edit_key, self.edit_blip)
				self.canvas.tag_bind(item, self.move_key, self.canvas_start)
				self.canvas.tag_bind(item, self.motion_key, self.item_select)
				self.canvas.tag_bind(item, self.control_select, self.ctrl_select)
		except Exception as e:
			print(e)
			print('no map text file')

	def make_menu(self):
		# built in tkinter menu
		self.menubar = tkinter.Menu(self.root, tearoff=0)
		option_menu = tkinter.Menu(self.menubar, tearoff=0)

		colors = tkinter.Menu(option_menu, tearoff=0)
		colors.add_command(label="Restore Defaults", command=self.set_default_colors)
		colors.add_command(label="selected blip",  background=self.selected_blip_color,  command=lambda: self.change_colors('selected_blip', self.selected_blip_menu))
		colors.add_command(label="new blip",       background=self.new_blip_color,       command=lambda: self.change_colors('new_blip', self.new_blip_menu))
		colors.add_command(label="blip place",     background=self.blip_place_color,     command=lambda: self.change_colors('blip_place', self.blip_place_menu))
		colors.add_command(label="blip named",     background=self.blip_named_color,     command=lambda: self.change_colors('blip', self.blip_named_menu))
		colors.add_command(label="blip",           background=self.blip_color,           command=lambda: self.change_colors('blip_encounter', self.blip_menu))
		colors.add_command(label="blip encounter", background=self.blip_encounter_color, command=lambda: self.change_colors('blip_special', self.blip_encounter_menu))
		colors.add_command(label="blip special",   background=self.blip_special_color,   command=lambda: self.change_colors('new_blip', self.blip_special_menu))
		option_menu.add_cascade(label="colors", menu=colors)

		blips = tkinter.Menu(option_menu, tearoff=0)
		blips.add_command(label="blip place",     command=lambda: self.blip_outlines('blip_place'))
		blips.add_command(label="blip named",     command=lambda: self.blip_outlines('blip_named'))
		blips.add_command(label="blip",           command=lambda: self.blip_outlines('blip'))
		blips.add_command(label="blip encounter", command=lambda: self.blip_outlines('blip_encounter'))
		blips.add_command(label="blip special",   command=lambda: self.blip_outlines('blip_special'))
		option_menu.add_cascade(label="outlines", menu=blips)

		blips = tkinter.Menu(option_menu, tearoff=0)
		blips.add_command(label="all",     command=lambda: self.blip_visibility('all'))
		blips.add_command(label="blip place",     command=lambda: self.blip_visibility('blip_place'))
		blips.add_command(label="blip named",     command=lambda: self.blip_visibility('blip_named'))
		blips.add_command(label="blip",           command=lambda: self.blip_visibility('blip'))
		blips.add_command(label="blip encounter", command=lambda: self.blip_visibility('blip_encounter'))
		blips.add_command(label="blip special",   command=lambda: self.blip_visibility('blip_special'))
		option_menu.add_cascade(label="hide blips", menu=blips)

		self.menubar.add_cascade(label="options", menu=option_menu)
		self.menubar.add_command(label="how to use",  command=self.guide)
		self.menubar.add_command(label="compile map", command=self.compile_data)
		self.menubar.add_command(label="new blip",    command=self.new_blip)

		self.root.config(menu=self.menubar)

	def set_default_colors(self):
		for tag, data in self.default_colors.items():
			color = data['default']
			self.blip_colors['colors'][tag]['color'] = color
			self.canvas.itemconfig(tag, fill=color)
			self.menubar.winfo_children()[-1].winfo_children()[0].entryconfigure(data['menu'], background=color)

		self.load_config('colors', self.blip_colors)
		self.json_save(self.config, self.save_data)

	def make_other(self):
		vcmd  = (self.root.register(lambda *args: self.edit_name(args)), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		vcmd1 = (self.root.register(lambda *args: self.edit_coords(args)), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

		frame         = tkinter.Frame(self.root, borderwidth=2)
		container     = tkinter.LabelFrame(frame, text='hovered blip', labelanchor='nw', borderwidth=2)
		self.mouse    = Label(container, text="x:none, y:none")
		self.location = Label(container, text="name: ")
		self.raw_item = Label(container, text="")

		self.mouse.grid(   sticky='SW', column=0, row=0)
		self.location.grid(sticky='SW', column=0, row=1)
		self.raw_item.grid(sticky='SW', column=0, row=3)
		frame.grid(        sticky='nw', column=0, row=3)
		container.grid(    sticky='nw', column=0, row=0)

		container1 = tkinter.LabelFrame(self.root, text='selected blip', labelanchor='n', borderwidth=2)
		name_label         = Label(   container1, text='name')
		type_label         = Label(   container1, text='type')
		self.name_entry    = Entry(   container1, state='disabled', width=20, textvariable=self.name_var, validate='key', validatecommand=vcmd)
		self.type_entry    = Combobox(container1, state='disabled', width=14, textvariable=self.type_var, values=('blip', 'blip_encounter', 'blip_special', 'blip_place', 'blip_named'))

		self.warning       = tkinter.LabelFrame(container1, text='WARNING', labelanchor='n', borderwidth=2, relief='sunken', fg='#f00')
		self.delete_button = tkinter.Button(self.warning, text="delete", state='disabled', command=self.item_delete)

		raw_entry      = Entry(  container1, width=50, textvariable=self.raw_var, validate='key', validatecommand=(self.root.register(lambda *_: False), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))

		x_label        = Label(  container1, text="x")
		y_label        = Label(  container1, text="y")
		r_label        = Label(  container1, text="radius")
		self.x_spinbox = Spinbox(container1, state='disabled', validate='key', validatecommand=vcmd1, from_=0, to=self.max_x+4,    width=15, textvariable=self.xs_var, command=self.move_blip)
		self.y_spinbox = Spinbox(container1, state='disabled', validate='key', validatecommand=vcmd1, from_=0, to=self.max_y+2, width=15, textvariable=self.ys_var, command=self.move_blip)
		self.r_spinbox = Spinbox(container1, state='disabled', validate='key', validatecommand=vcmd1, from_=0, to=2147483647,    width=15, textvariable=self.rs_var, command=self.move_blip)
		#self.xs_var.trace_add("write", lambda name, index, mode, sv=self.xs_var: print(sv))
		#self.ys_var.trace_add("write", lambda name, index, mode, sv=self.ys_var: print(sv))
		#self.rs_var.trace_add("write", lambda name, index, mode, sv=self.rs_var: print(sv))

		self.type_entry.bind("<<ComboboxSelected>>", self.type_edit)
		self.canvas.bind(self.shift_select, self.rectangle_start, True)
		self.canvas.bind(self.shift_move,   self.rectangle_end, True)


		container1.grid(        sticky='ne', column=2, row=2, rowspan=6)
		name_label.grid(        sticky='ne', column=2, row=1)
		type_label.grid(        sticky='nw', column=0, row=1)
		self.name_entry.grid(   sticky='nw', column=3, row=1)
		self.type_entry.grid(   sticky='nw', column=1, row=1)

		self.warning.grid(      sticky='nw', column=2, row=3, rowspan=2, columnspan=2)
		self.delete_button.grid(sticky='nw', column=1, row=0)

		raw_entry.grid(         sticky='nw', column=0, row=0, columnspan=10)

		x_label.grid(           sticky='nw', column=0, row=3)
		y_label.grid(           sticky='nw', column=0, row=4)
		r_label.grid(           sticky='nw', column=0, row=5)
		self.x_spinbox.grid(    sticky='nw', column=1, row=3)
		self.y_spinbox.grid(    sticky='nw', column=1, row=4)
		self.r_spinbox.grid(    sticky='nw', column=1, row=5)

	def reset_colors(self, items):
		for i in items:
			tag = self.canvas.itemcget(i, 'tag').split()
			if tag and tag[0] != 'current':
				self.canvas.itemconfig(i, fill=self.blip_colors['colors'][tag[0]]['color'])

	# draws the entire canvas
	def make_canvas(self):
		self.canvas = tkinter.Canvas(self.root, width=400, height=400, background=self.bg_color)
		self.canvas.configure(scrollregion=(0, 0, self.root.winfo_width(), self.root.winfo_height()))
		self.canvas.grid(row=0, column=0, sticky="nsew", columnspan=100)

		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		#self.tooltip = custom.HoverInfo.Tooltip(self.canvas, bg='white', textvar=True, move_with_cursor=True)
		self.canvas.bind('<Motion>', self.motion, True)
		self.canvas.bind(self.map_move_key,   self.canvas_start)
		self.canvas.bind(self.map_motion_key, self.canvas_end)

	# save the x y r to the item_data
	def save_coords(self, item, only_selected=False):
		x, y, x1, _ = [int(i) for i in self.canvas.coords(item)]
		r = x1-x # calculates the radius of the blip
		x += self.pos_number[0]
		y += self.pos_number[1]
		#location = self.canvas.itemcget(tag, 'tag').split()[0]
		self.item_data[item]['size'].update({'x': x, 'y': y, 'r': r})

		if not only_selected:
			self.label_configure(item)

if __name__ == "__main__":
	map_editor()
