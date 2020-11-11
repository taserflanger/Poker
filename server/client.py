import socket
import json
adresseIP = "127.0.0.1"	# Ici, le poste local
port = 12800	# Se connecter sur le port 50000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((adresseIP, port))
print("Connecté au serveur")
print("Tapez FIN pour terminer la conversation. ")
message = ""

def donner_action(balise):
    repons = client.recv(1024).decode()
    print(repons)
    while repons!= balise:
        message = input("> ")
        client.send(message.encode())
        repons = client.recv(1024).decode()
        print(repons)
        if repons=="raise":
            #print("Raise? (current stack: {self.stack})  "))
            print("how much?")
            donner_action("fin raise")
            repons=balise



donner_action("fin preparation")
print("La partie va commencer! (attendez qq instants que les autres joueurs soient prêts) ")
reponse=""
while reponse!= b"etape fin":
    reponse = client.recv(1024).decode()
    if reponse== "jouer":
        donner_action("fin action")
    else:
        print("actualisation:")
        print(reponse)
print("Connexion fermée")
client.close()