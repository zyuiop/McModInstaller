from DownloadManager import *
import tkinter
class ModsTab(DownloadManager):
    def initTab(self):
        Label(self.parent.tabs[2],text="Version du jeu :").grid(row=0,column=0)
        self.MODSMcVersions = Listbox(self.parent.tabs[2])
        self.MODSMcVersionsList = []

        for verid, ver in self.parent.repContent["mods"].items():
            ver["key"] = verid
            self.MODSMcVersionsList.append(ver)
            self.MODSMcVersions.insert(END, ver["version"])
        self.MODSMcVersions.grid(row=1,column=0)

        self.listButton = Button(self.parent.tabs[2],text="Lister les mods",command=self.refreshModList)
        self.listButton.grid(row=2,column=0)

    def refreshModList(self):
        frame = Frame(self.parent.tabs[2])
        frame.grid(row=0,column=1,rowspan=3)
        self.mods = tkinter.ttk.Treeview(frame, selectmode="browse")
        self.mods.heading("#0", text="Nom du mod")

        selVersionId = self.MODSMcVersions.curselection()
        if len(selVersionId) == 0:
            tkinter.messagebox.showwarning('Aucune sélection', "Vous n'avez sélectionné aucune version à afficher")
            return False

        try:
            mods = self.parent.repContent['mods'][self.MODSMcVersionsList[self.MODSMcVersions.index(selVersionId)]["key"]]["mods"]
        except:
            tkinter.messagebox.showwarning("Erreur", "Impossible de récupérer les mods la version demandée.")
            return False

        self.modsList = []
        for k,m in mods.items():
            m["key"] = k
            self.modsList.append(m)
            self.mods.insert('', 'end', text=m["name"])
        self.mods.pack()
        self.showButton = Button(frame,text="Plus d'infos", command=self.showModInfo)
        self.showButton.pack()
        self.instButton = Button(frame,text="Installer", command=self.installMod)
        self.instButton.pack()
        
    def showModInfo(self):
        package = self.getModInfo()
        if not package:
            return False
        self.appendConsole("\n#===[Informations sur : " + package["name"] + "]====#")
        self.parent.UI.packageInfoShower(package, self)

    def getModInfo(self):
        sel = self.mods.selection()
        if len(sel) == 0:
            tkinter.messagebox.showwarning("Aucune sélection", "Vous n'avez sélectionné aucun mod.")
            return False
        selectedMod = self.modsList[self.mods.index(sel[0])]
        self.appendConsole("Chargement des informations du client")
        res, package = self.parent.remote.downloadPkgInfo(selectedMod["pkgurl"])

        if not res:
            self.appendConsole("Erreur, impossible de récupérer les informations. Erreur : " + package)
            return False
        package["pkgurl"] = selectedMod["pkgurl"]
        package["key"] = selectedMod["key"]
        return package

    def installMod(self):
        package = self.getModInfo()
        if not package:
            return False

        if not tkinter.messagebox.askyesno("Installer le mod ?", "Voulez-vous installer le mod " + package["name"] + " ?"):
            self.appendConsole("Installation annulée")
            return False
        self.showButton.config(state=DISABLED)
        self.instButton.config(state=DISABLED)
        self.listButton.config(state=DISABLED)

        res = self.download(package)
        
        self.parent.refreshModContent()

        self.showButton.config(state=NORMAL)
        self.instButton.config(state=NORMAL)
        self.listButton.config(state=NORMAL)
        
