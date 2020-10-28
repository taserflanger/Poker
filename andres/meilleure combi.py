#le programme suivant donne la meilleure combinaison de 5 cartes parmi 7, les 7 cartes
# correspodant à la main du joueur + les cartes sur la table
# il renvoie les cartes formant la meilleure combinaison, c-a-d toujours 5 cartes car même s'il
# n'y a qu'une paire de 3 par exemple, ceux sont les 2 plus hautes cartes parmi les 5 restantes 
# qui forment la combinaison de 5 cartes. On appelle ces 3 cartes, les cartes complémentaires
# La fonction carte_haute donne ces cartes complémentaires.


#renvoie les cartes complémentaires
def carte_hautes(main, table):          
    k=len(main)
    complémentaires=[]
    for carte in table:
        if carte not in main:
            complémentaires.append(carte)
    complémentaires.sort(key= lambda x:x[0], reverse=True)
    chiffre_complémentaire=""
    for i in complémentaires[:(5-k)]:
        chiffre_complémentaire+= str(i[0])
    return complémentaires[:(5-k)], int(chiffre_complémentaire)

#convention AS correspond au 14.
#amélioration: dire le nom de la paire/full/brelan etc : paire d'as par exemple 
#cette fonction renvoie la meilleure combinaison de 5 cartes parmi 7 et un score associé
# La table des scores est faite de telle sorte que:  pour tout C1 et C2 des combinaisons
# si C1 est meilleur combi que C2 alors score(C1)>score(C2) 
# Le score se compose des points des cartes gagnantes (par exemple les points d'une paire d'AS cf table des points)
#  et d'un numero des cartes complémentaires (qui correspond à la concatenation des numeros de chacune 
# des cartes complémentaires: par exemple si les cartes complémentaires à paire d'AS sont 12, 11 et 10 alors 
# le numero complémentaire est 121110. Cela permet de départager les combinaisons qui ont les
# mêmes points 
# Si 2 scores sont égaux il y a ex aequo
def calculer_point(carte, table):
    max_points=0
    jeu=carte+table
    resultat={i:False for i in reversed(["carte haute", "paire", "double paire", "brelan", "quinte", "couleur", "full", "carré", "quinte flush"]) }
    print("jeu: ", jeu, "\n")
    
    #création d'un dictionnaire qui compte les occurences des cartes
    c_suite={str(i): [] for i in range(1, 15)}
    for carte in jeu:
        c_suite[str(carte[0])].append(carte)
        if carte[0]==14:
            c_suite[str("1")].append(carte)

    for hauteur in range(14, 1, -1):
        cards=c_suite[str(hauteur)]
        occurence=len(cards)
        
        #carré
        if occurence==4 and not resultat["carré"]:
            max_points=max(max_points, 650 + cards[0][0])
            ch=carte_hautes( cards , jeu )
            resultat["carré"]=(cards, ch)    

        #brelan
        elif occurence==3 and not resultat["brelan"]:
            max_points=max(max_points, 330 + cards[0][0])
            ch=carte_hautes( cards , jeu )
            resultat["brelan"]=(cards, ch) 

        #double paire
        elif occurence==2 and resultat["paire"] and not resultat["double paire"]:
            paire1=resultat["paire"][0]
            max_points=max(max_points, 40 + paire1[0][0]*20 + cards[0][0])     
            ch=carte_hautes( paire1 + cards, jeu )  
            resultat["double paire"]= ([paire1, cards], ch)  

        #paire
        elif occurence>=2 and not resultat["paire"]:
            if occurence==3:
                cards.pop(-1)
            max_points=max(max_points, 20 + cards[0][0])
            ch=carte_hautes( cards , jeu )         
            resultat["paire"]=(cards, ch)
     
        # carte haute
        elif cards and not resultat["carte haute"]:
            max_points=max(max_points, cards[0][0])           
            ch=carte_hautes( cards , jeu )
            resultat["carte haute"]=(cards, ch)
        
    #full 
    if resultat["paire"] and resultat["brelan"]:
        max_points=max(max_points, 390 + resultat["brelan"][0][0][0]*20 + resultat["paire"][0][0][0])
        resultat["full"]= ( resultat["brelan"][0] + resultat["paire"][0] , ([], 0))


    #permet de verifier la couleur d'un paquet pour la couleur et pour la quinte flush
    def verifier_couleur(paquet):
        for couleur in ['pique', 'trefle', 'coeur', 'carreau']: #pour tester la quinte flush
            compteur=0  
            qf=[]
            for cartes in paquet:
                for carte in cartes:
                    if carte[1]==couleur:
                        compteur+=1
                        qf.append(carte)
            if compteur>=5:
                qf.sort(key=lambda x:x[0], reverse=True)
                return qf[:5]  
        return False

    #quinte
    compteur=0
    for j, card in enumerate(c_suite.items()):
        card=card[1]
        if card:
            compteur+=1
            if compteur==5:
                max_points=max(max_points, 350 + j+1 )
                resultat["quinte"]= [c_suite[str(c)] for c in range(j-3, j+2)]
                qf=verifier_couleur(resultat["quinte"])
                if qf:
                    resultat["quinte flush"]=(qf, ([], 0))     
                    max_points=max(max_points, 700 + qf[0][0])
                else:
                    resultat["quinte"]= ([c_suite[str(c)][0] for c in range(j-3, j+2)], ([], 0))
                compteur-=1
        else:
            compteur=0
    
    #couleur
    for i in range(7):
        jeu[i]=[jeu[i]]
    couleur=verifier_couleur(jeu)
    resultat["couleur"]=(couleur, ([], 0)) if couleur else False 
    if couleur:
        max_points=max(max_points, 370 + couleur[0][0] )
    return resultat, max_points


#extraction des données
#ont pourra extraire les données différemment en fonction de comment on code le reste
res, ptn=calculer_point([(14, "pique"), (14, "carreau")], [(7, "pique"), (5, "pique"), (3, "pique"), (12, "pique"), (10, "carreau")] )
for i in res.items():
    print(i)
for i in res:
    if res[i]:
        meilleure_combi=(i, res[i])
        break
points=(ptn, meilleure_combi[1][1][1])
combi=(meilleure_combi[0], meilleure_combi[1][0]+ meilleure_combi[1][1][0])
print("\n La meilleure combinaison est:\n ", combi, "\n", points)