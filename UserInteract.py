import math
from config import *

class UserInteract:
	def yesNoQuestion(self,question, defaultNo = False):
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
		choix.append("Afficher l'aide")
		choix.append("Changer de dépôt")
		return self.menu("Menu Principal",choix)


