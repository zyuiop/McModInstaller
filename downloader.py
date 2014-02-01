import urllib.request as urllib
import math
import ProgressWindow as p
import time
import _thread

class Downloader:
	def __init__(self, url, saveas, label = "Downloaded {} / {}", gui = False, gui_filename=None):
		self.url = url
		self.saveas = saveas
		self.prog = None
		self.label = label
		if gui == True:
			self.prog = p.ProgressWindow("Téléchargement","Téléchargement",True)
			if gui_filename != None:
				self.label = gui_filename+"\n"+label


	def humanSize(self, size):
		if size > 1.5*1024*1024*1024: # Plus de 1.5go
			return str((math.floor((size/(1024*1024*1024))*10))/10)+"Gio"
		elif size > 1.5*1024*1024: # Plus de 1.5mo
			return str((math.floor((size/(1024*1024))*10))/10)+"Mio"
		elif size > 5*1024: # Plus de 5ko
			return str((math.floor((size/1024)*10))/10)+"Kio"
		else:
			return str(size)+"o"

	def progressBar(self, blocks, blocksize, total):
		file_size_dl = blocksize*blocks
		bars = math.floor((file_size_dl * 100 / total))
		pr = self.prog
		string = self.label.format(self.humanSize(file_size_dl), self.humanSize(total))
		if pr != None:
			pr.setProgressValue(file_size_dl, total)
			pr.setLabelText(string)
			if bars == 100:
				if self.autoclose:
					pr.fenetre.quit()
				else:
					pr.terminate()
		else:
			string += " : [" + "#"*bars + " "*(100-bars) + "] "+str(math.floor(file_size_dl * 100. / total))+"%       "
			string = string + chr(8)*(len(string))
			print(string, flush=True, end='')

	def guiDownload(self):
		try:
			urllib.urlretrieve(self.url, self.saveas, self.progressBar)
			return
		except urllib.URLError as erreur:
			self.prog.setLabelText("Une erreur s'est produite : \n"+str(erreur))
			self.error = str(erreur)
		except:
			self.prog.setLabelText("Une erreur d'origine inconue s'est produite.")
			self.error = "Erreur inconue"
		self.prog.terminate()
		self.prog.hideProgressBar()
		self.finished = False
		return


	def start(self, autoclose = False):
		try:
			if self.prog != None:
				self.finished = True
				self.error = self.saveas

				self.autoclose = autoclose

				_thread.start_new_thread(self.guiDownload, ())
				self.prog.mainloop()
				if not self.prog.finished:
					self.error = "Canceled"
					self.finished = False

				return (self.finished,self.error)

			urllib.urlretrieve(self.url, self.saveas, self.progressBar)
			return (True,self.saveas)
		except urllib.URLError as erreur:
			return (False, str(erreur))
		except:
			return (False, "Erreur inconue")
