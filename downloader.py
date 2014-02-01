import urllib.request as urllib
import math
import time
import _thread
import os

class Downloader:
	def __init__(self, url, saveas, label = "Downloaded {} / {}", gui = False, gui_filename=None, gui_parent = None):
		self.url = url
		self.saveas = saveas
		self.prog = None
		self.label = label
		self.gui_parent = None
		if gui == True:
			self.gui_parent = gui_parent
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
		if file_size_dl > total:
			file_size_dl = total
		self.size = total
		self.dl_size = file_size_dl
		bars = math.floor((file_size_dl * 100 / total))
		pr = self.gui_parent
		string = self.label.format(self.humanSize(file_size_dl), self.humanSize(total))
		if pr != None:
			pr.setProgressValue(file_size_dl, total)
			pr.setStateText(string)
		else:
			string += " : [" + "#"*bars + " "*(100-bars) + "] "+str(math.floor(file_size_dl * 100. / total))+"%       "
			string = string + chr(8)*(len(string))
			print(string, flush=True, end='')

	def guiDownload(self):
		try:
			urllib.urlretrieve(self.url, self.saveas, self.progressBar)
			return
		except urllib.URLError as erreur:
			self.error = str(erreur)
		except:
			self.error = "Erreur inconue"
		self.finished = False
		return


	def start(self):
		try:
			if self.gui_parent != None:
				self.finished = True
				self.error = self.saveas
				self.size = 0
				self.dl_size = -1

				_thread.start_new_thread(self.guiDownload, ())
				
				while self.dl_size < self.size and self.finished != False:
					self.gui_parent.after(25)
					self.gui_parent.fenetre.update()

				# On attend la fin du DL
				return (self.finished,self.error)
			print("Début du téléchargement...\n")
			urllib.urlretrieve(self.url, self.saveas, self.progressBar)
			print("\nTéléchargement réussi.")
			return (True,self.saveas)
		except urllib.URLError as erreur:
			return (False, str(erreur))
		except:
			return (False, "Erreur inconue")