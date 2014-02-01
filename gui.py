from tkinter import *
from tkinter.ttk import Notebook
import tkinter.ttk as ttk
from config import *
from os.path import expanduser
from LocalRepository import *
from Settings import *
import Remote as rem
import functions
import json
import math
import sys, getopt
import os
import UserInteract
import tkinter.messagebox as tkMessageBox
import time
from VersionsTab import *
from ModsTab import *


class Interface(Frame):
    
    
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=800, height=576, **kwargs)
        self.pack(fill=BOTH)
        self.fenetre = fenetre
        #
        # Récupération des variables à la con
        #
        self.home = expanduser("~")+mcpath
        self.settings = Settings(self.home)
        self.localDB = LocalRepository(self.home)
        self.UI = UserInteract.UserInteract()
        self.UI.setLocalDB(self.localDB)

        #
        # Création du notebook
        #
        self.notebook = Notebook(self, height=576)
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
        self.notebook.pack(side="left")

        #
        # Création de la zone de logging
        #

        logsFrame = LabelFrame(self, labelanchor="n",text="Logs :", height=576, width=400)
        logsFrame.pack(side="right", fill=BOTH)
        self.logs = Text(logsFrame, width=55, height=30)
        self.logs.grid(row = 0, column = 0, columnspan = 2)

        self.stateLabel = Label(logsFrame, text="En attente",anchor=NW, justify=LEFT)
        self.stateLabel.grid(row=1,column=0,columnspan=2)
        self.progressBar = ttk.Progressbar(logsFrame, length=350)
        self.progressBar.grid(row=2,column=0)
        self.progressVal = IntVar()
        self.progressBar.config(variable = self.progressVal)
        self.progLabel = Label(logsFrame,text="0%", justify=LEFT, anchor=W)
        self.progLabel.grid(row=2,column=1)


    #
    # Fonction de logging
    #
    def appendConsole(self, text, delete=False):
        self.logs.config(state=NORMAL)
        # À utiliser avec modération
        if delete:
            self.logs.delete("1.0",END)
        self.logs.insert(END, text)
        self.logs.config(state=DISABLED)
        self.logs.yview(END)

    #
    # Fonction de mise à jour de la progression
    #
    def setProgressValue(self, val, maxVal):
        v = (val/maxVal)*100
        self.progressVal.set(v)
        self.progLabel.config(text=str(math.floor(v))+"%")

    #
    # Modification du statustext
    #
    def setStateText(self, text, color="black"):
        self.stateLabel.config(text=text,fg=color)


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
        self.remoteLine = StringVar()

        # Préparation
        repo = self.settings.getNode("repository")
        repoDirectory = self.settings.getNode("directory")
        if repo == False:
            url = "minecraft.zgalaxy.fr/"
        else:
            url = repo+repoDirectory
        self.remoteLine.set(url)

        # Affichage des gros boutons sympas
        Label(self.tabs[0], text="Entrez l'adresse du dépôt : (sans le http://) ").grid(column=0,row=0,sticky=(W,E))

        repoLineEdit = Entry(self.tabs[0], textvariable=self.remoteLine, width=30)
        repoLineEdit.grid(column=1, row=0, sticky=(W, E))

        repoButton = Button(self.tabs[0], text="Connexion", command=self.connectToRepo)
        repoButton.grid(column=2, row=0, sticky=(W, E))

        self.connStatus = Label(self.tabs[0], text="En attente.")
        self.connStatus.grid(column=0, row=1, columnspan=3)

        Frame(self).pack()

    def connectToRepo(self):
        repo = self.remoteLine.get()

        self.appendConsole("Connexion à "+repo+"...")
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
        self.remote = rem.Remote(serveur, dossier, self.home, self.localDB, True, gui_parent = self)
        self.appendConsole("\nMise à jour de la base de données...")

        rep, self.repContent = self.remote.updateList()
        if rep == False:
            print(self.repContent)
            self.connStatus.configure(text="Impossible d'atteindre le dépot. Erreur : "+self.repContent, fg="red")
        else:
            self.connStatus.configure(text="Connexion réussie.", fg="green")
            self.appendConsole("\nBase de données mise à jour...")
            self.initTabs()


    def updateRepoConfig(self, repoSrv, repoDir):
        self.settings.updateNode("repository",repoSrv)
        self.settings.updateNode("directory",repoDir)

    def initTabs(self):
        self.notebook.tab(1, state="normal")
        self.notebook.tab(2, state="normal")
        self.notebook.tab(3, state="normal")
        self.notebook.tab(5, state="normal")
        
        modsTab = ModsTab(self)
        modsTab.initTab()
        versTab = VersionsTab(self)
        versTab.initTab()
"""

    ######################################
    ##### Initialisateur des onglets #####
    ######################################



        self.minecraftTab()
        self.modsTab()
        self.updatesTab()
        self.searchTab()
        

    def refreshLists(self):
        print("l")


    def log(self, message, type = "STDOUT"):
        print("["+type+"] "+message)"""


