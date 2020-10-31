    
    def determiner_gagnants(self):  # renvoie les gagnants sous forme de liste
        joueurs=self.active_players[:]
        n=len(joueurs)
        gagnants=[]
        liste_des_scores=[]*n

        for i in range(n):
            joueurs[i].score, joueurs[i].combinaison= self.meilleure_combinaison(joueurs[i].hand)
            liste_des_scores[i]=joueurs[i].score 

        #trier liste des scores selon les points d'abord et selon les complémentaires ensuite       
        liste_des_scores.sort(key=lambda x:x[1], reverse=True) #trie selon les complémentaires de façon décroissante
        liste_des_scores.sort(key=lambda x:x[0], reverse=True) #trie selon les points de facçon décroissante
        
        score_reference=liste_des_scores[0]  #score du gagnant
        for player in joueurs:               #si un jouer a le meme score que le gagnant alors il est gagnant 
            if player.score == score_reference:
                gagnants.append(player)
    
        return gagnants


#le programme suivant donne la meilleure combinaison de 5 cartes parmi 7, les 7 cartes
# correspodant à la main du joueur + les cartes sur la table

#convention AS correspond au 14.
#cette fonction renvoie la meilleure combinaison de 5 cartes parmi 7 et un score associé
# Le score se compose des points de la combinaison gagnantes (paire d'AS) et d'un numero des cartes complémentaires 
# à la combinaison (qui correspond à la concatenation des numeros de chacune des cartes complémentaires:
#  par exemple si les cartes complémentaires à paire d'AS sont 12, 11 et 10 alors le numero complémentaire est 121110.

    def meilleure_combinaison(self, hand):  
        
        def carte_hautes(cartes_combinaison, jeu): #jeu = table + main = 7 cartes        
            k=len(cartes_combinaison)              #cartes_combinaison est par exemple une paire d'as [(AS, "pique"), (AS, "carreau")] 
            complémentaires=[]
            for carte in jeu:
                if carte not in cartes_combinaison:
                    complémentaires.append(carte)
            complémentaires.sort(key= lambda x:x[0], reverse=True)
            chiffre_complémentaire=""
            for i in complémentaires[:(5-k)]:           #cocatenation des complémentaires: par exemple si 13, 12 sont 
                chiffre_complémentaire+= str(i[0])      #des complémentaires, alors chiffre_complémentaire vaut 1312
            return complémentaires[:(5-k)], int(chiffre_complémentaire)
        
        #permet de verifier la couleur d'un paquet pour la couleur et pour la quinte flush
        def verifier_couleur(paquet):
            for couleur in ['clubs', 'diamonds', 'hearts', 'spades']: #pour tester la quinte flush
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


        table=self.cards[:]
        max_points=0
        jeu=hand+table
        resultat={i:False for i in reversed(["carte haute", "paire", "double paire", "brelan", "quinte", "couleur", "full", "carré", "quinte flush"]) }
    
        #création d'un dictionnaire qui compte les occurences des cartes
        c_suite={str(i): [] for i in range(1, 15)}
        for carte in jeu:
            c_suite[str(carte[0])].append(carte)
            if carte[0]==14:
                c_suite[str("1")].append(carte)

        for hauteur in range(14, 1, -1):     #hauteur d'un AS est 14 et 1 à la fois 
            cards=c_suite[str(hauteur)]      
            occurence=len(cards)
        
            #carré
            if occurence==4 and not resultat["carré"]:
                max_points=max(max_points, 650 + cards[0][0])
                ch=carte_hautes( cards, jeu )
                resultat["carré"]=(cards, ch)    

            #brelan
            elif occurence==3 and not resultat["brelan"]:
                max_points=max(max_points, 330 + cards[0][0])
                ch=carte_hautes( cards, jeu )
                resultat["brelan"]=(cards, ch) 

            #double paire
            elif occurence==2 and resultat["paire"] and not resultat["double paire"]:
                paire1=resultat["paire"][0]
                max_points=max(max_points, 40 + paire1[0][0]*20 + cards[0][0])     
                ch=carte_hautes( paire1 + cards, jeu )  
                resultat["double paire"]= ([paire1, cards], ch)  

            #paire
            elif occurence>=2 and not resultat["paire"]:
                if occurence==3:                            #corrige le cas ou il y a 2 brelans dans le jeu
                    cards.pop(-1)
                max_points=max(max_points, 20 + cards[0][0])
                ch=carte_hautes( cards, jeu )         
                resultat["paire"]=(cards, ch)
     
            # carte haute
            elif cards and not resultat["carte haute"]:
                max_points=max(max_points, cards[0][0])           
                ch=carte_hautes( cards, jeu )
                resultat["carte haute"]=(cards, ch)
        
        #full 
        if resultat["paire"] and resultat["brelan"]:
            max_points=max(max_points, 390 + resultat["brelan"][0][0][0]*20 + resultat["paire"][0][0][0])
            resultat["full"]= ( resultat["brelan"][0] + resultat["paire"][0] , ([], 0))


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

        #extraction des données (inutile de comprendre ce passage, c'est de la mise en forme)
        for i in resultat:
            if resultat[i]:
                meilleure_combi=(i, resultat[i])
                break
        score=(max_points, meilleure_combi[1][1][1])
        return score, meilleure_combi