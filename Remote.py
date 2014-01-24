import http.client
import os
import shutil
import json

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

	def downloadFile(self,server,url):
		conn = http.client.HTTPConnection(server)
		conn.request("GET", url)
		rep = conn.getresponse()
		if rep.status != 200:
			print("Erreur : impossible de se connecter au serveur !! Code erreur : "+rep.reason)
			return False
		else:
			return rep.read()

	def updateList(self):
		try:
			rep = json.loads(self.downloadFile(self.repo, self.directory+"/repo.lst").decode("UTF-8"))
			assert rep != False
			self.repContent = rep
			return rep
		except:
			return False

	def downloadPkgInfo(self,package):
		try:
			return json.loads(self.downloadFile(self.repo, self.directory+"/"+package).decode("UTF-8"))
		except:
			return False

	def installMod(self,pkg):
		installpath = self.mcpath+"/mods/"+pkg["mcver"]

		# Vérif : est il installé SELON LA DB dans sa version la plus récente ?
		localPKG = self.localDB.getPackage(pkg["pkgurl"])
		if localPKG != False:
			if localPKG["version"] == pkg["version"] and localPKG["installname"] == pkg["installname"] and localPKG["mcver"] == pkg["mcver"]:
				print("> Le paquet "+pkg["name"]+" semble être dèjà installé... Voulez vous le réinstaller ?")
				if input("[O/n] ").lower() == "n":
					return True



		# Verif : est-ce un coremod (à installer à part) ?
		if "modtype" in pkg.keys():
			if pkg["modtype"] == "coremod":
				installpath = self.mcpath+"/coremods/"+pkg["mcver"]

		# Vérif : Le dossier d'install existe t-il ?
		if not os.path.exists(installpath):
			os.mkdir(installpath)

		# On checke les dépendances
		print(">> Résolution des dépendances...")
		for d in pkg["dependencies"]:
			print("")
			print("Installation de la dépendance "+d["name"])
			

			dep = self.downloadPkgInfo(d["pkgurl"])
			if not dep:
				print("Impossible de récupérer le paquet.")
				print("Une dépendance n'a pas été trouvée ! Le mod pourrait ne pas fonctionner")
			else:
				dep["pkgurl"] = d["pkgurl"]
				self.installMod(dep)
				print("")

		# Installation du mod
		installed = False
		print(">> Installation du mod")
		for m in pkg["mirrors"]:
			
			print("> Tentative de téléchargement de "+m["server"]+m["path"]+"...")
			tosave = self.downloadFile(m["server"],m["path"])
			
			if tosave == False:
					print("!> Erreur lors du téléchargement depuis "+m["server"])
			else:
				with open(installpath+"/"+pkg["installname"], "wb") as fichier:
					try:
						fichier.write(tosave)
						print("> Le mod a été installé !")
					except:
						print("Erreur d'écriture du mod.")
					else:
						self.localDB.updatePackage(pkg["pkgurl"], pkg)
						return True
				
		return False

	def installClient(self, pkg):

		# On vérifie si la version non moddée est installée
		path = self.mcpath+"/"
		if os.path.isdir(path+"versions/"+pkg["version"]):
			# Pareil, mais avec le jar
			if os.path.exists(path+"versions/"+pkg["version"]+"/"+pkg["version"]+".jar"):
				
				# On crée le dossier d'installation
				if not os.path.exists(path+"versions/"+pkg["profilename"]):
					os.mkdir(path+"versions/"+pkg["profilename"])
				else:
					print("[/!\\] Le dossier du profil existe")

				# S'il y a un fichier à télécharger
				if "jarfile" in pkg.keys():
					print("[1/3] Téléchargement de minecraft.jar...")
					with open(path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".jar", "wb") as fichier:
						try:
							tosave = downloadFile(self.repo,self.directory+"/"+pkg["jarfile"])
							fichier.write(tosave)
						except:
							print("Erreur ! Impossible de télécharger ou d'écrire "+pkg["profilename"]+".jar")
							return False
				else:
					print("[1/3] Copie du fichier...")
					shutil.copy(path+"versions/"+pkg["version"]+"/"+pkg["version"]+".jar", path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".jar")
					print("[1/3] Copie terminée.")

				print("[2/3] Téléchargement du profil")
				tosave = self.downloadFile(self.repo,self.directory+"/"+pkg["json"])
				with open(path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".json", "wb") as fichier:
					try:
						fichier.write(tosave)
					except:
						print("Erreur ! Impossible d'écrire dans le fichier ou de télécharger le fichier json")
						return False

				print("[2/3] Profil téléchargé et sauvegardé.")
				print("[3/3] Ecriture dans le fichier de profils...")
				try:
					with open(path+"launcher_profiles.json", "r") as fichier:
						try:
							jsonfile = fichier.read()
						except:
							print("Une erreur s'est produite.")
							return False
				except FileNotFoundError:
					print("Erreur : Lecture du fichier de profils impossibles. Minecraft est il correctement installé ?")
					return False

				tab = json.loads(jsonfile)
				new_profile = {"name":pkg["name"],"lastVersionId":pkg["profilename"]}
				tab["profiles"][pkg["name"]] = new_profile

				with open(path+"launcher_profiles.json", "w") as fichier:
					try:
						fichier.write(json.dumps(tab))
						print("[3/3] Terminé !")
						print("Le profil a bien été installé ! ")
						return True
					except:
						print("Erreur lors de l'écriture du fichier de profils")
						return False
			else:
				print("Minecraft n'est pas installé en "+pkg["version"]+". Veuillez l'installer avant toute chose")
		else:
			print("Minecraft n'est pas installé en "+pkg["version"]+". Veuillez l'installer avant toute chose")
		return False
