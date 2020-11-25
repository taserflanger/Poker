# -*- coding: utf-8 -*-
import socket
import json
#adresseIP_server_andres = "192.168.1.11"	# Ici, le poste local
#adresseIP_local="127.0.0.1"
adresseIP_server_linode="178.79.165.80"
port = 12800	# Se connecter sur le port 50000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((adresseIP_server_linode, port))
print("Connecté au serveur")
print("Tapez FIN pour terminer la conversation. ")
message = ""
nom_fichier=input("nom fichier\n >" )
nom_fichier_cartes=nom_fichier+"_cartes"
def action():
    print("(f), (c), or raise: enter how much if you raise")
    reponse=input("> ")
    client.send(reponse.encode("utf-8"))

def give_name_and_ready():
    msg="erreur nom"
    while msg == "erreur nom":
        print("Quel est ton nom?")
        reponse=input("> ")
        client.send(reponse.encode("utf-8"))
        msg=client.recv(1024).decode("utf-8")
    reponse=input("pret?\n >  ")
    client.send(reponse.encode("utf-8"))

reponse=""
fichier=open(nom_fichier, "w")
fichier.close()
fichier=open(nom_fichier, "r")

def actualisation(fichi):
    msg=client.recv(1024).decode("utf-8")
    msg=json.loads(msg)
    fichi.close()
    with open(nom_fichier, "w") as dossier:
        dossier.write(str(msg))

fichier_cartes=open(nom_fichier_cartes, "w")
fichier_cartes.close()
fichier_cartes=open(nom_fichier_cartes, "r")
def actualisation_debut(cartes):
    msg=client.recv(1024).decode("utf-8")
    msg=json.loads(msg)
    cartes.close()
    with open(nom_fichier_cartes, "w") as dossier:
        dossier.write(str(msg))

while reponse!= b"etape fin":
    reponse = client.recv(1024).decode("utf-8")
    if reponse== "actualisation tour" or reponse== "actualisation fin": 
        actualisation(fichier)
        fichier=open(nom_fichier, "r")
    elif  reponse== "actualisation debut":
        actualisation_debut(fichier_cartes)
        fichier_cartes=open(nom_fichier_cartes, "r")
    elif reponse=="preparation":
        give_name_and_ready() 
    elif reponse=="action":
        action()
print("Connexion fermée")
client.close()

