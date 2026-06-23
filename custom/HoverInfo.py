import tkinter
from typing import Unpack, TypedDict

class tkinter_label(TypedDict, total=False):
	bg:str
	fg:str
	cursor:str
	relief:str
	borderwidth:int
	textvariable:tkinter.StringVar

class Tooltip:#eveh=hover enter event, evex=hover exit event, evem=hover motion event
	def __init__(self, parent, text='text', move_with_cursor=False, eveh=False, evex=False, evem=False, **kwargs: Unpack[tkinter_label]):
		self.parent = parent
		self.text   = text
		self.kwargs = kwargs
		self.kwargs['bg']           = kwargs.get("bg", 'gray94')
		self.kwargs['fg']           = kwargs.get('fg', 'black')
		self.kwargs['cursor']       = kwargs.get('cursor', 'arrow')
		self.kwargs['relief']       = kwargs.get('relief', 'groove')# flat, groove, raised, ridge, solid, or sunken
		self.kwargs['borderwidth']  = kwargs.get('borderwidth', 2)

		self.parent.bind("<Enter>", lambda event: self.Hover(event) if not eveh else eveh(event))
		self.parent.bind("<Leave>", lambda event: self.Hover(event) if not evex else evex(event))
		if move_with_cursor:
			self.parent.bind("<Motion>", lambda event: self.motion(event) if not evem else evem(event), True)

	def Hover(self, event):
		evetype = int(event.type)
		if evetype == 7:
			self.Hovertoplevel = tkinter.Toplevel(self.parent)
			self.Hovertoplevel.overrideredirect(True)
			self.Hovertoplevel.geometry(f"+{event.x_root}+{event.y_root+20}")
			self.parent.config(cursor=self.kwargs.get('cursor'))
			tkinter.Label(self.Hovertoplevel, text=self.text, **self.kwargs, ).grid(column=0, row=0)
		if evetype == 8:
			self.Hovertoplevel.destroy()

	def motion(self, event):
		self.Hovertoplevel.geometry(f"+{event.x_root}+{event.y_root+20}")

if __name__ == "__main__":
	root = tkinter.Tk()
	lbl = tkinter.Label(root, text='hover over me!')
	lbl.grid(column=0, row=0)
	msg = "cool right?\n at least I think so!"
	textvar = tkinter.StringVar()
	textvar.set('aaaaaaaaaaa')
	Tooltip(lbl, text=msg, bg='green', fg='purple', cursor="hand2", relief='sunken', borderwidth=10, move_with_cursor=True)
	#methods
	#test.text = "new words though \"text\""
	#test.strVar.set("new text though \"StringVar\"\n benefit to this is it updates live rather then needing to be destroyed and remade but it really doesn't\n matter unless you remove the \"Leave\" event but that kind of defeats the purpose of this library") #only works if textvar=True
	root.mainloop()
