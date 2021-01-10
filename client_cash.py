
import socket
import json
import pandas as pd
adresseIP_server_andres = "192.168.1.11"	# Ici, le poste local
adresseIP_local="127.0.0.1"
adresseIP_server_linode="178.79.165.80"
port = 12800	# Se connecter sur le port 50000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((adresseIP_local, port))
print("Connecté au serveur")
print("Tapez FIN pour terminer la conversation. ")
message = ""
nom_fichier=input("nom fichier\n >" )
nom_fichier_cartes=nom_fichier+"_cartes"

def action():
    print("(f), (c), or raise: enter how much if you raise")
    reponse=input("> ")
    client.send(reponse.encode("utf-8"))

data=pd.read_csv("server/tmp_data/data.csv")
  
def ask_password(name):
    actual_password_idx=data[data["name"]==name].index.values
    actual_password=data["password"][actual_password_idx].values
    print(actual_password)
    for i in range(3):
        print("give password, try number", i, "\n", 3-i, "tries left")
        password=input(">")
        if password == actual_password:
            print("correct paswword")
            return True
    return False
   
def ask_pseudo():
    for i in range(3):
        print("what is your pseudo account?")
        name=input("> ")
        if name in data["name"].values:
            print("correct pseudo!")
            return True, name
        else:
            print("error name")
    return False, ""

def give_name_and_ready():
    print("sign_in? (y) yes or (n) no")
    sign_in=input("> ")
    sign_in=True if sign_in=="y" else False

    if sign_in:
        name_correct=False
        password_correct=False
        name_correct, name= ask_pseudo() 
        if name_correct:
            password_correct=ask_password(name)
        if not password_correct or not name_correct:
            sign_in=False
            print("la connexion a ton compte n'a pas fonctionnée, créé un nouveau compte!")
        else:
            client.send(name.encode("utf-8"))

    if sign_in==False: 
        rep="''"
        client.send(rep.encode("utf-8"))
        msg="erreur nom"
        while msg == "erreur nom":
            print("Quel est ton nom?")
            reponse=input("> ")
            client.send(reponse.encode("utf-8"))
            infos=client.recv(1024).decode("utf-8")
            msg=json.loads(infos)["flag"]

        print("Quel est ton mot de passe?")
        reponse=input("> ")
        while len(reponse)<3:
            print("mot de passe trop cour, saisi un nouveau mdp:")
            reponse=input("> ")
        client.send(reponse.encode("utf-8"))
    
    reponse=input("pret?\n >  ")
    client.send(reponse.encode("utf-8"))

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

while reponse!= b"etape fin":
    reponse = client.recv(1024).decode("utf-8")
    infos=json.loads(reponse)
    if infos["flag"]== "actualisation tour" or reponse== "actualisation fin": 
        actualisation(fichier, infos)
        fichier=open(nom_fichier, "r")
    elif infos["flag"]== "actualisation debut":
        actualisation_debut(fichier_cartes, infos)
        fichier_cartes=open(nom_fichier_cartes, "r")
    elif infos["flag"]=="preparation":
        give_name_and_ready() 
    elif infos["flag"]=="action":
        action()
print("Connexion fermée")
client.close()

