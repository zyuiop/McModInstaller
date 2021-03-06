import os
import shutil
import Remote
from tkinter import *
from distutils.dir_util import *
import json
# C'est une classe abstraite, tu l'utilises directement et tu vas voir à la sortie.
class DownloadManager:
    def __init__(self, parent=None, cli=False):
        self.parent = parent
        self.dependencies = []
        self.cli = cli
    
    def appendConsole(self, text, delete=False):
        if not self.cli:
            self.parent.logs.config(state=NORMAL)
            # À utiliser avec modération
            if delete:
                self.parent.logs.delete("1.0",END)
            self.parent.logs.insert(END, text + "\n")
            self.parent.logs.config(state=DISABLED)
            self.parent.logs.yview(END)
        else:
            print(text)
    
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
                        self.appendConsole("[1/3] Téléchargement du minecraft.jar")
                        if not self.parent.remote.downloadFile('http://' + self.parent.remote.repo + self.parent.remote.directory + pkg['jarfile'], profilepath + "/" + pkg['profilename'] + '.jar', "Téléchargé : {} / {}", "Téléchargement du minecraft.jar"):
                            self.appendConsole("--> Échec lors du téléchargement")
                    else:
                        self.appendConsole("[1/3] Copie du minecraft.jar")
                        shutil.copy(vanilladir + "/" + pkg['version'] + ".jar", profilepath + "/" + pkg['profilename'] + ".jar")
                        self.appendConsole("--> Copie terminée") # Comme notre relation, salaud !
                        self.appendConsole("[2/3] Téléchargement du profil")
                        if not self.parent.remote.downloadFile('http://' + self.parent.remote.repo + self.parent.remote.directory + pkg['json'], profilepath + "/" + pkg['profilename'] + ".json", "Téléchargé : {} / {}", "Récupération du profil"):                        
                            self.appendConsole("--> Échec lors du téléchargement du profil")
                        else:
                            self.appendConsole("[3/3] Ajout au fichier de profils")
                            try:
                                with open(self.parent.remote.mcpath+"/launcher_profiles.json", "r") as fichier:
                                    try:
                                        jsonfile = fichier.read()
                                    except:
                                        self.appendConsole("--> Une erreur s'est produite.")
                                        return False
                            except FileNotFoundError:
                                self.appendConsole("--> Erreur : Lecture du fichier de profils impossibles. Minecraft est il correctement installé ?")
                                return False

                            tab = json.loads(jsonfile)
                            new_profile = {"name":pkg["name"],"lastVersionId":pkg["profilename"]}
                            tab["profiles"][pkg["name"]] = new_profile

                            with open(self.parent.remote.mcpath+"/launcher_profiles.json", "w") as fichier:
                                try:
                                    fichier.write(json.dumps(tab))
                                    self.appendConsole("[3/3] Terminé !")
                                    self.appendConsole("Le profil a bien été installé ! ")
                                    return True
                                except:
                                    self.appendConsole("Erreur lors de l'écriture du fichier de profils")
                                    return False
            else:
                self.appendConsole("La version " + pkg['version'] + " de Minecraft n'est pas installée.")        
        else:
            self.appendConsole("\nInstallation de "+pkg["name"])
            path = self.parent.remote.mcpath + "/"
            if pkg['modtype'] == 'coremod':
                path += "coremods"
            else:
                path += "mods"
            path += "/" + pkg['mc_version']
            if not os.path.isdir(path):
                mkpath(path)
            path += '/' + pkg['package_name'] + ".jar"
            i = 0
            worked = False
            while not worked and i < len(pkg['mirrors']):
                url = 'http://' + pkg['mirrors'][i]['server'] + pkg['mirrors'][i]['path']
                self.appendConsole("--> Tentative de téléchargement de "+url+"...")
                worked, err = self.parent.remote.downloadFile(url, path, "Téléchargé : {} / {}", "Téléchargement de " + pkg['name'])
                if not worked:
                    self.appendConsole("--> Erreur de téléchargement : "+err)
                i += 1
            self.dependencies.append(pkg['name'])

            for d in pkg['dependencies']:
                if not d['name'] in self.dependencies:
                    self.dependencies.append(d['name'])
                    rep, dpkg = self.parent.remote.downloadPkgInfo(d['pkgurl'])
                    dpkg["pkgurl"] = d["pkgurl"]
                    if rep:
                        self.download(dpkg, False)
                    else:
                        self.appendConsole("--> Erreur de lecture de la dépendance : "+dpkg)
            if is_first == True:
                self.dependencies = []

            self.parent.localDB.updatePackage(self.parent.localDB.packageName(pkg["package_name"], pkg["mc_version"]), pkg)

            if is_first:
                self.appendConsole("--> Téléchargement terminé. Le mod a été installé.")     
            else:
                self.appendConsole("--> Dépendance installée.")
            
