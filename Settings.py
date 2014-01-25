import http.client
import os
import shutil
import json

class Settings:

	def __init__(self, mcpath):
		self.settingsFile = mcpath+"/mcmodsinstaller.config"
		if not os.path.exists(mcpath):
			mkpath(mcpath)
		
	def read(self):
		if not os.path.exists(self.settingsFile):
			print("Création de la configuration...")
			tab = {}
			self.updateConfig(tab)

		with open(self.settingsFile, "r") as fichier:
			try:
				return json.load(fichier)
			except:
				print("[FATAL] Erreur de lecture de la configuration")
				exit()

	def getNode(self, nodename):
		config = self.read()
		ret = config.get(nodename)
		if ret == None:
			return False
		else:
			return ret

	def updateNode(self, nodename, node):
		if self.deleteNode(nodename):
			if self.addNode(nodename, node):
				return True
		return False

	def deleteNode(self, nodename):
		config = self.read()
		try:
			config.pop(nodename)
		except:
			pass
		if self.updateConfig(config):
			return True
		else:
			return False

	def addNode(self, nodename, node):
		conf = self.read()
		conf[nodename] = node
		if self.updateConfig(conf):
			return True
		else:
			return False

	def updateConfig(self, conf):
		with open(self.settingsFile, "w") as fichier:
			try:
				fichier.write(json.dumps(conf))
				return True
			except:
				return False