from rodrigue.deck import Deck

"""
L'itérateur de la classe table permet de parcourir les joueurs restant dans la main, à partir de celui qui doit parler
en premier.
Pour jouer une main:

TODO:   - s'occuper de la fonctionnalité fold, et de l'attribut ind_speaker
        - s'occuper du cas de figure ou tout le monde sauf 1 s'est couché
        - retranscrire dans un modèle client/serveur, où le client n'a accès qu'aux informations qui le concernent
        - (détail: Si un joueur n'a pas assez d'argent pour faire sa blinde, il doit être exclu au début)

"""
import random


class Table:

    def __init__(self, table_players, small_blind, big_blind, dealer="random"):
        self.nb_players = len(table_players)
        self.players = table_players
        self.nb_players = len(self.players)
        if dealer == "random":
            self.id_dealer = random.randint(0, self.nb_players - 1)
        else:
            self.id_dealer = dealer
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.active_players = [True for _ in range(self.nb_players)]
        self.sb = small_blind
        self.bb = big_blind
        self.deck = Deck()
        self.cards = []
        self.pot = 0
        self.id_dealer = 0  # l'indice du dealer

    def __iter__(self):
        i = (self.id_dealer + 1) % self.nb_players
        for k in range(self.nb_players):
            yield (i + k) % self.nb_players

    def new_hand(self):
        for player in self.players:
            player.set = []
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pot = 0
        self.cards = []
        self.deck = Deck()

    def next_player_id(self, player_id):
        next_id = (player_id + 1) % self.nb_players
        while not self.active_players[next_id]:
            next_id = (next_id + 1) % self.nb_players
        return next_id

    def initialise_round(self):
        for player in self.players:
            self.pot += player.on_going_bet
            player.on_going_bet = 0
        self.id_speaker = self.next_player_id(self.id_dealer)

    def set(self):
        self.new_hand()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            winner_id = round_ob()
            if winner_id:
                break
        print(f"{self.players[winner_id].name} wins")

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.set.append(self.deck.deal())
        for i in range(2):
            print(f"{self.players[self.id_speaker].name} bets {[self.sb, self.bb][i]}")
            self.players[self.id_speaker].on_going_bet += [self.sb, self.bb][i]
            self.id_speaker = self.next_player_id(self.id_speaker)

    def pre_flop(self):
        print(f'Dealer : {self.id_dealer}', f"Speaker : {self.id_speaker}", sep='\n')
        self.deal_and_blinds()
        return self.players_speak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        print([str(card) for card in self.cards])
        return self.players_speak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        return self.players_speak()

    def players_speak(self, mise=0):
        # Todo: implémenter le tour depuis le raiser
        for _ in range(self.nb_players):
            speaker = self.id_speaker
            if sum(self.active_players) == 1:
                winner_id = self.next_player_id(
                    speaker)  # on trouve le dernier joueur restant (qui est aussi le suivant)
                return winner_id
            if not self.active_players[speaker]:
                continue
            dealer = self.id_dealer

            action, amount = self.players[self.id_speaker].speaks(mise)
            if speaker == dealer and self.players[self.next_player_id(dealer)].on_going_bet == mise:
                # si personne n'a relancé dans le tour, on passe à l'étape suivante.
                return
            if action == "f":
                self.active_players[speaker] = False
            self.id_speaker = self.next_player_id(self.id_speaker)
            mise += amount


    def determiner_gagnants(self): #renvoie les gagnants sous forme de liste
        table=self.cards[:]
        joueurs=self.active_players[:]
        n=len(joueurs)
        gagnants=[]
        liste_des_scores=[]*n

        for i in range(n):
            joueurs[i].score= self.score(joueurs[i].carte)
            liste_des_scores[i]=joueurs[i].score 

        #trier liste des scores selon les points d'abord et selon les complémentaires ensuite       
        liste_des_scores.sort(key=lambda x:x[1], reverse=True)   #trie selon les complémentaires de façon décroissante
        liste_des_scores.sort(key=lambda) x:x[0], reverse=True) #trie selon les points de facçon décroissante
        
        score_reference=liste_des_scores[0]  #score du gagnant
        for player in joueurs:               #si un jouer a le meme score que le gagnant alors il est gagnant 
            if player.score == score_reference:
                gagnants.append(player)
    
        return gagnants


#le programme suivant donne la meilleure combinaison de 5 cartes parmi 7, les 7 cartes
# correspodant à la main du joueur + les cartes sur la table
# il renvoie les cartes formant la meilleure combinaison, c-a-d toujours 5 cartes car même s'il
# n'y a qu'une paire de 3 par exemple, ceux sont les 2 plus hautes cartes parmi les 5 restantes 
# qui forment la combinaison de 5 cartes. On appelle ces 3 cartes, les cartes complémentaires
# La fonction carte_haute donne ces cartes complémentaires.


#renvoie les cartes complémentaires
    def carte_hautes(self, main): 
        table=self.cards[:]         
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
    def calculer_point(self, carte):
        table=self.cards[:]
        max_points=0
        jeu=carte+table
        resultat={i:False for i in reversed(["carte haute", "paire", "double paire", "brelan", "quinte", "couleur", "full", "carré", "quinte flush"]) }
    
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
                ch=self.carte_hautes( cards )
                resultat["carré"]=(cards, ch)    

            #brelan
            elif occurence==3 and not resultat["brelan"]:
                max_points=max(max_points, 330 + cards[0][0])
                ch=self.carte_hautes( cards )
                resultat["brelan"]=(cards, ch) 

            #double paire
            elif occurence==2 and resultat["paire"] and not resultat["double paire"]:
                paire1=resultat["paire"][0]
                max_points=max(max_points, 40 + paire1[0][0]*20 + cards[0][0])     
                ch=self.carte_hautes( paire1 + cards )  
                resultat["double paire"]= ([paire1, cards], ch)  

            #paire
            elif occurence>=2 and not resultat["paire"]:
                if occurence==3:
                    cards.pop(-1)
                max_points=max(max_points, 20 + cards[0][0])
                ch=self.carte_hautes( cards )         
                resultat["paire"]=(cards, ch)
     
            # carte haute
            elif cards and not resultat["carte haute"]:
                max_points=max(max_points, cards[0][0])           
                ch=self.carte_hautes( cards )
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

        score=(max_points)
        for i in resultat:
            if resultat[i]:
                meilleure_combi=(i, resultat[i])
                break
        score=(max_points, meilleure_combi[1][1][1])
        return score, meilleure_combi

    def score(self, table):
        points, meilleure_combi=self.calculer_point(carte)
        return points