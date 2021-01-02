# -*- coding: utf-8 -*-
import socket
import json
adresseIP_server_andres = "192.168.1.11"	# Ici, le poste local
adresseIP_server_local="127.0.0.1"
adresseIP_server_linode="178.79.165.80"
port = 12800	# Se connecter sur le port 50000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((adresseIP_server_local, port))
print("Connecté au serveur")
print("Tapez FIN pour terminer la conversation. ")
message = ""
nom_fichier=input("nom fichier\n >" )
nom_fichier_cartes=nom_fichier+"_cartes"

def action():
    print("(f), (c), or raise: enter how much if you raise")
    reponse=input("> ")
    msg={"flag":"action", "action":str(reponse)}
    data=json.dumps(msg).encode("utf-8")
    client.send(data)

def give_name_and_ready():
    msg="error name"
    while msg == "error name":
        print("Quel est ton nom?")
        reponse=input("> ")
        envoie={"flag":"name", "name":reponse}
        data=json.dumps(envoie).encode("utf-8")
        client.send(data)
        msg=client.recv(1024).decode("utf-8")
        infos=json.loads(msg)
        msg=infos["flag"]
    reponse=input("pret?\n >  ")
    message={"flag":"ready"}
    data=json.dumps(message).encode("utf-8")
    client.send(data)

reponse=""
fichier=open(nom_fichier, "w")
fichier.close()
fichier=open(nom_fichier, "r")

def actualisation(fichi, infos_act):
    fichi.close()
    with open(nom_fichier, "w") as dossier:
        dossier.write(str(infos_act))

fichier_cartes=open(nom_fichier_cartes, "w")
fichier_cartes.close()
fichier_cartes=open(nom_fichier_cartes, "r")

def actualisation_debut(cartes, infos_act):
    cartes.close()
    with open(nom_fichier_cartes, "w") as dossier:
        dossier.write(str(infos_act))

give_name_and_ready()
while reponse!= b"etape fin":
    reponse = client.recv(1024).decode("utf-8")
    infos=json.loads(reponse)
    if infos["flag"]== "update table" or infos["flag"]=="init_game": 
        actualisation(fichier, infos)
        fichier=open(nom_fichier, "r")
    elif  infos["flag"]== "end_game":
        print(infos)
    elif infos["flag"]== "new_game":
        actualisation_debut(fichier_cartes, infos)
        fichier_cartes=open(nom_fichier_cartes, "r")
    elif infos["flag"]=="action":
        action()
print("Connexion fermée")
client.close()

