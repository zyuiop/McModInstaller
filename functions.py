import http.client
import os
import shutil
import json

def updateList(repo):
	conn = http.client.HTTPConnection(repo)
	conn.request("GET", "/repo.lst")
	rep = conn.getresponse()
	if rep.status != 200:
		print("Erreur : impossible de se connecter au dépôt !! Code erreur : "+rep.reason)
		return False
	else:
		return rep.read()

def downloadPkgInfo(repo, pkg):
	conn = http.client.HTTPConnection(repo)
	conn.request("GET", pkg)
	rep = conn.getresponse()
	if rep.status != 200:
		print("Erreur : impossible de se connecter au serveur !! Code erreur : "+rep.reason)
		return False
	else:
		return rep.read()

def installMod(repo,pkg,path):
	installpath = path+"mods/"+pkg["mcver"]
	if "modtype" in pkg.keys():
		if pkg["modtype"] == "coremod":
			installpath = path+"coremods/"+pkg["mcver"]
	if not os.path.exists(installpath):
		os.mkdir(installpath)

	print(">> Résolution des dépendances...")
	for d in pkg["dependencies"]:
		print("Installation de la dépendance "+d["name"])
		try:
			package = json.loads(functions.downloadPkgInfo("minecraft.zgalaxy.fr",d["pkgurl"]).decode("UTF-8"))
		except:
			print("Impossible de récupérer le paquet.")
			print("Une dépendance n'a pas été trouvée ! Le mod pourrait ne pas fonctionner")
		else:
			installMod(repo,package,path)

	installed = False
	print(">> Installation du mod")
	for m in pkg["mirrors"]:
		with open(installpath+"/"+pkg["installname"], "wb") as fichier:
			try:
				print("> Connection à "+m["server"]+m["path"]+"...")
				tosave = downloadPkgInfo(m["server"],m["path"])
				fichier.write(tosave)
				print("> Le mod a été installé !")
				return True
			except:
				print("!> Erreur lors du téléchargement depuis "+m["server"])
	return False

def installClient(repo, pkg, path):
	if os.path.isdir(path+"versions/"+pkg["version"]):
		if os.path.exists(path+"versions/"+pkg["version"]+"/"+pkg["version"]+".jar"):
			if not os.path.exists(path+"versions/"+pkg["profilename"]):
				os.mkdir(path+"versions/"+pkg["profilename"])
			else:
				print("[/!\\] Le dossier du profil existe")

			if "jarfile" in pkg.keys():
				print("[1/3] Téléchargement de minecraft.jar...")
				with open(path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".jar", "wb") as fichier:
					try:
						tosave = downloadPkgInfo(repo,pkg["jarfile"])
						fichier.write(tosave)
					except:
						print("Erreur ! Impossible de télécharger ou d'écrire "+pkg["profilename"]+".jar")
						return False
			else:
				print("[1/3] Copie du fichier...")
				shutil.copy(path+"versions/"+pkg["version"]+"/"+pkg["version"]+".jar", path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".jar")
				print("[1/3] Copie terminée.")

			print("[2/3] Téléchargement du profil")
			with open(path+"versions/"+pkg["profilename"]+"/"+pkg["profilename"]+".json", "w") as fichier:
				try:
					tosave = downloadPkgInfo(repo,pkg["json"]).decode("UTF-8")
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
