from tkinter import *
from tkinter.ttk import Notebook
import tkinter.ttk as ttk
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
import tkinter.messagebox as tkMessageBox
import time


class Interface(Frame):
    
    
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)
        self.nb_clic = 0
        
        # Préparation :
        self.home = expanduser("~")+mcpath
        self.settings = Settings(self.home)
        self.localDB = LocalRepository(self.home)
        self.UI = UserInteract.UserInteract()
        self.UI.setLocalDB(self.localDB)



        # Création de nos widgets
        self.notebook = Notebook()
        self.tabs = []
        i = 0
        while i < 7:
            tab = ttk.Frame()
            self.tabs.append(tab)
            i+=1

        self.repoTab()
        self.delModsTab()

        self.notebook.add(self.tabs[0], text='Dépôt')
        self.notebook.add(self.tabs[1], text='Versions de Minecraft', state="hidden")
        self.notebook.add(self.tabs[2], text='Installer Mods', state="hidden")
        self.notebook.add(self.tabs[3], text='Mettre à jour mods', state="hidden")
        self.notebook.add(self.tabs[4], text='Supprimer mods')
        self.notebook.add(self.tabs[5], text='Chercher mods', state="hidden")
        self.notebook.pack()
    
    # FONCTIONS DE SUPPRESSION


    def refreshModContent(self):
        # Actualise les listes de mods installés.
        self.delModsTab()

    def delModsTab(self):
        mods_o = self.localDB.getAllPackages()


        # Génération de la liste des mods installés
        self.installedMods = ttk.Treeview(self.tabs[4], selectmode="browse")
        self.installedMods['columns'] = ('version')
        self.installedMods.heading('version', text='Version Minecraft')
        self.installedMods.heading("#0", text='Nom du mod')
        
        # Insertion des mods installés et conversion en liste
        self.installedModsList = []
        for k,m in mods_o.items():
            m["key"] = k
            self.installedModsList.append(m)
            self.installedMods.insert('', 'end', text=m["name"], values=(m["mcver"]))

        self.installedMods.grid(column=0,row=0,columnspan=2)
        Button(self.tabs[4], text="Supprimer le mod", command=self.supprMod).grid(column=0,row=1)
        Button(self.tabs[4], text="Supprimer de la liste", command=self.supprFromDB).grid(column=1,row=1)

    def supprFromDB(self):
        mods = self.installedMods.selection()
        if len(mods) == 0:
            tkMessageBox.showwarning("Aucun mod à supprimer","Vous n'avez sélectionné aucun mods à supprimer.")
            return

        if not tkMessageBox.askyesno("Confirmer la suppression", "Voulez vous vraiment supprimer ce mod de la liste ? Il n'apparaitra plus dans la liste et ne pourra plus être mis à jour."):
            return

        modid = mods[0]
        index = self.installedMods.index(modid)
        mod = self.installedModsList[index]
        self.localDB.deletePackage(mod["key"])
        self.installedMods.delete(modid)
        self.installedModsList.pop(index)

        tkMessageBox.showinfo("Réussite","Le mod a bien été supprimé de la liste.")

    def supprMod(self):
        mods = self.installedMods.selection()
        if len(mods) == 0:
            tkMessageBox.showwarning("Aucun mod à supprimer","Vous n'avez sélectionné aucun mod à supprimer.")
            return

        if not tkMessageBox.askyesno("Confirmer la suppression", "Voulez vous vraiment supprimer ce mod ?"):
            return

        modid = mods[0]
        index = self.installedMods.index(modid)
        mod = self.installedModsList[index]
        self.installedModsList.pop(index)
        
        try:
            os.remove(self.home+"/mods/"+mod["mcver"]+"/"+mod["installname"])
        except:
            tkMessageBox.showerror("Erreur de suppression", "Une erreur s'est produite durant la suppression du fichier "+mod["installname"])
        else:
            self.localDB.deletePackage(mod["key"])
            self.installedMods.delete(modid)
            tkMessageBox.showinfo("Fin de la suppression","La suppression des mods s'est terminée, le mod "+mod["installname"]+" a bien été supprimé.")


    # CONNEXION AU DEPOT ET CHARGEMENT

    def repoTab(self):
        self.repoLine = StringVar()

        # Préparation
        repo = self.settings.getNode("repository")
        repoDirectory = self.settings.getNode("directory")
        if repo == False:
            url = "minecraft.zgalaxy.fr/"
        else:
            url = repo+repoDirectory
        self.repoLine.set(url)

        # Affichage des gros boutons sympas
        Label(self.tabs[0], text="Entrez l'adresse du dépôt : (sans le http://) ").grid(column=0,row=0,sticky=(W,E))

        repoLineEdit = Entry(self.tabs[0], textvariable=self.repoLine, width=30)
        repoLineEdit.grid(column=1, row=0, sticky=(W, E))

        repoButton = Button(self.tabs[0], text="Connexion", command=self.connectToRepo)
        repoButton.grid(column=2, row=0, sticky=(W, E))

        self.connStatus = Label(self.tabs[0], text="En attente.")
        self.connStatus.grid(column=0, row=1, columnspan=3)

        Frame(self).pack()

    def connectToRepo(self):
        repo = self.repoLine.get()

        self.log("Connecting to "+repo+"...")
        # On update la config du dépôt :
        repo = repo.split("/")
        serveur = ""
        dossier = "/"
        if len(repo) == 1:
            serveur = repo[0]
        elif len(repo) == 2:
            serveur = repo[0]
            dossier = repo[1]
        else:
            serveur = repo[0]
            for key,content in enumerate(repo):
                if key > 0:
                    dossier = dossier+content+"/"
        self.updateRepoConfig(serveur, dossier)

        # On se connecte au repository :
        self.repo = Remote(serveur, dossier, self.home, self.localDB)
        self.connStatus.configure(text="Tentative de mise à jour de la base de données...")

        rep, self.repContent = self.repo.updateList()
        if rep == False:
            self.connStatus.configure(text="Impossible d'atteindre le dépot. Erreur : "+self.repContent, fg="red")
        else:
            self.connStatus.configure(text="Base de données syncronisée.", fg="green")
            self.initTabs()


    def updateRepoConfig(self, repoSrv, repoDir):
        self.log("Updating repo config")
        self.settings.updateNode("repository",repoSrv)
        self.settings.updateNode("directory",repoDir)

    # INITIALISATION DES ONGLETS


    #######################################
    ##### Onglet "Versions Minecraft" #####
    #######################################

    def minecraftTab(self):
        self.mcVersions = ttk.Treeview(self.tabs[1], selectmode="browse")
        self.mcVersions.heading("#0", text='Nom du client')
        
        clients = self.repContent["clients"]
        self.mcVersionsList = []
        for k,c in clients.items():
            c["key"] = k
            self.mcVersionsList.append(c)
            self.mcVersions.insert('', 'end', text=c["name"])
        self.mcVersions.grid(row=0,column=0)

        infoFrame = LabelFrame(self.tabs[1],labelanchor="n",text="Informations :")
        infoFrame.grid(row=0,column=1,rowspan=3)
        self.versionInfo = Text(infoFrame)
        self.changeVersionsInfoText("Sélectionnez un client et cliquez sur \"Plus d'infos\"", False)
        self.versionInfo.config(state=DISABLED)
        self.versionInfo.pack()
        Button(self.tabs[1],text="Plus d'infos",command=self.showClientInfo).grid(row=1,column=0)
        Button(self.tabs[1],text="Installer",command=self.installClient).grid(row=2,column=0)

    def changeVersionsInfoText(self, text, delete=True):
        self.versionInfo.config(state=NORMAL)
        if delete:
            self.versionInfo.delete("1.0",END)
        self.versionInfo.insert(END, text)
        self.versionInfo.config(state=DISABLED) 

    def showClientInfo(self):
        # Récupération de la sélection :
        package = self.getClientInfo()
        if not package:
            return False

        self.changeVersionsInfoText("#====[Affichage des informations client]====#")
        self.changeVersionsInfoText("\nNOM DU CLIENT : "+package["name"], False)
        self.changeVersionsInfoText("\nVERSION : "+package["version"], False)
        self.changeVersionsInfoText("\nDESCRIPTION : "+package["description"], False)
        self.changeVersionsInfoText("\nURL du .PKG : "+package["pkgurl"], False)
        self.changeVersionsInfoText("\nNOM DU PAQUET : "+package["key"], False)

    def getClientInfo(self):
        sel = self.mcVersions.selection()
        if len(sel) == 0:
            tkMessageBox.showwarning("Aucune sélection","Vous n'avez sélectionné aucune version à afficher.")
            return False
        
        selectedClient = self.mcVersionsList[self.mcVersions.index(sel[0])]
        self.changeVersionsInfoText("Chargement des informations du client...")
        res, package = self.repo.downloadPkgInfo(selectedClient["pkgurl"])

        if not res:
            self.changeVersionsInfoText("Une erreur s'est produite, impossible de récupérer les infos du client. \nErreur : "+package)
            return False
        package["pkgurl"] = selectedClient["pkgurl"]
        package["key"] = selectedClient["key"]

        return package

    def installClient(self):
        package = self.getClientInfo()
        if not package:
            return False

        if not tkMessageBox.askyesno("Installer le client ?", "Voulez vous installer le client "+package["name"] +" ?"):
            self.changeVersionsInfoText("L'installation a été avortée.")
            return False

        self.changeVersionsInfoText("\nDébut de l'installation du client...", False)

        res = self.repo.installClient(package, self)
        self.changeVersionsInfoText("\nFin de l'installation. Résultat : ", False)
        if res == False:
            tkMessageBox.showerror("Erreur","Erreur : le client n'a pas été installé. Consultez le log pour plus d'informations.")
            self.changeVersionsInfoText("Echec...", False)
        else:
            tkMessageBox.showinfo("Réussite","Le client a bien été installé. Vous le trouverez dans votre launcher :)")
            self.changeVersionsInfoText("Réussite !", False)


    #####################################
    ##### Onglet "Télécharger Mods" #####
    #####################################

    def modsTab(self):
        # Liste des versions
        Label(self.tabs[2],text="Version du jeu :").grid(row=0,column=0)
        self.MODSMcVersions = Listbox(self.tabs[2])
        self.MODSMcVersionsList = []
        
        for verid, ver in self.repContent["mods"].items():
            ver["key"] = verid
            self.MODSMcVersionsList.append(ver)
            self.MODSMcVersions.insert(END,ver["version"])
        self.MODSMcVersions.grid(row=1,column=0)

        Button(self.tabs[2],text="Lister les mods",command=self.refreshModList).grid(row=2,column=0)

        infoFrame = LabelFrame(self.tabs[2],labelanchor="n",text="Informations :")
        infoFrame.grid(row=0,column=2,rowspan=3)
        self.modInfo = Text(infoFrame)
        self.changeModsInfoText("Sélectionnez une version et cliquez sur \"Lister les mods\"", False)
        self.modInfo.config(state=DISABLED)
        self.modInfo.pack()


    def refreshModList(self):
        frame = Frame(self.tabs[2])
        frame.grid(row=0,column=1, rowspan=3)
        self.mods = ttk.Treeview(frame, selectmode="browse")
        self.mods.heading("#0", text='Nom du mod')
        
        selVersionId = self.MODSMcVersions.curselection()
        if len(selVersionId) == 0:
            tkMessageBox.showwarning("Aucune sélection","Vous n'avez sélectionné aucune version à afficher.")
            return False

        try:
            mods = self.repContent["mods"][self.MODSMcVersionsList[self.MODSMcVersions.index(selVersionId)]["key"]]["mods"]
        except:
            tkMessageBox.showwarning("Erreur","Impossible de récupérer les mods pour la version choisie.")
            return False

        self.modsList = []
        for k,m in mods.items():
            m["key"] = k
            self.modsList.append(m)
            self.mods.insert('', 'end', text=m["name"])
        self.mods.pack()

        self.changeModsInfoText("Sélectionnez un mod et cliquez sur \"Plus d'infos\"")
        
        Button(frame,text="Plus d'infos",command=self.showModInfo).pack()
        Button(frame,text="Installer",command=self.installMod).pack()
        
    def changeModsInfoText(self, text, delete=True):
        self.modInfo.config(state=NORMAL)
        if delete:
            self.modInfo.delete("1.0",END)
        self.modInfo.insert(END, text)
        self.modInfo.config(state=DISABLED) 

    def showModInfo(self):
        # Récupération de la sélection :
        package = self.getModInfo()
        if not package:
            return False

        self.changeModsInfoText("#====[Affichage du mod : "+package["name"]+"]====#")
        self.UI.packageInfoShower(package, self)

    def getModInfo(self):
        sel = self.mods.selection()
        if len(sel) == 0:
            tkMessageBox.showwarning("Aucune sélection","Vous n'avez sélectionné aucun mod à afficher.")
            return False
        
        selectedMod = self.modsList[self.mods.index(sel[0])]
        self.changeModsInfoText("Chargement des informations du client...")
        res, package = self.repo.downloadPkgInfo(selectedMod["pkgurl"])

        if not res:
            self.changeModsInfoText("Une erreur s'est produite, impossible de récupérer les infos du mod. \nErreur : "+package)
            return False
        package["pkgurl"] = selectedMod["pkgurl"]
        package["key"] = selectedMod["key"]

        return package

    def installMod(self):
        package = self.getModInfo()
        if not package:
            return False

        if not tkMessageBox.askyesno("Installer le mod ?", "Voulez vous installer le mod "+package["name"] +" ?"):
            self.changeModsInfoText("L'installation a été avortée.")
            return False

        self.changeModsInfoText("\nDébut de l'installation du mod...", False)

        res = self.repo.installMod(package,False,[], self)
        self.changeModsInfoText("\nFin de l'installation. Résultat : ", False)
        if res == False:
            tkMessageBox.showerror("Erreur","Erreur : le mod n'a pas été installé. Consultez le log pour plus d'informations.")
            self.changeModsInfoText("Echec...", False)
        else:
            tkMessageBox.showinfo("Réussite","Le mod a bien été installé.")
            self.changeModsInfoText("Réussite !", False)

        self.refreshModContent()

    #######################################
    ##### Onglet "Mettre à jour mods" #####
    #######################################

    # Future feature : Mettre à jour les mods individuellement.
    def updatesTab(self):
        Button(self.tabs[3], text="Rechercher des mises à jour", command=self.showUpdates).grid(row=0,column=0)
        self.installUpdatesBtn = Button(self.tabs[3], text="Installer les mises à jour", command=self.installUpdates, state=DISABLED)
        self.installUpdatesBtn.grid(row=0,column=1)


        # Initialisation du log
        infoFrame = LabelFrame(self.tabs[3],labelanchor="n",text="Logs :")
        infoFrame.grid(row=0,column=2,rowspan=2)
        self.updateInfo = Text(infoFrame)
        self.changeUpdatesInfoText("Recherchez des mises à jour puis cliquez sur \"Installer les Mises à jour\" pour lancer l'installation.", False)
        self.updateInfo.config(state=DISABLED)
        self.updateInfo.pack()

    def showUpdates(self):
        self.changeUpdatesInfoText("Chargement de la liste de mods...")
        self.installUpdatesBtn.config(state=NORMAL)
        liste = ttk.Treeview(self.tabs[3], selectmode="browse")
        liste['columns'] = ('mcversion','newversion')
        liste.heading('mcversion', text='Version Minecraft')
        liste.heading('newversion', text='Version Mod')
        liste.heading("#0", text='Nom du mod')
        toupdate = self.repo.updateMods(False, self)
        print(str(toupdate))
        for up in toupdate:
            liste.insert('', 'end', text=up["name"], values=up["mcver"]+" "+up["version"])
        liste.grid(row=1,column=0,columnspan=2)

        return toupdate

    def installUpdates(self):
        toupdate = self.showUpdates()
        time.sleep(0.5)
        self.changeUpdatesInfoText("Application des mises à jour...")
        for package in toupdate:
            self.changeUpdatesInfoText("\n> Mise à jour de "+package["name"]+" vers la version "+package["version"])
            self.repo.installMod(package,False,[],self,"Update")


    def changeUpdatesInfoText(self, text, delete=True):
        self.updateInfo.config(state=NORMAL)
        if delete:
            self.updateInfo.delete("1.0",END)
        self.updateInfo.insert(END, text)
        self.updateInfo.config(state=DISABLED) 

    ####################################
    ##### Onglet "rechercher mods" #####
    ####################################

    def searchTab(self):
        Label(self.tabs[5],text="Rechercher :").grid(row=0,column=0)
        self.searchLine = StringVar()
        Entry(self.tabs[5],textvariable=self.searchLine, width=30).grid(row=0, column=1)

        Button(self.tabs[5],text="Lancer la recherche",command=self.research).grid(row=0,column=2)

        self.searchInfoFrame = LabelFrame(self.tabs[5],labelanchor="n",text="Informations :")
        self.searchInfoFrame.grid(row=1,column=0,columnspan=3, rowspan=3)
        self.searchInfo = Text(self.searchInfoFrame)
        self.changeSearchInfoText("Effectuez une recherche.", False)
        self.searchInfo.config(state=DISABLED)
        self.searchInfo.pack()

    def research(self):
        # Vérifions le contenu du label #
        keyword = self.searchLine.get()
        if len(keyword) == 0:
            tkMessageBox.showerror("Aucune recherche", "Impossible de lancer la recherche : aucun mot clé entré.")
            return

        self.searchInfoFrame.grid(column=1, columnspan=2)

        self.searchResults = ttk.Treeview(self.tabs[5], selectmode="browse")
        self.searchResults.grid(row=1, column=0)
        self.searchResults["columns"] = ("version")
        self.searchResults.heading("#0", text='Nom du mod')
        self.searchResults.heading("version", text='Version minecraft')
        Button(self.tabs[5], text="Voir le mod", command=self.showSearchResult).grid(column=0, row=2)
        Button(self.tabs[5], text="Installer le mod", command=self.installSearchResult).grid(column=0, row=3)

        results = self.repo.search(keyword, self)
        self.searchResultsList = []
        for res in results:
            self.searchResults.insert("", "end", text=res["name"], values=(res["version"]))
            self.searchResultsList.append(res)


    def showSearchResult(self):
        package = self.getSearchItemInfo()
        if not package:
            return False

        self.changeSearchInfoText("#====[Affichage du mod : "+package["name"]+"]====#")
        self.UI.packageInfoShower(package, self, "Search")

    def getSearchItemInfo(self):
        sel = self.searchResults.selection()
        if len(sel) == 0:
            tkMessageBox.showwarning("Aucune sélection","Vous n'avez sélectionné aucun mod à afficher.")
            return False
        
        selectedMod = self.searchResultsList[self.searchResults.index(sel[0])]
        self.changeSearchInfoText("Chargement des informations du mod...")
        rep, selectedMod = self.repo.getPackage(selectedMod["pkname"],selectedMod["version"])
        if rep == False:
            self.changeSearchInfoText("Une erreur s'est produite, impossible de trouver le paquet. \nErreur : "+selectedMod)
            return False

        res, package = self.repo.downloadPkgInfo(selectedMod["pkgurl"])

        if not res:
            self.changeSearchInfoText("Une erreur s'est produite, impossible de récupérer les infos du mod. \nErreur : "+package)
            return False
        package["pkgurl"] = selectedMod["pkgurl"]

        return package
        
    def changeSearchInfoText(self, text, delete=True):
        self.searchInfo.config(state=NORMAL)
        if delete:
            self.searchInfo.delete("1.0",END)
        self.searchInfo.insert(END, text)
        self.searchInfo.config(state=DISABLED) 

    

    def installSearchResult(self):
        package = self.getSearchItemInfo()
        if not package:
            return False

        if not tkMessageBox.askyesno("Installer le mod ?", "Voulez vous installer le mod "+package["name"] +" ?"):
            self.changeSearchInfoText("L'installation a été avortée.")
            return False

        self.changeSearchInfoText("\nDébut de l'installation du mod...", False)

        res = self.repo.installMod(package,False,[], self, "Search")
        self.changeSearchInfoText("\nFin de l'installation. Résultat : ", False)
        if res == False:
            tkMessageBox.showerror("Erreur","Erreur : le mod n'a pas été installé. Consultez le log pour plus d'informations.")
            self.changeSearchInfoText("Echec...", False)
        else:
            tkMessageBox.showinfo("Réussite","Le mod a bien été installé.")
            self.changeSearchInfoText("Réussite !", False)

        self.refreshModContent()

    ######################################
    ##### Initialisateur des onglets #####
    ######################################

    def initTabs(self):
        self.notebook.tab(1, state="normal")
        self.notebook.tab(2, state="normal")
        self.notebook.tab(3, state="normal")
        self.notebook.tab(5, state="normal")

        self.minecraftTab()
        self.modsTab()
        self.updatesTab()
        self.searchTab()
        # JE ME SUIS ARRETE A : afficher les tabs
        # IL ME FAUT FAIRE : Initialiser les treeviews, les remplir, ajouter les boutons d'action
        # Ainsi que : assurer le bon fonctionnement du no-ui
        

    def refreshLists(self):
        print("l")


    def log(self, message, type = "STDOUT"):
        print("["+type+"] "+message)


