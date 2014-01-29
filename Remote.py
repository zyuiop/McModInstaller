import http.client
import urllib.request
import UserInteract
import os
import shutil
import json
from distutils.dir_util import *
import time
import tkinter.messagebox as tkMessageBox

class Remote:
	def __init__(self, repo, directory, mcpath, LocalDB):
		
		"""Initialise la classe Remote
		repo = domaine du repository (exemple: minecraft.zgalaxy.fr)
		directory = dossier du repo (exemple: /depot/)
		mcpath = chemin complet (exemple: /home/zyuiop/.minecraft/)"""

		self.repo = repo
		self.directory = directory
		self.mcpath = mcpath
		self.localDB = LocalDB

	def downloadFile(self,server,url,progress=True):
		conn = http.client.HTTPConnection(server)
		conn.request("GET", url)
		rep = conn.getresponse()
		if rep.status != 200:
			return (False, rep.reason)
		else:
			return (True, rep.read())

	def updateList(self):
		result, content = self.downloadFile(self.repo, self.directory+"/repo.lst")
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
		result, content = self.downloadFile(self.repo, self.directory+"/"+package)
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

	def showModStatusText(self, text, caller = None, origin = None):
		if caller == None:
			print(text)
		else:
			if origin == "Update":
				self.updateLog(text, caller)
			elif origin == "Search":
				caller.changeSearchInfoText("\n"+text, False)
			else:
				caller.changeModsInfoText("\n"+text,False)
		return


	def search(self,key, caller = None):
		gotRes = False
		key = key.lower()
		results = []

		for name, version in self.repContent["mods"].items():
			for pkname, pk in version["mods"].items():
				if key in pk["name"].lower() or key in pkname.lower():
					results.append({"name":pk["name"],"version":name,"pkname":pkname})

		if caller == None:
			print("#====[AFFICHAGE DES RESULTATS]====#")
			print("# Recherche : "+key)
			print("Nom du paquet : Nom du Mod (Version minecraft)")
			for res in results:
				print(res["version"]+"__"+res["pkname"]+" : "+res["name"]+" ("+res["version"]+")")
		else:
			return results

	def updateLog(self, message, caller = None):
		if caller == None:
			print(message)
		else:
			caller.changeUpdatesInfoText("\n"+message,False)
		return

	def updateMods(self, noconfirm = False, caller = None):
		self.updateLog("Recherche des mises à jour...", caller)
		pkgs = self.localDB.getAllPackages()
		toupdate = []
	
		# Vérif des updates
		for reponame, package in pkgs.items():
			self.updateLog("> Vérification des mises à jour de "+package["name"], caller)
			ok, rep = self.downloadPkgInfo(package["pkgurl"])
			
			if ok == False:
				self.updateLog(">> Impossible de vérifier la version du paquet (Erreur réseau : "+rep+")", caller)
			else:
				if rep["version"] > package["version"]:
					rep["pkgurl"] = package["pkgurl"]
					toupdate.append(rep)
					self.updateLog(">> Mise à jour disponible.", caller)
				else:
					self.updateLog(">> Non mis à jour", caller)
			
		if len(toupdate) == 0:
			self.updateLog("AUCUNE MISE A JOUR DISPONIBLE.", caller)
		else:
			self.updateLog("Il y a "+str(len(toupdate))+" mise(s) à jour à installer.", caller)
			if caller == None:
				if noconfirm or UserInteract.UserInteract().yesNoQuestion("Voulez vous les installer ?"):
					print("")
					print("Début de la mise à jour...")

					for package in toupdate:
						print("> Mise à jour de "+package["name"])
						print("")
						if not self.installMod(package, noconfirm):
							print("> Erreur de mise à jour.")
						else:
							print("> Mise à jour du mod effectuée.")
						print("")
						return True
			
		return toupdate

	def yesNo(self, question, questionTitle="", caller = None):
		if caller == None:
			return UserInteract.UserInteract.yesNoQuestion(None, question)
		else:
			return tkMessageBox.askyesno(questionTitle, question)

	def installMod(self,pkg,noconfirm = False, depends_treated = [], caller=None, origin = None):
		installpath = self.mcpath+"/mods/"+pkg["mcver"]

		# Vérif : est il installé SELON LA DB dans sa version la plus récente ?
		installed, localPKG = self.localDB.isInstalled(pkg["package_name"], pkg["mc_version"])
		if installed != False:
			if localPKG["version"] == pkg["version"] and localPKG["installname"] == pkg["installname"] and localPKG["mcver"] == pkg["mcver"] and not noconfirm:
				continuer = self.yesNo("Le paquet "+pkg["name"]+" semble être dèjà installé... Voulez vous le réinstaller ?", "Paquet dèjà installé", caller)
				if not continuer:
					return True



		# Verif : est-ce un coremod (à installer à part) ?
		if "modtype" in pkg.keys():
			if pkg["modtype"] == "coremod":
				installpath = self.mcpath+"/coremods/"+pkg["mcver"]

		# Vérif : Le dossier d'install existe t-il ?
		if not os.path.exists(installpath):
			mkpath(installpath)

		# On checke les dépendances
		self.showModStatusText(">> Résolution des dépendances...", caller, origin)
		for d in pkg["dependencies"]:
			

			res, dep = self.downloadPkgInfo(d["pkgurl"])

			if not res:
				self.showModStatusText("/!\ Impossible de récupérer le paquet d'une dépendance... Erreur : "+dep, caller, origin)
				self.showModStatusText("/!\ Une dépendance n'a pas été trouvée ! Le mod pourrait ne pas fonctionner", caller, origin)
			else:
				dep_name = self.localDB.packageName(dep["package_name"],dep["mc_version"])
				if not dep_name in depends_treated:
					self.showModStatusText("", caller, origin)
					self.showModStatusText("Installation de la dépendance "+d["name"], caller, origin)
					dep["pkgurl"] = d["pkgurl"]
					depends_treated.append(dep_name)
					self.installMod(dep,noconfirm, depends_treated, caller, origin)
					self.showModStatusText("", caller,origin)


		# Installation du mod
		installed = False
		self.showModStatusText(">> Installation du mod", caller, origin)
		for m in pkg["mirrors"]:
			
			self.showModStatusText("> Tentative de téléchargement de "+m["server"]+m["path"]+"...", caller, origin)
			res, tosave = self.downloadFile(m["server"],m["path"])
			
			if res == False:
					self.showModStatusText("/!\ Erreur lors du téléchargement depuis "+m["server"]+". Erreur : "+tosave, caller, origin)
					self.showModStatusText("", caller, origin)
			else:
				with open(installpath+"/"+pkg["installname"], "wb") as fichier:
					try:
						fichier.write(tosave)
						self.showModStatusText("> Téléchargement réussi. Le mod a été installé", caller, origin)
					except:
						self.showModStatusText("(!) Erreur d'écriture du mod, echec d'installation.", caller, origin)
					else:
						depends_treated = {}
						self.localDB.updatePackage(self.localDB.packageName(pkg["package_name"], pkg["mc_version"]), pkg)
						time.sleep(1)
						return True
		depends_treated = {}		
		return False

	def showClientStatusText(self, text, caller = None):
		if caller == None:
			print(text)
		else:
			caller.changeVersionsInfoText("\n"+text,False)
		return



	def installClient(self, pkg, caller = None):

		# On vérifie si la version non moddée est installée
		path = self.mcpath+"/"
		if os.path.isdir(path+"versions/"+pkg["version"]):
			# Pareil, mais avec le jar
			if os.path.exists(path+"versions/"+pkg["version"]+"/"+pkg["version"]+".jar"):
				
				# On crée le dossier d'installation
				if not os.path.exists(path+"versions/"+pkg["profilename"]):
					mkpath(path+"versions/"+pkg["profilename"])
				else:
					self.showClientStatusText("[/!\\] Le dossier du profil existe",caller)

				# S'il y a un fichier à télécharger
				if "jarfile" in pkg.keys():
					self.showClientStatusText("[1/3] Téléchargement de minecraft.jar...",caller)
					res, tosave = self.downloadFile(self.repo,self.directory+"/"+pkg["jarfile"])
					if not res:
						self.showClientStatusText("Erreur lors du téléchargement de "+self.repo+self.directory+"/"+pkg["jarfile"]+". Code erreur : "+tosave,caller)
					else:
						with open(path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".jar", "wb") as fichier:
							try:
								fichier.write(tosave)
							except:
								self.showClientStatusText("Erreur ! Impossible d'écrire "+pkg["profilename"]+".jar",caller)
								return False
				else:
					self.showClientStatusText("[1/3] Copie du fichier...",caller)
					shutil.copy(path+"versions/"+pkg["version"]+"/"+pkg["version"]+".jar", path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".jar")
					self.showClientStatusText("[1/3] Copie terminée.",caller)

				self.showClientStatusText("[2/3] Téléchargement du profil",caller)
				res, tosave = self.downloadFile(self.repo,self.directory+"/"+pkg["json"])
				if not res:
					self.showClientStatusText("Erreur lors du téléchargement de "+self.repo+self.directory+"/"+pkg["json"]+". Code erreur : "+tosave,caller)
				with open(path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".json", "wb") as fichier:
					try:
						fichier.write(tosave)
					except:
						self.showClientStatusText("Erreur ! Impossible d'écrire dans le fichier json du profil. ",caller)
						return False

				self.showClientStatusText("[2/3] Profil téléchargé et sauvegardé.",caller)
				self.showClientStatusText("[3/3] Ecriture dans le fichier de profils...",caller)
				try:
					with open(path+"launcher_profiles.json", "r") as fichier:
						try:
							jsonfile = fichier.read()
						except:
							self.showClientStatusText("Une erreur s'est produite.",caller)
							return False
				except FileNotFoundError:
					self.showClientStatusText("Erreur : Lecture du fichier de profils impossibles. Minecraft est il correctement installé ?",caller)
					return False

				tab = json.loads(jsonfile)
				new_profile = {"name":pkg["name"],"lastVersionId":pkg["profilename"]}
				tab["profiles"][pkg["name"]] = new_profile

				with open(path+"launcher_profiles.json", "w") as fichier:
					try:
						fichier.write(json.dumps(tab))
						self.showClientStatusText("[3/3] Terminé !",caller)
						self.showClientStatusText("Le profil a bien été installé ! ",caller)
						return True
					except:
						self.showClientStatusText("Erreur lors de l'écriture du fichier de profils",caller)
						return False
			else:
				self.showClientStatusText("Minecraft n'est pas installé en "+pkg["version"]+". Veuillez l'installer avant toute chose",caller)
		else:
			self.showClientStatusText("Minecraft n'est pas installé en "+pkg["version"]+". Veuillez l'installer avant toute chose",caller)
		return False
