from config import *
from os.path import expanduser
from LocalRepository import *
from Settings import *
from Remote import *
import functions
import json
import math
import sys, getopt
import os
import UserInteract

# INITIALISATION DE CERTAINES CLASSES UTILES
home = expanduser("~")+mcpath
settingsManager = Settings(home)
localDB = LocalRepository(home)
UI = UserInteract.UserInteract()


# ANALYSE DES ARGUMENTS
args = sys.argv[1:]
if len(args) > 0:
	try:
		opts, args = getopt.getopt(sys.argv[1:],"uhm:v:p:c:",["update","help","mod=","version=","package=","client=","noconfirm"])
	except getopt.GetoptError:
		print("Unknown argument. Try --help for help")
	else:
		from Args import *
		cl = Args(localDB, settingsManager, home, opts, sys.argv[1:])
		cl.execute()
	exit()


# Program start
print("Minecraft Mods Installer - Version "+version)
Exec = True


# Connexion au dépôt
# 1. Récup de la configuration
repo = settingsManager.getNode("repository")
repoDirectory = settingsManager.getNode("directory")

# 2. Si non configuré, on demande à l'utilisateur de configurer
if repo == False:
	print("Aucun dépôt n'a été renseigné.")
	repo, repoDirectory = UI.inputDepot()
	settingsManager.addNode("repository",repo)
	settingsManager.addNode("directory",repoDirectory)

if repoDirectory == False:
	repoDirectory = "/"


# 3. Initialisation de la classe dépot avec les paramètres
oldrepo = repo
while True:
	depot = Remote(oldrepo, repoDirectory, home, localDB)

	# 4. Récupération de la liste des oaqyets
	print("Mise à jour de la base de donnée de paquets depuis 'http://"+oldrepo+repoDirectory+"'... Ceci peut prendre quelques instants")
	repo = depot.updateList()

	# 5. Vérification des erreurs
	if not repo:
		print("!!! ERREUR : Impssible de se connecter au dépôt..")
		if UI.yesNoQuestion("Voulez vous changer de dépôt ?", True):
			repo, repoDirectory = UI.inputDepot()
			settingsManager.updateNode("repository",repo)
			settingsManager.updateNode("directory",repoDirectory)
		else:
			print("Fermeture du programme.")
			exit()
	else:
		break

# 6. Validation de la connexion
if Exec:
	print("Vous êtes bien connecté au dépôt \""+repo["repo"]+"\"")

# Boucle principale
while Exec:
	print("")
	choix = UI.mainMenu()
	if choix == 5:
		# Aide
		print("Aide du MCMod Installer")
		print("La première chose à faire est d'installer un client custom. Le client le plus moddé est le client FML (Forge Mod Loader). Allez donc dans 'Clients' puis sélectionnez le client FML de votre version")
		print("Ensuite, installez des mods. Pour cela, rendez vous dans ''mods'' et sélectionnez la version du jeu que vous souhaitez modder. Ensuite, choisissez votre mod !")
	
	elif choix == 0:
		Exec = False

	elif choix == 6:
		# Modification du dépot
		repo, repoDirectory = UI.inputDepot()
		settingsManager.updateNode("repository",repo)
		settingsManager.updateNode("directory",repoDirectory)
		print("Le dépôt a été modifié. Relancez le programme pour vous y connecter.")
		Exec = False
	
	elif choix == 3:
		depot.updateMods()
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
					assert do < len(pge)
				except:
					print("Nombre incorrect")
				else:
					modid = do+(currentPage*10)
					mod = mods[modid]
					print("#====[Affichage du mod : "+mod["name"]+"]====#")
					print("VERSION : "+mod["version"])
					print("POUR MINECRAFT "+mod["requires"])
					print("NOM DU PACKET : "+mod["key"])
					print("== Voulez vous désinstaller ce mod ? ==")
					char = input("[O/n] ")
					if char == "" or char.lower() == "o":
						print("Le mod va être désinstallé. Patientez s'il vous plait...")
						try:
							os.remove(home+"/mods/"+mod["mcver"]+"/"+mod["installname"])
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
		clients_o = repo["clients"]
		clients = []
		#Conversion du DICTIONNAIRE clients_o en LISTE
		for k,c in clients_o.items():
			c["key"] = k
			clients.append(c)
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
			print("> Récupération des infos du paquet...")
			package = depot.downloadPkgInfo(sel_cl["pkgurl"])
			if package == False:
				print("[ERREUR RESEAU] Impossible de récupérer le paquet.")
			else:
				print("#====[Affichage client : "+sel_cl["name"]+"]====#")
				print("VERSION : "+package["version"])
				print("DESCRIPTION : "+package["description"])
				print("URL du .PKG : "+sel_cl["pkgurl"])
				print("NOM DU PAQUET : "+sel_cl["key"])
				print("")
				print(">> Voulez vous installer ce client ?")
				char = input("[O/n] ")
				if char == "" or char.lower() == "o":
					print("Le client va être installé. Patientez s'il vous plait...")
					depot.installClient(package)
				else:
					print("Le client ne sera pas installé. Retour au menu")
	elif choix == 2:
		print("#====[Choisir une version de Minecraft]====#")
		versions = repo["mods"]

		print("ID : Nom de version")
		for verid, ver in versions.items():
			print(str(verid)+" : "+ver["version"])
		print(">> Choix (ID) ?")
		try:
			num = input("> ")
			assert num in versions.keys()
		except:
			print("Erreur : cet ID de version n'existe pas !")
		else:
			print(">> Récupération de la liste de mods pour la version "+versions[num]["version"]+" <<")
			
			mods_o = versions[num]["mods"]
			mods = []
			# Conversion en liste
			for k,m in mods_o.items():
				m["key"] = k
				mods.append(m)
			
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
						package = depot.downloadPkgInfo(mods[modid]["pkgurl"])
						if package == False:
							print("Impossible de récupérer le paquet...")
						else:
							mod = mods[modid]
							packageName = localDB.packageName(package["package_name"], package["mc_version"])
							print("#====[Affichage du mod : "+mod["name"]+"]====#")
							print("VERSION : "+package["version"])
							print("NOM PAQUET : "+packageName)
							print("DESCRIPTION : "+package["description"])
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
								depot.installMod(package)
								print("")
							else:
								print("Le mod ne sera pas installé.")

print("Au revoir ! ")
