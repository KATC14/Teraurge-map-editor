import tkinter
#import tkinter.colorchooser
from tkinter.ttk import *


class pick(tkinter.Toplevel):
	def __init__(self, parent=None, title=None, color=None, **kw):
		super().__init__(parent, **kw)
		if title:
			self.title('Pick a color')
		if parent: self.transient(parent, **kw)
		self.protocol("WM_DELETE_WINDOW", self.return_color)

		if isinstance(color, tuple): self.color = self.rgb2hex(color)
		elif color: self.color = color
		else: self.color = '#000000'
		color_hex = self.hex_fix(self.color)
		color_hex = (color_hex[:2], color_hex[2:4], color_hex[4:6])
		rgb = self.hex2rgb(self.color)

		self.var_0 = tkinter.StringVar(value=self.color)
		self.var_1 = tkinter.StringVar(value=rgb)
		self.colorlabel = Label(self, text="               ", background=self.color)
		self.hex_r = Label(self, text=color_hex[0].lower())
		self.hex_g = Label(self, text=color_hex[1].lower())
		self.hex_b = Label(self, text=color_hex[2].lower())
		self.scale = tkinter.Scale(self, orient='horizontal', length=250, from_=0, to=255, command=self.sacale)
		self.scale1 = tkinter.Scale(self, orient='horizontal', length=250, from_=0, to=255, command=self.sacale)
		self.scale2 = tkinter.Scale(self, orient='horizontal', length=250, from_=0, to=255, command=self.sacale)
		self.scale .set(rgb[0])
		self.scale1.set(rgb[1])
		self.scale2.set(rgb[2])
		# hex
		hexxl = Label(self, text="hex")
		hexx = Entry(self, width=40, textvariable=self.var_0, validate='key', validatecommand=(self.register(lambda *args: False), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))
		# rgb
		rgbl = Label(self, text="rgb")
		rgb = Entry(self, width=40, textvariable=self.var_1, validate='key', validatecommand=(self.register(lambda *args: False), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))

		self.colorlabel.grid(column=1, row=1)
		self.hex_r.grid(column=0, row=2)
		self.scale.grid(column=1, row=2, columnspan=2)
		self.hex_g.grid(column=0, row=3)
		self.scale1.grid(column=1, row=3, columnspan=2)
		self.hex_b.grid(column=0, row=4)
		self.scale2.grid(column=1, row=4, columnspan=2)

		hexxl.grid(column=0, row=5)
		hexx.grid( column=1, row=5)
		rgbl.grid( column=0, row=6)
		rgb.grid(  column=1, row=6)
		self.master.wait_window(self)

	def return_color(self):
		self.destroy()
		self.color = self.var_0.get()

	def rgb2hex(self, rgb:tuple) -> str:
		r, g, b = rgb
		return f'#{r:02x}{g:02x}{b:02x}'

	def hex_fix(self, hexx:str) -> tuple:
		if len(hexx) == 3:
			hexx = ''.join([str(c + c) for c in hexx])
		elif len(hexx) == 4:
			hexx = ''.join([str(c + c) for c in hexx[1:]])
		elif len(hexx) == 7:
			hexx = hexx[1:]
		return hexx

	def hex2rgb(self, hexx:str) -> tuple:
		hexx = self.hex_fix(hexx)
		n = 2
		a = [hexx[i:i+n] for i in range(0, len(hexx), n)]
		return tuple(int(i, 16) for i in a)

	def sacale(self, event):
		r = self.scale.get()
		g = self.scale1.get()
		b = self.scale2.get()
		hexclr = f'#{r:02x}{g:02x}{b:02x}'
		self.colorlabel.config(background=hexclr)#, text=hex, foreground=TCC(hex)
		#self.config(background=f'#{h}{e}{x}')
		self.hex_r.config(text=hexclr[1:3])
		self.hex_g.config(text=hexclr[3:5])
		self.hex_b.config(text=hexclr[5:7])

		self.var_0.set(hexclr)
		self.var_1.set(f'{r}, {g}, {b}')

def askcolor(parent=None, color=None, **kw):
	return pick(parent, color=color, **kw).color

if __name__ == "__main__":
	root = tkinter.Tk()
	#tkinter.colorchooser.askcolor(title='Pick a color')[1]
	a = askcolor(root, color='#FFDBC6')
	print(a)
	root.mainloop()