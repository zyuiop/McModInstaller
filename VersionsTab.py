from DownloadManager import *
import tkinter.ttk as ttk
from tkinter import *
import tkinter.messagebox as tkMessageBox

# VersionsTab : gestion de l'onglet des versions de MC
class VersionsTab(DownloadManager):
    # Pas de INIT : on utilise celui du parent

    def initTab(self):
        self.versions = ttk.Treeview(self.parent.tabs[1], selectmode="browse")
        self.versions.heading("#0", text='Nom du client')
        
        clients = self.parent.repContent["clients"]
        self.versionsList = []
        for k,c in clients.items():
            c["key"] = k
            self.versionsList.append(c)
            self.versions.insert('', 'end', text=c["name"])
        self.versions.grid(row=0,column=0)

        self.infosBtn = Button(self.parent.tabs[1],text="Plus d'infos",command=self.showInfo)
        self.infosBtn.grid(row=1,column=0)
        self.installBtn = Button(self.parent.tabs[1],text="Installer",command=self.install)
        self.installBtn.grid(row=2,column=0)


    def showInfo(self):
        # Récupération de la sélection :
        package = self.getClientInfo()
        if not package:
            return False

        self.appendConsole("\n#====[Affichage des informations client]====#")
        self.appendConsole("NOM DU CLIENT : "+package["name"], False)
        self.appendConsole("VERSION : "+package["version"], False)
        self.appendConsole("DESCRIPTION : "+package["description"], False)
        self.appendConsole("URL du .PKG : "+package["pkgurl"], False)
        self.appendConsole("NOM DU PAQUET : "+package["key"], False)

    def getClientInfo(self):
        
        sel = self.versions.selection()
        if len(sel) == 0:
            tkMessageBox.showwarning("Aucune sélection","Vous n'avez sélectionné aucune version à afficher.")
            return False
        
        selectedClient = self.versionsList[self.versions.index(sel[0])]
        self.appendConsole("\nChargement des informations du client...")
        res, package = self.parent.remote.downloadPkgInfo(selectedClient["pkgurl"])

        if not res:
            self.appendConsole("Une erreur s'est produite, impossible de récupérer les infos du client. \nErreur : "+package)
            return False
        package["pkgurl"] = selectedClient["pkgurl"]
        package["key"] = selectedClient["key"]

        return package

    def install(self):
        package = self.getClientInfo()
        if not package:
            return False

        if not tkMessageBox.askyesno("Installer le client ?", "Voulez vous installer le client "+package["name"] +" ?"):
            self.appendConsole("L'installation a été avortée.")
            return False

        self.appendConsole("\nDébut de l'installation du client.", False)
        self.installBtn.config(state=DISABLED)
        self.infosBtn.config(state=DISABLED)
        self.download(package)
        self.installBtn.config(state=NORMAL)
        self.infosBtn.config(state=NORMAL)
