from DownloadManager import *
import tkinter.ttk as ttk
from tkinter import *
import tkinter.messagebox as tkMessageBox

class SearchTab(DownloadManager):

    def initTab(self):
        Label(self.parent.tabs[5],text="Rechercher :").grid(row=0,column=0)
        self.searchLine = StringVar()
        Entry(self.parent.tabs[5],textvariable=self.searchLine, width=30).grid(row=0, column=1)

        Button(self.parent.tabs[5],text="Lancer la recherche",command=self.research).grid(row=0,column=2)

    def research(self):
        # Vérifions le contenu du label #
        keyword = self.searchLine.get()
        if len(keyword) == 0:
            tkMessageBox.showerror("Aucune recherche", "Impossible de lancer la recherche : aucun mot clé entré.")
            return

        

        self.searchResults = ttk.Treeview(self.parent.tabs[5], selectmode="browse")
        self.searchResults.grid(row=1, column=1)
        self.searchResults["columns"] = ("version")
        self.searchResults.heading("#0", text='Nom du mod')
        self.searchResults.heading("version", text='Version minecraft')
        Button(self.parent.tabs[5], text="Voir le mod", command=self.showSearchResult).grid(column=1, row=2)
        Button(self.parent.tabs[5], text="Installer le mod", command=self.installSearchResult).grid(column=1, row=3)

        results = self.parent.remote.search(keyword)
        self.searchResultsList = []
        for res in results:
            self.searchResults.insert("", "end", text=res["name"], values=(res["version"]))
            self.searchResultsList.append(res)


    def showSearchResult(self):
        package = self.getSearchItemInfo()
        if not package:
            return False

        self.appendConsole("#====[Affichage du mod : "+package["name"]+"]====#")
        self.parent.UI.packageInfoShower(package, self)

    def getSearchItemInfo(self):
        sel = self.searchResults.selection()
        if len(sel) == 0:
            tkMessageBox.showwarning("Aucune sélection","Vous n'avez sélectionné aucun mod à afficher.")
            return False
        
        selectedMod = self.searchResultsList[self.searchResults.index(sel[0])]
        self.appendConsole("Chargement des informations du mod...")
        rep, selectedMod = self.parent.remote.getPackage(selectedMod["pkname"],selectedMod["version"])
        if rep == False:
            self.appendConsole("Une erreur s'est produite, impossible de trouver le paquet. \nErreur : "+selectedMod)
            return False

        res, package = self.parent.remote.downloadPkgInfo(selectedMod["pkgurl"])

        if not res:
            self.appendConsole("Une erreur s'est produite, impossible de récupérer les infos du mod. \nErreur : "+package)
            return False
        package["pkgurl"] = selectedMod["pkgurl"]

        return package
        
    def changeSearchInfoText(self, text, delete=True):
        self.appendConsole(text)

    

    def installSearchResult(self):
        package = self.getSearchItemInfo()
        if not package:
            return False

        if not tkMessageBox.askyesno("Installer le mod ?", "Voulez vous installer le mod "+package["name"] +" ?"):
            self.appendConsole("L'installation a été avortée.")
            return False

        self.appendConsole("\nDébut de l'installation du mod...", False)

        res = self.download(package)

        self.parent.refreshModContent()