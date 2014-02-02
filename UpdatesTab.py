from DownloadManager import *
import tkinter
import tkinter.ttk

class UpdatesTab(DownloadManager):
    def initTab(self):
        Button(self.parent.tabs[3], text="Rechercher des mises à jours", command=self.showUpdates).grid(row=0,column=0)
        self.installUpdatesBtn = Button(self.parent.tabs[3], text="Installer les mises à jour",command=self.installUpdates,state=DISABLED)
        self.installUpdatesBtn.grid(row=0,column=1)
        self.appendConsole("Recherchez des mises à jour puis cliquez sur \"Installer les mises à jour\" pour lancer l'installation.")
    
    def showUpdates(self):
        self.appendConsole("Chargement de la liste de mods ...")
        self.installUpdatesBtn.config(state=NORMAL)
        liste = tkinter.ttk.Treeview(self.parent.tabs[3], selectmode="browse")
        liste['columns'] = ('mcversion', 'newversion')
        liste.heading('mcversion', text='Version Minecraft')
        liste.heading('newversion', text='Version Mod')
        liste.heading('#0', text='Nom')
        toupdate = self.ModsToUpdate()
        self.appendConsole(str(toupdate))
        for up in toupdate:
            liste.insert('', 'end', text=up["name"], values=up["mcver"] + " " + up["version"])
        liste.grid(row=1,column=0,columnspan=2)

        return toupdate
    
    def ModsToUpdate(self):
        self.appendConsole("Recherche des mises à jour ...")
        pkgs = self.parent.localDB.getAllPackages()
        toupdate = []

        for reponame, pkg in pkgs.items():
            ok, rep = self.parent.remote.getPackageUpdates(pkg)
            if not ok:
                self.appendConsole("Erreur lors de la vérification de " + pkg['name'] + ': ' + rep)
            elif rep != None:
                rep["pkgurl"] = pkg["pkgurl"]
                toupdate.append(rep)
        return toupdate

    def installUpdates(self):
        toupdate = self.showUpdates()
        self.appendConsole("Mise à jour ...")
        for pkg in toupdate:
            self.appendConsole("Mise à jour de " + pkg['name'] + "en version " + pkg['version'])
            self.download(pkg)
        
                

