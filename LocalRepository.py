import http.client
import os
import shutil
import json

class LocalRepository:

	def __init__(self, appdata):
		self.mcModsDirectory = appdata+"/.minecraft/mods/"
		self.localRepoFileName = appdata+"/.minecraft/mcmodsinstaller.local.db"
		
	def read(self):
		if not os.path.exists(self.localRepoFileName):
			print("Création de la base de données locale...")
			tab = {"mods":{}}
			self.updateDB(tab)

		with open(self.localRepoFileName, "r") as fichier:
			try:
				return json.load(fichier)
			except:
				print("[FATAL] Impossible de charger la base de données locale")
				exit()
				
	def getAllPackages(self):
		db = self.read().get("mods")
		if db == None:
			db = {}
		return db

	def getPackage(self, packageName):
		db = self.read().get("mods")
		if db == None:
			db = {}

		ret = db.get(packageName)
		if ret == None:
			return False
		else:
			return ret
		return db[packageName]

	def updatePackage(self, packageName, package):
		if self.deletePackage(packageName):
			if self.addPackage(packageName, package):
				return True
		return False
		

	def deletePackage(self, packageName):
		db = self.read().get("mods")
		if db == None:
			db = {}
		
		try:
			db.pop(packageName)
		except:
			pass
		
		if self.updateDB(db):
			return True
		else:
			return False

	def addPackage(self, packageName, package):
		db = self.read().get("mods")
		if db == None:
			db = {}
		db[packageName] = package
		if self.updateDB(db):
			return True
		else:
			return False

	def updateDB(self, db):
		with open(self.localRepoFileName, "w") as fichier:
			try:
				db = {"mods":db}
				fichier.write(json.dumps(db))
				return True
			except:
				return False
