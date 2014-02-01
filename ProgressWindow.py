from tkinter import *
import tkinter.ttk as ttk
import math
import tkinter.messagebox as tkMessageBox

class ProgressWindow(Frame):
	def __init__(self, text, title, showProgress = False,**kwargs):
		self.fenetre = Tk()
		self.fenetre.title(title)
		Frame.__init__(self, self.fenetre, width=768, height=576, **kwargs)
		self.pack()

		self.label = Label(self, text=text, anchor=NW, justify=LEFT)
		self.label.grid(row=0,column=0,columnspan=2)
		if showProgress:
			self.progressBar = ttk.Progressbar(self, length=300)
			self.progressBar.grid(row=1,column=0)
			self.progressVal = IntVar()
			self.progressBar.config(variable = self.progressVal)
			self.progLabel = Label(self,text="0%", justify=LEFT, anchor=W)
			self.progLabel.grid(row=1,column=1)

		self.fenetre.protocol("WM_DELETE_WINDOW", self.handler)
		self.finished = True

	def setProgressValue(self, val, maxVal):
		v = (val/maxVal)*100
		self.progressVal.set(v)
		self.progLabel.config(text=str(math.floor(v))+"%")

	def hideProgressBar(self):
		self.progressBar.destroy()
		self.progLabel.destroy()

	def setLabelText(self, text, color="black"):
		self.label.config(text=text,fg=color)

	def terminate(self):
		Button(self, text="Fermer",command=self.fenetre.quit).grid(row=2,column=0,columnspan=2)

	def handler(self):
		if tkMessageBox.askyesno("Annuler ?", "Voulez vous vraiment annuler le téléchargement ?"):
			self.finished = False
			self.fenetre.quit()