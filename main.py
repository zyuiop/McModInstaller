# CONFIGURATION !!!
appdata = ""
# Décommentez la ligne ci dessous pour le programme WINDOWS :
# appdata = "AppData/Roaming"

import functions
import json
import math
from os.path import expanduser
home = expanduser("~")+appdata
import os

from LocalRepository import *
from Settings import *

settingsManager = Settings(home)
localDB = LocalRepository(home)

print("Minecraft Mods Installer - Version 0.2a")
Exec = True


repo = settingsManager.getNode("repository")
repoDirectory = settingsManager.getNode("directory")
if repo == False:
	print("Aucun dépôt configuré. Merci d'indiquer le serveur de dépôt (Attention : seuls les serveurs peuvent être renseignés. Exemple : repo.example.com ou alors example.com sont VALIDES. example.com/repo n'est PAS VALIDE)")
	repo, repoDirectory = functions.inputDepot()
	settingsManager.addNode("repository",repo)
	settingsManager.addNode("directory",repoDirectory)

if repoDirectory == False:
	repoDirectory = "/"

from Remote import *
depot = Remote(repo, repoDirectory, home+"/.minecraft", localDB)

# Récupération de la liste 
print("Connection au dépôt \""+repo+repoDirectory+"\"")
print("Mise à jour de la base de donnée de paquets... Ceci peut prendre quelques instants")
repo = depot.updateList()
if not repo:
	print("[ERREUR FATALE] Impossible de se connecter au dépôt. Souhaitez vous le changer ?")
	choice = input("Changer de dépôt ? [o/N] ")
	if choice.lower() == "o":
		repo, repoDirectory = functions.inputDepot()
		settingsManager.updateNode("repository",repo)
		settingsManager.updateNode("directory",repoDirectory)
		print("Le dépôt a été modifié. Relancez le programme pour vous y connecter.")
		Exec = False
	else:
		Exec = False

if Exec:
	print("Vous êtes bien connecté au dépôt \""+repo["repo"]+"\"")

# Boucle ppale
while Exec:
	print("")
	print("#=====[Menu principal]=====#")
	print("0 : Quitter le programme")
	print("1 : Gestion des versions de Minecraft")
	print("2 : Installer des Mods")
	print("3 : Mettre à jour les mods")
	print("4 : Supprimer des mods")
	print("5 : Afficher l'aide")
	print("6 : Changer de dépôt")
	try:
		choix = int(input("Choix (Nombre) : "))
		assert choix >= 0 and choix < 7
	except:
		print("Choix non valide, merci de recommencer")
	else:
		if choix == 5:
			print("Aide du MCMod Installer")
			print("La première chose à faire est d'installer un client custom. Le client le plus moddé est le client FML (Forge Mod Loader). Allez donc dans 'Clients' puis sélectionnez le client FML de votre version")
			print("Ensuite, installez des mods. Pour cela, rendez vous dans ''mods'' et sélectionnez la version du jeu que vous souhaitez modder. Ensuite, choisissez votre mod !")
		elif choix == 6:
			repo, repoDirectory = functions.inputDepot()
			settingsManager.updateNode("repository",repo)
			settingsManager.updateNode("directory",repoDirectory)
			print("Le dépôt a été modifié. Relancez le programme pour vous y connecter.")
			Exec = False
		elif choix == 3:
			print("> Préparation de la mise à jour de tous les mods...")
			pkgs = localDB.getAllPackages()
			toupdate = []
			print("> Vérification des mises à jour disponibles...")
			for reponame, package in pkgs.items():
				print(">> Vérification des mises à jour de "+package["name"])
				rep = depot.downloadPkgInfo(reponame)
				if rep == False:
					print(">> Impossible de vérifier la version du paquet (Erreur réseau)")
				else:
					if rep["version"] > package["version"]:
						rep["pkgurl"] = package["pkgurl"]
						toupdate.append(rep)
						print(">> Mise à jour disponible.")
					else:
						print(">> Non mis à jour")

			if len(toupdate) == 0:
				print("")
				print("AUCUNE MISE A JOUR DISPONIBLE.")
			else:
				print("Il y a "+str(len(toupdate))+" mises à jour à installer.")
				print("Voulez vous les installer ?")
				ch = input("[O/n] ")
				if ch.lower() == "o" or ch.lower() == "":
					for package in toupdate:
						print("> Mise à jour de "+package["name"])
						print("> Récupération du mod...")
						if not depot.installMod(package):
							print("> Erreur de mise à jour.")
						else:
							print("> Mise à jour du mod effectuée.")
		elif choix == 4:
			mods_o = localDB.getAllPackages()
			nbpages = math.ceil(len(mods_o)/10)
			
			i = 0
			currentPage = 0
			Browse = True
			mods = []
			for k,m in mods_o.items():
				m["key"] = k
				mods.append(m)

			pages = []
			while i < nbpages:
				i+=1
				pages.append(mods[10*(i-1):10*i])

			
			while Browse:
				pge = pages[currentPage]
				print("#====[Mods installés]====#")
				print("# Page n° "+str(currentPage+1)+"/"+str(nbpages))
				print("n° : Description")
				print("q : Retour au menu")
				
				if nbpages > 1:
					if currentPage != nbpages-1:
						print("n : Page suivante")
					if currentPage != 0:
						print("p : Page précédente")
					print(pgstring)

					
				for modid, mod in enumerate(pge):
					print(str(modid)+" : "+mod["name"] +"(MC "+mod["mcver"]+")")


				print("Action à effectuer ? ")
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
						assert do in pge
					except:
						print("Nombre incorrect")
					else:
						modid = do+(currentPage*10)
						mod = mods[modid]
						print("#====[Affichage du mod : "+mod["name"]+"]====#")
						print("VERSION : "+mod["version"])
						print("POUR MINECRAFT "+mod["requires"])
						print("== Voulez vous désinstaller ce mod ? ==")
						char = input("[O/n] ")
						if char == "" or char.lower() == "o":
							print("Le mod va être désinstallé. Patientez s'il vous plait...")
							try:
								os.remove(home+"/.minecraft/mods/"+mod["mcver"]+"/"+mod["installname"])
							except OSError:
								print("[ERREUR] Le fichier est un dossier")
							except:
								print("[ERREUR] Impossible de désinstaller le mod")
							else:
								print("Le mod a été supprimé")
							localDB.deletePackage(mod["key"])
							pages[currentPage].pop(modid)
							print("")
		elif choix == 1:
			print("")
			print("#====[Clients disponibles sur le dépôt]====#")
			clients = repo["clients"]
			print("n° : Nom du client")
			for clid, cl in enumerate(clients):
				print(str(clid)+" : "+cl["name"])
			print(">> Voir des détails à propos du client n° ?")
			try:
				num = int(input(">> "))
				assert num >= 0 and num < len(clients)
			except:
				print("Erreur : ce client n'a pas été trouvé !")
			else:
				sel_cl = clients[num]
				package = depot.downloadPkgInfo(sel_cl["pkgurl"])
				if package == False:
					print("[ERREUR RESEAU] Impossible de récupérer le paquet.")
				else:
					print("#====[Affichage client : "+sel_cl["name"]+"]====#")
					print("VERSION : "+package["version"])
					print("DESCRIPTION : "+sel_cl["description"])
					print("URL du .PKG : "+sel_cl["pkgurl"])
					print("")
					print(">> Voulez vous installer ce client ?")
					char = input("[O/n] ")
					if char == "" or char.lower() == "o":
						print("Le client va être installé. Patientez s'il vous plait...")
						mcpath = home+"/.minecraft/"
						depot.installClient(package)
					else:
						print("Le client ne sera pas installé. Retour au menu")

		elif choix == 2:
			print("#====[Choisir une version de Minecraft]====#")
			mcpath = home+"/.minecraft/"
			versions = repo["mods"]
			print("n° : Nom de version")
			for verid, ver in enumerate(versions):
				print(str(verid)+" : "+ver["version"])

			print(">> Choix ?")
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
					print("#====[Affichage des mods]====#")
					print("# Page n° "+str(currentPage+1)+"/"+str(nbpages))
					print("n° : Description")
					print("q : Retour au menu")
					if nbpages > 1:
						if currentPage != nbpages-1:
							print("n : Page suivante")
						if currentPage != 0:
							print("p : Page précédente")
						print(pgstring)


					for modid,mod in enumerate(pge):
						print(str(modid)+" : "+mod["name"])

					print("Action à effectuer ? ")
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
								package = depot.downloadPkgInfo(mods[modid]["pkgurl"])
							except:
								print("Impossible de récupérer le paquet...")
							else:
								mod = mods[modid]
								print("#====[Affichage du mod : "+mod["name"]+"]====#")
								print("VERSION : "+package["version"])
								print("DESCRIPTION : "+mod["description"])
								print("URL du .PKG : "+mod["pkgurl"])
								print("POUR MINECRAFT "+package["requires"])
								print("SITE WEB : "+package["website"])
								print("DEPENDANCES : ")
								for dep in package["dependencies"]:
									print(" -> "+dep["name"])

								print("== Voulez vous installer ce mod ? ==")
								char = input("[O/n] ")
								if char == "" or char.lower() == "o":
									package["pkgurl"] = mod["pkgurl"]
									print("Le mod va être installé. Patientez s'il vous plait...")
									modspath = home+"/.minecraft/"
									depot.installMod(package)
									print("")
								else:
									print("Le mod ne sera pas installé.")

		else:
			Exec = False


print("Au revoir ! ")
