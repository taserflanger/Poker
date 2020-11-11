import socket
import json
adresseIP_server_andres = "176.160.246.2"	# Ici, le poste local
#adresseIP_local="127.00.01"
port = 12800	# Se connecter sur le port 50000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((adresseIP_server_andres, port))
print("Connecté au serveur")
print("Tapez FIN pour terminer la conversation. ")
message = ""
nom_fichier=input("nom fichier\n >" )

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


while reponse!= b"etape fin":
    reponse = client.recv(1024).decode("utf-8")
    if reponse== "actualisation debut" or reponse== "actualisation tour" or reponse== "actualisation fin": 
        actualisation(fichier)
        fichier=open(nom_fichier, "r")
    elif reponse=="preparation":
        give_name_and_ready() 
    elif reponse=="action":
        action()
print("Connexion fermée")
client.close()