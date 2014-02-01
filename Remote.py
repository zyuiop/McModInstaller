import http.client
import urllib.request
import UserInteract
import os
import shutil
import json
from distutils.dir_util import *
import time
import tkinter.messagebox as tkMessageBox
import downloader

class Remote:
	def __init__(self, repo, directory, mcpath, LocalDB, gui = False, gui_parent = None):
		"""Initialise la classe Remote
		repo = domaine du repository (exemple: minecraft.zgalaxy.fr)
		directory = dossier du repo (exemple: /depot/)
		mcpath = chemin complet (exemple: /home/zyuiop/.minecraft/)"""

		self.repo = repo
		self.directory = directory
		self.mcpath = mcpath
		self.localDB = LocalDB
		self.gui = gui
		self.gui_parent = gui_parent

	def downloadFile(self,url, savepath = "temp.bin", label="Downloaded {} / {}", gui_filename = None):
		dl = downloader.Downloader(url, savepath,label, self.gui, gui_filename = gui_filename, gui_parent = self.gui_parent)
		res,rep = dl.start()
		if res != True:
			return (False, rep)
		else:
			f = open(rep, "rb")
			return (True, f.read())

	def updateList(self):
		result, content = self.downloadFile("http://"+self.repo+self.directory+"/repo.lst", gui_filename="Syncronisation du dépôt")
		if result == False:
			return (False, content)
		try:
			rep = json.loads(content.decode("UTF-8"))
			assert rep != False
			self.repContent = rep
			return (True, rep)
		except:
			return (False, "Erreur")

	def downloadPkgInfo(self,package):
		result, content = self.downloadFile("http://"+self.repo+self.directory+"/"+package, gui_filename="Récupération du paquet")
		if not result:
			return (result, content)
		try:
			return (True, json.loads(content.decode("UTF-8")))
		except:
			return (False,"Erreur d'interprétation du json)")

	def getPackage(self, package_name, minecraft_version):
		mods = self.repContent["mods"]
		modv = mods.get(minecraft_version)
		if modv == None:
			return (False, "La version de minecraft n'est pas prise en charge.")
		mod = modv["mods"].get(package_name)
		if mod == None:
			return (False,"Le mod n'a pas été trouvé.")

		return (True, mod)

	def search(self,key):
		gotRes = False
		key = key.lower()
		results = []

		for name, version in self.repContent["mods"].items():
			for pkname, pk in version["mods"].items():
				if key in pk["name"].lower() or key in pkname.lower():
					results.append({"name":pk["name"],"version":name,"pkname":pkname})

		return results

	def getPackageUpdates(self, package):
		url = package.get("pkgurl")
		version = package.get("version")

		if url == None or version == None:
			return (False, "Paquet invalide.")
		ok, rep = self.downloadPkgInfo(package["pkgurl"])
		if ok == False:
			return (False, "Erreur de récupération du paquet : "+rep)

		if rep["version"] > package["version"]:
			return (True, True)
		return (True, False)
