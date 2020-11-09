"""On appelle cette méthode de la classe Table à chaque boucle de la méthode set(), juste après avoir appelé round_ob().
Donc de manière schématique, on appelle cette fonction à chaque fin de round_ob, et elle agit comme un état des lieux,
au lieu d'être appelée tout au long du jeu, dès que quelqu'un raise, ou fait all-in.

Au début de chaque set, on initialise: self.pots = [[0, self.players]]"""

def manage_pots(self):
    ogb_values = [0] + list(set([player.on_going_bet for player in self.players if not player.folded]))
    # on met le 0 pour la ligne 18, pour le ogb_values[i-1]
    for i in range(1, len(ogb_values)):
        pot_value = 0
        pot_players = []
        for p_id in range(self.nb_players):
            player_ogb = self.players[p_id].on_going_bet
            if player_ogb >= ogb_values[i-1]: #
                pot_value += min(player_ogb - ogb_values[i-1], ogb_values[i] - ogb_values[i-1])
                # importance du min : si l'ogb du joueur se situe entre deux ogb_values => le joueur s'est couché
            if player_ogb >= ogb_values[i]:
                pot_players.append(p_id)
        self.pots.append((pot_value, pot_players))