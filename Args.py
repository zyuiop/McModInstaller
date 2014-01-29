# File used for commands

import http.client
import os
import shutil
import json
import sys,getopt
from Remote import *
from UserInteract import *


class Args:
	def __init__(self, localDB, settings, mcpath, args, original_args):
		self.localDB = localDB
		self.settings = settings
		self.mcpath = mcpath
		self.args = args
		self.original_args = original_args
		self.UI = UserInteract()

	def init(self):
		repo = self.settings.getNode("repository")
		repoDirectory = self.settings.getNode("directory")
		if repo == False:
			print("Aucun dépôt configuré. Le programme va quitter")
			exit()
		self.repo = Remote(repo, repoDirectory, self.mcpath, self.localDB)
		self.liste = self.repo.updateList()
		if not self.liste:
			print("Impossible d'atteindre le dépôt.")
			exit()

		self.UI.setRemote(self.repo)

	def execute(self):
		# Analyse des paramètres

		mod = ""
		version = ""
		for opt, arg in self.args:
			if opt in ("-h","--help"):
				print("Usage : main.py or main.py [-mvpc]")
				print("Without arguments : start main.py with a CLI UI")
				print("Arguments :")
				print(" -m or --mod=<modname> : Install a mod (must be used with the -v or --version)")
				print(" -v or --version=<mcversion> : Minecraft version. Needed to install a mod using -m (for example : main.py --version=1.6.2 --mod=ComputerCraft) ")
				print(" -p or --package=<packagename> : Install a mod using packagename (for example : 1.6.2__ComputerCraft)")
				print(" -c or --client=<clientname> : Install a client (for example : 1.5.2_FML)")
				print(" -u or --update : Update all mods")
				print(" -s or --search : search a mod")
				print(" --noconfirm : don't confirm before installing mod")
				print(" --cli : don't open the GUI, only the console interface")
				return True
			elif opt in ("-m", "--mod"):
				mod = arg
				if version != "":
					self.searchMod(version,mod)
			elif opt in ("-v", "--version"):
				version = arg
				if mod != "":
					self.searchMod(version,mod)
			elif opt in ("-c", "--client"):
				self.searchClient(arg)
			elif opt in ("-p", "--package"):
				cl = arg.split("__")
				if len(cl) < 2:
					print("Erreur : nom de paquet non supporté")
					exit()
				ver = cl[:1]
				reste = cl[1:]
				if len(reste) > 1:
					print("Erreur : nom de paquet non supporté")
					exit()
				self.searchMod(ver[0],reste[0])
			elif opt in ("-u", "--update"):
				self.init()
				if "--noconfirm" in self.original_args:
					self.repo.updateMods(True)
				else:
					self.repo.updateMods()
			elif opt in ("-s", "--search"):
				self.init()
				self.repo.search(arg)
	

	def searchMod(self, mcversion, modname):
		self.init()
		mod = self.repo.getPackage(modname, mcversion)
		if mod == None:
			print("Paquet non trouvé.")
			exit()

		noconfirm = False
		if "--noconfirm" in self.original_args:
			noconfirm = True
		self.UI.packageInstallPrompt(mod["pkgurl"], noconfirm)
		exit()


	def searchClient(self, clientname):
		self.init()
		clients = self.liste.get("clients")
		if clients == None:
			print("La base de données est corrompue.")
			exit()

		client = clients.get(clientname)
		if client == None:
			print("Erreur : Le client est introuvable")
			exit()

		package = self.repo.downloadPkgInfo(client["pkgurl"])
		if package == False:
			print("[ERREUR RESEAU] Impossible de récupérer le paquet.")
		else:
			noconfirm = False
			if "--noconfirm" in self.original_args:
				noconfirm = True
			else:
				print("#====[Affichage client : "+client["name"]+"]====#")
				print("VERSION : "+package["version"])
				print("DESCRIP TION : "+package["description"])
				print("URL du .PKG : "+client["pkgurl"])
				print(">> Voulez vous installer ce client ?")
				char = input("[O/n] ")
				if char == "" or char.lower() == "o":
					print("Le client va être installé. Patientez s'il vous plait...")
				else:
					print("Le client ne sera pas installé. ")
					exit()
		print("Installation du client")
		self.repo.installClient(package)

