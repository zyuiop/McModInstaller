# CONFIGURATION !!!
appdata = ""
# Décommentez la ligne ci dessous pour le programme WINDOWS :
# appdata = "AppData/Roaming"

import functions
import json
import math
print("Bienvenue dans le MC Mod Downloader")
Exec = True

# Récupération de la liste 
print("Connection au dépôt 'minecraft.zgalaxy.fr'")
print("Mise à jour de la base de donnée de paquets... Ceci peut prendre quelques instants")
try:
	repo = json.loads(functions.updateList("minecraft.zgalaxy.fr").decode("UTF-8"))
except:
	print("Impossible de récupérer la liste.")
	Exec = False

from os.path import expanduser
home = expanduser("~")+appdata
import os

# Boucle ppale
while Exec:
	print("")
	print("")
	print("> DEPOT = '"+repo["repo"]+"'")
	print("> Menu principal <")
	print("------------------")
	print("0>Quitter")
	print("1>Clients")
	print("2>Mods")
	print("3>Aide")
	try:
		choix = int(input("Choix : "))
		assert choix >= 0 and choix < 4
	except:
		print("Choix non valide")
	else:
		if choix == 3:
			print("Aide du MCMod Installer")
			print("La première chose à faire est d'installer un client custom. Le client le plus moddé est le client FML (Forge Mod Loader). Allez donc dans 'Clients' puis sélectionnez le client FML de votre version")
			print("Ensuite, installez des mods. Pour cela, rendez vous dans ''mods'' et sélectionnez la version du jeu que vous souhaitez modder. Ensuite, choisissez votre mod !")
		elif choix == 1:
			print(">> Clients disponibles sur le dépôt <<")
			clients = repo["clients"]
			for clid, cl in enumerate(clients):
				print(str(clid)+">"+cl["name"])
			print(">> Voir des détails à propos du client n° ?")
			try:
				num = int(input(">> "))
				assert num >= 0 and num < len(clients)
			except:
				print("Erreur : ce client n'a pas été trouvé !")
			else:
				sel_cl = clients[num]
				try:
					package = json.loads(functions.downloadPkgInfo("minecraft.zgalaxy.fr",sel_cl["pkgurl"]).decode("UTF-8"))
				except:
					print("Impossible de récupérer le paquet.")
				else:
					print("CLIENT : "+sel_cl["name"])
					print("VERSION : "+package["version"])
					print("DESCRIPTION : "+sel_cl["description"])
					print("URL du .PKG : "+sel_cl["pkgurl"])
					print("== Voulez vous installer ce client [O/n] ? ==")
					char = input("> ")
					if char == "" or char.lower() == "o":
						print("Le client va être installé. Patientez s'il vous plait...")
						mcpath = home+"/.minecraft/"
						functions.installClient("minecraft.zgalaxy.fr", package, mcpath)
					else:
						print("Le client ne sera pas installé. Retour au menu")

		elif choix == 2:
			print(">> Versions de mods disponibles : <<")
			mcpath = home+"/.minecraft/"
			versions = repo["mods"]
			for verid, ver in enumerate(versions):
				print(str(verid)+">"+ver["version"])
			print(">> Télécharger des mods pour la version n°")
			try:
				num = int(input("> "))
				assert num >= 0 and num < len(versions)
			except:
				print("Erreur : cet id de version n'existe pas !")
			else:
				print(">> Récupération de la liste de mods pour la version "+versions[num]["version"]+" <<")
				mods = versions[num]["mods"]
				print(">> "+str(len(mods))+" mods sont disponibles pour cette version <<")
				nbpages = math.ceil(len(mods)/10)
				pages = []
				i = 0
				while i < nbpages:
					i+=1
					pages.append(mods[10*(i-1):10*i])
				currentPage = 0
				Browse = True
				while Browse:
					pge = pages[currentPage]
					print("Affichage des mods : page "+str(currentPage+1)+"/"+str(nbpages))
					print("q>Retour au menu")
					if nbpages > 1:
						if currentPage != nbpages-1:
							print("n>Page suivante")
						if currentPage != 0:
							print("p>Page précédente")
						print(pgstring)
					for modid,mod in enumerate(pge):
						print(str(modid)+">"+mod["name"])
					print("Que voulez vous faire ? ")
					do = input("> ")
					if do.lower() == "q":
						Browse = False
					elif do.lower() == "p":
						if currentPage != 0:
							currentPage -= 1
						else:
							print("Vous êtes dèjà à la page 0")
					elif do.lower() == "n":
						if currentPage != nbpages-1:
							currentPage+= 1
						else:
							print("Vous êtes à la page maximum")
					else:
						try:
							do = int(do)
							assert do >= 0 and do < 10
						except:
							print("Nombre incorrect")
						else:
							modid = do+(currentPage*10)
							try:
								package = json.loads(functions.downloadPkgInfo("minecraft.zgalaxy.fr",mods[modid]["pkgurl"]).decode("UTF-8"))
							except:
								print("Impossible de récupérer le paquet.")
							else:
								mod = mods[modid]
								print("MOD : "+mod["name"])
								print("VERSION : "+package["version"])
								print("DESCRIPTION : "+mod["description"])
								print("URL du .PKG : "+mod["pkgurl"])
								print("POUR MINECRAFT "+package["requires"])
								print("SITE WEB : "+package["website"])
								print("DEPENDANCES : ")
								dep = package["dependencies"]
								for d in dep:
									print("> "+dep["name"])
								print("== Voulez vous installer ce mod [O/n] ? ==")
								char = input("> ")
								if char == "" or char.lower() == "o":
									print("Le mod va être installé. Patientez s'il vous plait...")
									modspath = home+"/.minecraft/"
									functions.installMod("minecraft.zgalaxy.fr", package, mcpath)
								else:
									print("Le mod ne sera pas installé.")

		else:
			Exec = False


print("Au revoir ! ")
