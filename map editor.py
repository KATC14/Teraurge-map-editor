import json
import tkinter
import tkinter.colorchooser
from tkinter.ttk import *

#third party import
from PIL import Image, ImageTk

#custom libraries made by KATC14 give or take
#import custom.HoverInfo
#from custom import utilities
from custom import color_picker, menu


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

		self.delete_confirmation = self.toplevel_open = False
		self.active_image_dict, self.item_data = {}, {}
		self.xs_var          = tkinter.IntVar()# x_spinbox
		self.ys_var          = tkinter.IntVar()# y_spinbox
		self.rs_var          = tkinter.IntVar()# r_spinbox
		self.item_var        = tkinter.IntVar()# item selected
		self.name_var        = tkinter.StringVar()# name_entry
		self.type_var        = tkinter.StringVar()# type_entry
		self.raw_var         = tkinter.StringVar()# raw_entry
		self.map_move_var    = tkinter.StringVar()# map_move
		self.move_blip_var   = tkinter.StringVar()# move_blip
		self.select_blip_var = tkinter.StringVar()# select_blip

		self.bg_color    = '#65a8b1'

		# default controls
		self.default_map_move_key   = '<Button-1>'  # left mouse
		self.default_map_motion_key = '<B1-Motion>' # left mouse motion
		self.default_edit_key       = '<Button-1>'  # left mouse
		self.default_move_key       = '<Button-3>'  # right mouse
		self.default_motion_key     = '<B3-Motion>' # right mouse motion

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

		self.blip_data = {
			'selected_blip':  {'visibility': True, 'outline': True},
			'new_blip':       {'visibility': True, 'outline': True},
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
			data             = self.json_load(self.config)
			self.custom_menu = data['custom_menu']
			self.custom_color_picker = data['custom_color_picker']
		if where == 'controls':
			self.controls = data
			controls = data['controls']

			self.map_move_key   = controls['map_move']['key']
			self.map_motion_key = controls['map_move_to']['key']
			self.move_key       = controls['move']['key']
			self.edit_key       = controls['select']['key']
			self.motion_key     = controls['move_to']['key']

			self.map_move_var.set(self.convert_keys(self.map_move_key))
			self.move_blip_var.set(self.convert_keys(self.move_key))
			self.select_blip_var.set(self.convert_keys(self.edit_key))

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

	def toplevel_close(self, top):
		self.toplevel_open = False
		#print(len(self.canvas.find_all()))
		top.destroy()

	def make_toplevel(self):
		top = tkinter.Toplevel(self.root)
		top.transient(self.root)
		top.protocol("WM_DELETE_WINDOW", lambda: self.toplevel_close(top))
		return top

	def convert_keys(self, key):
		keys = {
			"<Button-1>": "left mouse",
			"<Button-2>": "middle mouse",
			"<Button-3>": "right mouse"
		}
		return keys[key]

	def guide(self, event=None):
		if not self.toplevel_open:
			self.toplevel_open = True
			top = self.make_toplevel()

			Label(top, text="custom menu and custom color picker are experimental use at your own risk\n").grid(sticky='nw', column=0, row=0)
			Label(top, text=f"{self.convert_keys(self.map_move_key)} drag to move map.").grid(sticky='nw', column=0, row=1)
			Label(top, text=f"{self.convert_keys(self.move_key)} drag to move blips.").grid(sticky='nw', column=0, row=2)
			Label(top, text=f"{self.convert_keys(self.edit_key)} on blips for options.").grid(sticky='nw', column=0, row=3)
			Label(top, text="you change the value of 'type, x, y, and radius' by using the scrollwheel").grid(sticky='nw', column=0, row=4)

	def loadfile(self, filename):
		with open(filename, "r") as file:
			return file.read()

	def _create_circle(self, x, y, r, **kwargs):
		return self.canvas.create_oval(x, y, x+r, y+r, **kwargs)
		#return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

	#move
	def move_start(self, event):
		self.canvas.start_xy = (event.x, event.y)
		self.canvas.scan_mark(event.x, event.y)

	def move_to(self, event):
		self.canvas.scan_dragto(event.x, event.y, gain=1)

	def item_move(self, event):
		current = self.canvas.find_withtag("current")[-1]
		x, y = event.x-self.canvas.start_xy[0], event.y-self.canvas.start_xy[1]
		self.canvas.move(current, x, y)
		self.canvas.start_xy = (event.x, event.y)

		# if statement: to fix a error where if you have a blip selected and move another
		# the moved blip would not save its coords
		self.save_coords(current, True if self.item_var.get() != current else False)

	def canvas_image(self, xy_coords, file):
		with Image.open(file) as img:
			pil_image = ImageTk.PhotoImage(img)
			canvas_image = self.canvas.create_image(xy_coords[0], xy_coords[1], image=pil_image, anchor='nw')
			# keeps the image from getting garbage collected
			self.active_image_dict.update({file: {"item": canvas_image, "image": pil_image}})
			return canvas_image, img

	def get_data(self, item):
		item_data = self.item_data[item]
		item_type = item_data['type']
		name = item_data['name']
		x, y, r = [i for i in item_data['size'].values()]
		return ((x, y, r), item_type, name)

	def motion(self, event=None):
		# keeps the hover from detecting the map image as a blip
		#name = raw = None
		current = self.canvas.gettags("current")
		if current and current[0] != 'current':
			# gets the hovered blip
			current = self.canvas.find_withtag("current")[-1]
			(x, y, r), item_type, name = self.get_data(current)
			# formats the data to conform to the map formatting
			raw = f'{x}|{y}|{r}|{item_type}|{name}'


			self.location.configure(text=f'name: {name}')
			self.raw_item.configure(text=raw)
		else:
			self.location.configure(text='name:')
			self.raw_item.configure(text='')

		# gets position of mouse cursor for easy positioning of blips
		x = int(self.canvas.canvasx(event.x))+self.pos_number[0]
		y = int(self.canvas.canvasy(event.y))+self.pos_number[1]
		#self.tooltip.strVar.set(f'x:{x}, y:{y}\nname: {name}\n{raw}')
		self.mouse.config(text=f'x:{x}, y:{y}')


	def label_configure(self, item):
		(x, y, r), item_type, name = self.get_data(item)
		#print('L', x, y, r)
		self.xs_var.set(x)
		self.ys_var.set(y)
		self.raw_var.set(f'{x}|{y}|{r}|{item_type}|{name}')

	# loops over all items in canvas
	def compile_data(self, event=None):
		#print(event)
		data = []
		for i in self.canvas.find_all():
			# make sure the item is in memory
			if i in self.item_data:
				(x, y, r), item_type, name = self.get_data(i)
				data.append(f'{x}|{y}|{r}|{item_type}|{name}')

		with open('new_map.txt', "w") as file:
			file.write(']['.join(data))

	def new_blip(self, event=None):
		x = int(self.canvas.canvasx(650))
		y = int(self.canvas.canvasy(300))
		r = 20

		item_type = 'blip'

		item = self.canvas.create_circle(x, y, r, fill=self.new_blip_color, outline="black", tag=item_type)
		self.canvas.addtag_withtag('new_blip', item)

		self.canvas.tag_bind(item, self.edit_key, self.edit_blip)
		self.canvas.tag_bind(item, self.move_key, self.move_start)
		self.canvas.tag_bind(item, self.motion_key, self.item_move)

		self.item_data.update({item:{'type': item_type, 'name': 'no_name', 'size':{'x': x+self.pos_number[0], 'y': y+self.pos_number[1], 'r': r}}})

		self.edit_blip(item, True)

	def change_colors(self, event, menu_item=None):
		if self.custom_menu:
			item  = event.widget.cget('text').replace(' ', '_')
			fill = event.widget.master.color_old
		else:
			item = self.canvas.itemcget(event, 'tag')
			if item: item = item.split()[-1]
			fill = self.blip_colors['colors'][event]['color']

		if self.custom_color_picker:
			color = color_picker.askcolor(self.root, title='Pick a color', color=fill)
		else:
			color = tkinter.colorchooser.askcolor(title='Pick a color', color=fill)[1]

		# saves to memory and config file
		if color:
			self.blip_colors['colors'][event]['color'] = color
			self.json_save(self.config, {"custom_menu": self.custom_menu, "custom_color_picker": self.custom_color_picker, 'colors': self.blip_colors['colors'], 'controls': self.controls['controls']})

			# changes menu background color
			if self.custom_menu:
				event.widget.config(background=color)
			else:
				self.menubar.winfo_children()[-1].winfo_children()[0].entryconfigure(menu_item, background=color)

			self.canvas.itemconfig(item, fill=color)
			# keeps the 'new_blip' from being grouped into 'blip' because thay have the same type
			self.canvas.itemconfig(self.item_var.get(), fill=self.selected_blip_color)
			self.canvas.itemconfig('new_blip', fill=self.new_blip_color)

	def blip_outlines(self, event=None):
		if self.custom_menu:
			tag = event.widget.cget('text').replace(' ', '_')
		else:
			tag = event

		outline = self.blip_data[tag]['outline']
		if  outline: self.blip_data[tag]['outline'], outline = False, ''
		else:        self.blip_data[tag]['outline'], outline = True, 'black'

		self.canvas.itemconfig(tag, outline=outline)

	def blip_visibility(self, event=None):
		if self.custom_menu:
			tag = event.widget.cget('text').replace(' ', '_')
		else:
			tag = event

		visibility = self.blip_data[tag]['visibility']
		if  visibility: self.blip_data[tag]['visibility'], state = False, 'hidden'
		else:           self.blip_data[tag]['visibility'], state = True, 'normal'

		self.canvas.itemconfig(tag, state=state)

	def make_map(self):
		x1, y1 = (-self.pos_number[0], -self.pos_number[1])
		world_map = self.canvas_image((x1, y1), self.map_image)
		x2, y2 = world_map[1].size
		self.max_x, self.max_y = x2, y2


		self.canvas.configure(scrollregion=(x1, y1, x2+x1, y2+y1))
		# moves the visible area closer to the center of the map
		self.canvas.scan_dragto(100, -250, gain=1)

	def edit_name(self, args):
		item = self.item_var.get()
		name = args[2]

		# only allow spaces if its deleting
		if args[4] == ' ' and int(args[0]):
			return False

		self.item_data[item]['name'] = name
		self.label_configure(item)

		return True

	def edit_coords(self, args) -> bool:
		print(args)
		if not args[4].isdigit() or not args[2].isdigit():
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
		item = self.item_var.get()
		text = event.widget.get()

		self.item_data[item]['type'] = text
		self.canvas.itemconfig(item, tag=text)
		self.label_configure(item)

	# moves the blip from the spin boxes
	def move_blip(self, x=None, y=None, r=None):
		item = self.item_var.get()
		#(x, y, r), _, _ = self.get_data(item)
		if not x: x = self.xs_var.get()
		if not y: y = self.ys_var.get()
		if not r: r = self.rs_var.get()
		# remove offset because the x, y from the map file does not match the visual coords
		x = x-self.pos_number[0]
		y = y-self.pos_number[1]

		self.canvas.coords(item, x, y, x+r, y+r)
		self.save_coords(item)

	def item_delete(self):
		item = self.item_var.get()
		button = self.blip_editables[1]
		button.config(text='are you sure?', activebackground='#f00', bg='#f00')

		# confirmation you want to delete
		if self.delete_confirmation:
			self.xs_var.set('')
			self.ys_var.set('')
			self.rs_var.set('')
			self.name_var.set('')
			self.type_var.set('')
			self.raw_var.set('')

			[i.config(state='disabled') for i in self.blip_editables]
			button.config(text='delete', activebackground='#f0f0f0', bg='#f0f0f0')
			self.canvas.delete(item)
			del self.item_data[item]

		self.delete_confirmation = True

	def edit_blip(self, event, fake=False):
		# spoofing for adding a new blip
		if fake: item = event
		else:    item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))[-1]

		[x.config(state='readonly' if i == 2 else 'normal') for i, x in enumerate(self.blip_editables)]
		#self.this_test[1].config(state=)
		# get last blip selected
		temp = self.item_var.get()
		tag = self.canvas.itemcget(temp, 'tag').split()
		if temp and tag and tag[-1] != 'current':
			# gets color of blips of the same tag to remove the selection color
			self.canvas.itemconfig(temp, fill=self.blip_colors['colors'][tag[-1]]['color'])

		if item != 1:
			# changes delete confirmation back
			self.delete_confirmation = False
			self.blip_editables[1].config(text='delete', activebackground='#f0f0f0', bg='#f0f0f0')

			(x, y, r), item_type, name = self.get_data(item)

			self.xs_var.set(x)
			self.ys_var.set(y)
			self.rs_var.set(r)
			self.item_var.set(item)
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
				self.canvas.tag_bind(item, self.move_key, self.move_start)
				self.canvas.tag_bind(item, self.motion_key, self.item_move)
		except:
			print('no map text file')

	def toggle_menus(self, where, menu):
		if   menu == 'custom':
			if where == 'menu':
				self.custom_menu = True
			elif where == 'color_picker':
				self.custom_color_picker = True
		elif menu == 'native':
			if where == 'menu':
				self.custom_menu = False
			elif where == 'color_picker':
				self.custom_color_picker = False

		self.json_save(self.config, {"custom_menu": self.custom_menu, "custom_color_picker": self.custom_color_picker, 'colors': self.blip_colors['colors'], 'controls': self.controls['controls']})

	def make_menu(self):
		if self.custom_menu:
			# custom menu recreation
			self.menubar = menu.MainMenu(self.root)

			option_menu = menu.MainMenu(self.menubar)
			option_menu.add_command(label="toggle to native menu (needs restart)", command=lambda: self.toggle_menus('menu', 'native'))
			option_menu.add_command(label="toggle to native color picker", command=lambda: self.toggle_menus('color_picker', 'native'))
			option_menu.add_command(label="controls", command=self.change_controls)

			colors = menu.MainMenu(option_menu)
			colors.add_command(label="Restore Defaults", command=self.set_default_colors)
			self.selected_blip_menu  = colors.add_command(label="selected blip",  background=self.selected_blip_color,  command=self.change_colors)
			self.new_blip_menu       = colors.add_command(label="new blip",       background=self.new_blip_color,       command=self.change_colors)
			self.blip_place_menu     = colors.add_command(label="blip place",     background=self.blip_place_color,     command=self.change_colors)
			self.blip_named_menu     = colors.add_command(label="blip named",     background=self.blip_named_color,     command=self.change_colors)
			self.blip_menu           = colors.add_command(label="blip",           background=self.blip_color,           command=self.change_colors)
			self.blip_encounter_menu = colors.add_command(label="blip encounter", background=self.blip_encounter_color, command=self.change_colors)
			self.blip_special_menu   = colors.add_command(label="blip special",   background=self.blip_special_color,   command=self.change_colors)
			option_menu.add_cascade(label="colors", menu=colors)

			blips = menu.MainMenu(option_menu)
			blips.add_command(label="blip place",     command=self.blip_outlines)
			blips.add_command(label="blip named",     command=self.blip_outlines)
			blips.add_command(label="blip",           command=self.blip_outlines)
			blips.add_command(label="blip encounter", command=self.blip_outlines)
			blips.add_command(label="blip special",   command=self.blip_outlines)
			option_menu.add_cascade(label="outlines", menu=blips)

			blips = menu.MainMenu(option_menu)
			blips.add_command(label="blip place",     command=self.blip_visibility)
			blips.add_command(label="blip named",     command=self.blip_visibility)
			blips.add_command(label="blip",           command=self.blip_visibility)
			blips.add_command(label="blip encounter", command=self.blip_visibility)
			blips.add_command(label="blip special",   command=self.blip_visibility)
			option_menu.add_cascade(label="hide blips", menu=blips)

			self.menubar.add_cascade(label="options", menu=option_menu)
			self.menubar.add_command(label="how to use",  command=self.guide)
			self.menubar.add_command(label="compile map", command=self.compile_data)
			self.menubar.add_command(label="new blip",    command=self.new_blip)
		else:
			# built in tkinter menu
			self.menubar = tkinter.Menu(self.root, tearoff=0)

			option_menu = tkinter.Menu(self.menubar, tearoff=0)
			option_menu.add_command(label="toggle to custom menu (needs restart)", command=lambda: self.toggle_menus('menu', 'custom'))
			option_menu.add_command(label="toggle to custom color picker", command=lambda: self.toggle_menus('color_picker', 'custom'))
			option_menu.add_command(label="controls", command=self.change_controls)

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

	def combo_edit(self, event, where):
		match event.widget.get():
			case 'left mouse':
				key        = '<Button-1>'
				motion_aug = '<B1-Motion>'
			case 'middle mouse':
				key        = '<Button-2>'
				motion_aug = '<B2-Motion>'
			case 'right mouse':
				key        = '<Button-3>'
				motion_aug = '<B3-Motion>'

		# unbind all sequences
		if where in ('select_blip', 'move_blip'):
			for i in ('<Button-1>', '<Button-2>', '<Button-3>', '<B3-Motion>'):
				for x in self.canvas.find_all():
					self.canvas.tag_unbind(x, i)
		else:
			for i in ('<Button-1>', '<B1-Motion>', '<Button-2>', '<B2-Motion>', '<Button-2>', '<B2-Motion>'):
				self.canvas.unbind(i)

		# bind new sequences
		match where:
			case 'map_move':
				self.canvas.bind(self.move_key, self.move_start, True)
				self.canvas.bind(self.motion_key, self.move_to, True)

				self.controls['controls']['map_move']['key']    = key
				self.controls['controls']['map_move_to']['key'] = motion_aug
			case 'move_blip':
				self.controls['controls']['move']['key']        = key
				self.controls['controls']['move_to']['key']     = motion_aug
			case 'select_blip':
				self.controls['controls']['select']['key']      = key
		self.load_config('controls', self.controls)

		if where != 'map_move':
			for i in self.canvas.find_all():
				if i != 1:
					self.canvas.tag_bind(i, self.edit_key, self.edit_blip, True)
					self.canvas.tag_bind(i, self.move_key, self.move_start, True)
					self.canvas.tag_bind(i, self.motion_key, self.item_move, True)

		# saves to config file
		self.json_save(self.config, {"custom_menu": self.custom_menu, "custom_color_picker": self.custom_color_picker, 'colors': self.blip_colors['colors'], 'controls': self.controls['controls']})

	def default_controls(self):
		# unbind all sequences
		for i in ('<Button-1>', '<B1-Motion>', '<Button-2>', '<B2-Motion>', '<Button-3>', '<B3-Motion>'):
			for x in self.canvas.find_all():
				self.canvas.tag_unbind(x, i)
		for i in ('<Button-1>', '<B1-Motion>', '<Button-2>', '<B2-Motion>', '<Button-3>', '<B3-Motion>'):
			self.canvas.unbind(i)

		# bind all sequences to default
		self.canvas.bind(self.default_map_move_key, self.move_start)
		self.canvas.bind(self.default_map_motion_key, self.move_to)
		for i in self.canvas.find_all():
			if i != 1:
				self.canvas.tag_bind(i, self.default_edit_key, self.edit_blip)
				self.canvas.tag_bind(i, self.default_move_key, self.move_start)
				self.canvas.tag_bind(i, self.default_motion_key, self.item_move)

		# changes user keys back to default and saves to config file
		a = {
			"map_move": self.default_map_move_key, "map_move_to": self.default_map_motion_key,
	   		"move": self.default_move_key, "move_to": self.default_motion_key, "select": self.default_edit_key
		}
		for func, key in a.items():
			self.controls['controls'][func]['key'] = key
		self.load_config('controls', self.controls)
		self.json_save(self.config, {"custom_menu": self.custom_menu, "custom_color_picker": self.custom_color_picker, 'colors': self.blip_colors['colors'], 'controls': self.controls['controls']})

	def change_controls(self, event=None):
		# how to rebind?
		if not self.toplevel_open:
			self.toplevel_open = True
			top = self.make_toplevel()
			set_defaults = tkinter.Button(top, text="default controls", command=self.default_controls)

			map_move_label    = Label(   top, text='move map')
			move_blip_label   = Label(   top, text='move blip')
			select_blip_label = Label(   top, text='select blip')
			map_move          = Combobox(top, state='readonly', textvariable=self.map_move_var, values=('left mouse', 'middle mouse', 'right mouse'))
			move_blip         = Combobox(top, state='readonly', textvariable=self.move_blip_var, values=('left mouse', 'middle mouse', 'right mouse'))
			select_blip       = Combobox(top, state='readonly', textvariable=self.select_blip_var, values=('left mouse', 'middle mouse', 'right mouse'))

			self.map_move_var.set(   self.convert_keys(self.map_move_key))
			self.move_blip_var.set(  self.convert_keys(self.move_key))
			self.select_blip_var.set(self.convert_keys(self.edit_key))
			map_move.bind(   "<<ComboboxSelected>>", lambda e: self.combo_edit(e, 'map_move'))
			move_blip.bind(  "<<ComboboxSelected>>", lambda e: self.combo_edit(e, 'move_blip'))
			select_blip.bind("<<ComboboxSelected>>", lambda e: self.combo_edit(e, 'select_blip'))

			set_defaults.grid(     sticky='nw', column=1, row=0)

			map_move_label.grid(   sticky='ne', column=0, row=1)
			move_blip_label.grid(  sticky='ne', column=0, row=2)
			select_blip_label.grid(sticky='ne', column=0, row=3)
			map_move.grid(         sticky='nw', column=1, row=1)
			move_blip.grid(        sticky='nw', column=1, row=2)
			select_blip.grid(      sticky='nw', column=1, row=3)

	def set_default_colors(self, event=None):
		for tag, data in self.default_colors.items():
			color = data['default']
			self.blip_colors['colors'][tag]['color'] = color
			self.canvas.itemconfig(tag, fill=color)
			if self.custom_menu:
				data['menu'].config(background=color)
			else:
				self.menubar.winfo_children()[-1].winfo_children()[0].entryconfigure(data['menu'], background=color)

		self.load_config('colors', self.blip_colors)
		self.json_save(self.config, {"custom_menu": self.custom_menu, "custom_color_picker": self.custom_color_picker, 'colors': self.blip_colors['colors'], 'controls': self.controls['controls']})

	def make_other(self):
		vcmd  = (self.root.register(lambda *args: self.edit_name(args)), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		vcmd1 = (self.root.register(lambda *args: self.edit_coords(args)), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

		container     = tkinter.LabelFrame(self.root, text='hovered blip', labelanchor='nw', borderwidth=2)
		self.mouse    = Label(container, text="x:none, y:none")
		self.location = Label(container, text="name: ")
		#self.formatted_item = Label(container, text="{}")
		self.raw_item = Label(container, text="")

		self.mouse.grid(   sticky='SW', column=0, row=0)
		self.location.grid(sticky='SW', column=0, row=1)
		#self.formatted_item.grid(sticky='SW', column=0, row=2)
		self.raw_item.grid(sticky='SW', column=0, row=3)
		container.grid(    sticky='nw', column=0, row=2)

		container1    = tkinter.LabelFrame(self.root, text='selected blip', labelanchor='n', borderwidth=2)
		name_label    = Label(   container1, text='name')
		type_label    = Label(   container1, text='type')
		name_entry    = Entry(   container1, state='disabled', width=20, textvariable=self.name_var, validate='key', validatecommand=vcmd)
		type_entry    = Combobox(container1, state='disabled', width=14, textvariable=self.type_var, values=('blip', 'blip_encounter', 'blip_special', 'blip_place', 'blip_named'))

		warning       = tkinter.LabelFrame(container1, text='WARNING', labelanchor='n', borderwidth=2, relief='sunken', fg='#f00')
		delete_button = tkinter.Button(warning, text="delete", state='disabled', command=self.item_delete)

		raw_entry     = Entry(  container1, width=50, textvariable=self.raw_var, validate='key', validatecommand=(self.root.register(lambda *_: False), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))

		x_label       = Label(  container1, text="x")
		y_label       = Label(  container1, text="y")
		r_label       = Label(  container1, text="radius")
		x_spinbox     = Spinbox(container1, state='disabled', validate='key', validatecommand=vcmd1, from_=0, to=self.max_x,    width=15, textvariable=self.xs_var, command=self.move_blip)
		y_spinbox     = Spinbox(container1, state='disabled', validate='key', validatecommand=vcmd1, from_=0, to=self.max_y+20, width=15, textvariable=self.ys_var, command=self.move_blip)
		r_spinbox     = Spinbox(container1, state='disabled', validate='key', validatecommand=vcmd1, from_=0, to=2147483647,    width=15, textvariable=self.rs_var, command=self.move_blip)
		#self.xs_var.trace_add("write", lambda name, index, mode, sv=self.xs_var: print(sv))
		#self.ys_var.trace_add("write", lambda name, index, mode, sv=self.ys_var: print(sv))
		#self.rs_var.trace_add("write", lambda name, index, mode, sv=self.rs_var: print(sv))

		type_entry.bind("<<ComboboxSelected>>", self.type_edit)

		container1.grid(   sticky='ne', column=0, row=2, rowspan=6)
		name_label.grid(   sticky='ne', column=2, row=1)
		type_label.grid(   sticky='nw', column=0, row=1)
		name_entry.grid(   sticky='nw', column=3, row=1)
		type_entry.grid(   sticky='nw', column=1, row=1)

		warning.grid(      sticky='nw', column=2, row=3, rowspan=2, columnspan=2)
		delete_button.grid(sticky='nw', column=1, row=0)

		raw_entry.grid(    sticky='nw', column=0, row=0, columnspan=10)

		x_label.grid(      sticky='nw', column=0, row=3)
		y_label.grid(      sticky='nw', column=0, row=4)
		r_label.grid(      sticky='nw', column=0, row=5)
		x_spinbox.grid(    sticky='nw', column=1, row=3)
		y_spinbox.grid(    sticky='nw', column=1, row=4)
		r_spinbox.grid(    sticky='nw', column=1, row=5)
		self.blip_editables = (name_entry, delete_button, type_entry, x_spinbox, y_spinbox, r_spinbox)

	# draws the entire canvas
	def make_canvas(self):
		self.canvas = tkinter.Canvas(self.root, width=400, height=400, background=self.bg_color)
		self.canvas.configure(scrollregion=(0, 0, self.root.winfo_width(), self.root.winfo_height()))
		self.canvas.grid(row=0, column=0, sticky="nsew", columnspan=2)

		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		#self.tooltip = custom.HoverInfo.Tooltip(self.canvas, bg='white', textvar=True, move_with_cursor=True)
		self.canvas.bind('<Motion>', self.motion, True)
		self.canvas.bind(self.map_move_key, self.move_start)
		self.canvas.bind(self.map_motion_key, self.move_to)

	# save the x y r to the item_data
	def save_coords(self, item, only_selected=False):
		x, y, x1, _ = [int(i) for i in self.canvas.coords(item)]
		#print('a', x, y, x1)
		r = x1-x # calculates the radius of the blip
		x += self.pos_number[0]
		y += self.pos_number[1]
		#location = self.canvas.itemcget(tag, 'tag').split()[0]
		self.item_data[item]['size'].update({'x': x, 'y': y, 'r': r})

		if not only_selected:
			self.label_configure(item)

if __name__ == "__main__":
	map_editor()
