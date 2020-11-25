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
    msg_reçu="erreur nom"
    while msg_reçu == "erreur nom":
        print("Quel est ton nom?")
        reponse=input("> ")
        client.send(reponse.encode("utf-8"))
        msg_reçu=client.recv(1024).decode("utf-8")
    reponse=input("pret?\n >  ")
    client.send(reponse.encode("utf-8"))

reponse=""
fichier=open(nom_fichier, "w")
fichier.close()
fichier=open(nom_fichier, "r")

def actualisation(fichi):
    msg_reçu=client.recv(1024).decode("utf-8")
    msg_reçu=json.loads(msg_reçu)
    fichi.close()
    with open(nom_fichier, "w") as dossier:
        dossier.write(str(msg_reçu))

fichier_cartes=open(nom_fichier_cartes, "w")
fichier_cartes.close()
fichier_cartes=open(nom_fichier_cartes, "r")
def actualisation_debut(cartes):
    msg_reçu=client.recv(1024).decode("utf-8")
    msg_reçu=json.loads(msg_reçu)
    cartes.close()
    with open(nom_fichier_cartes, "w") as dossier:
        dossier.write(str(msg_reçu))

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

