def players_speak(self):
    # Todo: implémenter le tour depuis le raiser
    while True:
        speaker = self.id_speaker
        previous_speaker = self.next_player_id(speaker, -1)
        next_speaker = self.next_player_id(speaker)
        if sum(self.active_players) == 1:
            # cas où il ne reste plus qu'un joueur
            winner_id = next_speaker  # on trouve le dernier joueur restant (qui est aussi le suivant)
            return winner_id
        if not self.active_players[speaker] or self.players[speaker].is_all_in:
            # si le joueur est fold on le dégage
            continue
        amount_to_call = self.players[previous_speaker].on_going_bet

        if speaker == self.last_raiser and \
                self.players[speaker].on_going_bet == amount_to_call:
            # si personne n'a relancé dans le tour, on passe à l'étape suivante.
            return

        action, amount = self.players[speaker].speaks(amount_to_call)
        if self.players[speaker].is_all_in:
            self.new_pot(amount)
        if action == "f":
            self.active_players[speaker] = False
        elif action == "r":
            self.last_raiser = speaker
        self.id_speaker = self.next_player_id(self.id_speaker)