import os
import shutil
import Remote
from tkinter import *

# C'est une classe abstraite, tu l'utilises directement et tu vas voir à la sortie.
class DownloadManager:
    def __init__(self, parent):
        self.parent = parent
        self.dependencies = []
    
    def appendConsole(self, text, delete=False):
        self.parent.logs.config(state=NORMAL)
        # À utiliser avec modération
        if delete:
            self.parent.logs.delete("1.0",END)
        self.parent.logs.insert(END, text + "\n")
        self.parent.logs.config(state=DISABLED)
        self.parent.logs.yview(END)
    
    def download(self, pkg, is_first=True):
        # !!! LOCAL DB NON SUPPORTEE !!!
        worked = False
        i = 0
        if pkg.get("modtype") == None: # C'est un client
            vanilladir = self.parent.remote.mcpath + "/versions/" + pkg['version']
            if os.path.isdir(vanilladir):
                if os.path.exists(vanilladir + "/" + pkg['version'] + ".jar"):
                    profilepath = self.parent.remote.mcpath + "/versions/" + pkg['profilename']
                    if not os.path.isdir(profilepath):
                        mkpath(profilepath)
                    else:
                        self.appendConsole("/!\\ Le dossier " + profilepath + " existe.")
                    if "jarfile" in pkg.keys():
                        self.appendConsole("[1/2] Téléchargement du minecraft.jar")
                        if not self.parent.remote.downloadFile('http://' + self.parent.remote.repo + self.parent.remote.directory + pkg['jarfile'], profilepath + "/" + pkg['profilename'] + '.jar', "Téléchargé : {} / {}", "Téléchargement du minecraft.jar"):
                            self.appendConsole("--> Échec lors du téléchargement")
                    else:
                        self.appendConsole("[1/2] Copie du minecraft.jar")
                        shutil.copy(vanilladir + "/" + pkg['version'] + ".jar", profilepath + "/" + pkg['profilename'] + ".jar")
                        self.appendConsole("--> Copie terminée") # Comme notre relation, salaud !
                    self.appendConsole("[2/2] Téléchargement du profil")
                    if not self.parent.remote.downloadFile('http://' + self.parent.remote.repo + self.parent.remote.directory + pkg['json'], profilepath + "/" + pkg['profilename'] + ".json", "Téléchargé : {} / {}", "Récupération du profil"):                        
                        self.appendConsole("--> Échec lors du téléchargement du profil")
                    else:
                        self.appendConsole("--> Terminé. Le client a été installé.")
            else:
                self.appendConsole("La version " + pkg['version'] + " de Minecraft n'est pas installée.")        
        else:
            path = self.parent.remote.mcpath + "/"
            if pkg['modtype'] == 'coremod':
                path += "coremods"
            else:
                path += "mods"
            if not os.path.isdir(path):
                mkpath(path)
            path += "/" + pkg['package_name'] + ".jar"
            i = 0
            worked = False
            while not worked and i < len(pkg['mirrors']):
                worked = self.parent.remote.downloadFile('http://' + pkg['mirrors'][i]['server'] + pkg['mirrors'][i]['path'], path, "Téléchargé : {} / {}", "Téléchargement de " + pkg['name'])
                i += 1
            self.dependencies.append(pkg['name'])
            for d in pkg['dependencies']:
                if not d['name'] in self.dependencies:
                    self.dependencies.append(d['name'])
                    dpkg = self.parent.remote.downloadPkgInfo(d['name'])
                    self.download(self, dpkg, False)
            if is_first == True:
                self.dependencies = []
