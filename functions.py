import http.client
import os
import shutil
import json

def inputDepot():
	srv = input("Entrez l'addresse du serveur (sans le http://)(d pour utiliser le serveur minecraft.zgalaxy.fr) : ")
	if srv == "d":
		return ("minecraft.zgalaxy.fr", "/")
	srv = srv.split("/")
	serveur = ""
	dossier = "/"
	if len(srv) == 1:
		serveur = srv[0]
	else:
		serveur = srv[0]
		for key,content in enumerate(srv):
			if key > 0:
				dossier = dossier+content+"/"

	return (serveur, dossier)
