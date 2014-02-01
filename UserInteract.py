import math
from config import *

class UserInteract:
	def setLocalDB(self, localDB):
		self.localDB = localDB

	def setRemote(self,remote):
		self.remote = remote


	def yesNoQuestion(self, question, defaultNo = False):
		rep = "x"
		while rep.lower() not in ("o","n", ""):
			print(question)
			help = "[O/n] "
			if defaultNo:
				help = "[o/N] "
			rep = input(help)
			if rep == "":
				if defaultNo:
					return False
				return True
			elif rep.lower() == "o":
				return True
			elif rep.lower() == "n":
				return False
			else:
				print("Saisie non valide")

	def mainMenu(self):
		return 0

	def showModStatusText(self, text, caller = None, origin = None):
		if caller == None:
			print(text)
		else:
			caller.appendConsole(text)
		return

	def inputDepot(self):
		if not self.yesNoQuestion("Voulez vous utiliser le dépôt par défaut ? (Non = dépôt personnalisé) "):
			srv = input("Entrez l'adresse exacte du serveur sans le \"http://\" : ")
			srv = srv.split("/")
			serveur = ""
			dossier = "/"
			if len(srv) == 1:
				serveur = srv[0]
			else:
				serveur = srv[0]
				for key,content in enumerate(srv):
					if key > 0:
						dossier = dossier+content+"/"

			return (serveur, dossier)
		else:
			return ("minecraft.zgalaxy.fr","/")

	def menu(self, name, choices):
		print("#====["+name+"]====#")
		for i,ch in enumerate(choices):
			print(str(i)+" : "+ch)

		try:
			choix = int(input("Action : "))
			assert choix >= 0 and choix < len(choices)
			return choix
		except:
			print("Choix non valide, merci de recommencer")


	def mainMenu(self):
		choix = []
		choix.append("Quitter le programme")
		choix.append("Gérer les versions de Minecraft")
		choix.append("Installer des mods")
		choix.append("Mettre à jour des mods")
		choix.append("Supprimer des mods")
		choix.append("Rechercher des mods")
		choix.append("Afficher l'aide")
		choix.append("Changer de dépôt")
		return self.menu("Menu Principal",choix)

	def packageInfoShower(self, package, caller = None, origin = None):
		self.showModStatusText("VERSION : "+package["version"], caller)
		self.showModStatusText("NOM PAQUET : "+package["mc_version"]+"__"+package["package_name"], caller, origin)
		self.showModStatusText("DESCRIPTION : "+package["description"], caller, origin)
		self.showModStatusText("URL du .PKG : "+package["pkgurl"], caller, origin)
		self.showModStatusText("POUR MINECRAFT "+package["requires"], caller, origin)
		self.showModStatusText("SITE WEB : "+package["website"], caller, origin)
		self.showModStatusText("DEPENDANCES : ", caller, origin)
		for dep in package["dependencies"]:
			self.showModStatusText(" -> "+dep["name"], caller, origin)

	def packageInstallPrompt(self, packageUrl, noconfirm = False, caller = None):
		# Récup du paquet
		if self.remote == None:
			print("Erreur interne : la méthode setRemote(remote) n'a pas été appelée")
			return False

		result, package = self.remote.downloadPkgInfo(packageUrl)
		if result == False:
			print("Impossible de récupérer le paquet...")
			print("Détails de l'erreur : "+package)
		else:
			package["pkgurl"] = packageUrl
			self.showModStatusText("#====[Affichage du mod : "+package["name"]+"]====#",caller)
			self.packageInfoShower(package, caller)

			if noconfirm or self.yesNoQuestion("== Voulez vous installer ce mod ? =="):
				
				print("Le mod va être installé. Patientez s'il vous plait...")
				self.remote.installMod(package,noconfirm)
