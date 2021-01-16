# server.Table

## Attributs:

- `speaker (Player)` joueur qui a la parole.
- `sb, bb (float)` small blind, big blind (normalement bb = 2*sb)
- `final_hand (bool)` flag qui indique si on montre les cartes
-  `in_change, in_game, end, redistributions (bool)` flags pour l’interface
- `history (List)` historique des événements depuis la création de la table
- `bot_training (bool)` change le comportement (notamment désactive les logs) lorsqu’il est activé
- `verbose (bool)` logs activés si vrais
- `salon (Salon)` salon dont dépend la table

## Méthodes

- `next_player(p: Player) -> Player` joueur qui suit p dans la table
- `sleep(ms: float) -> None` met le serveur en pause pendant ms milisecondes, désactivée si on est en bot_training
- `print` version custom de print, désactivée si on n’est pas en verbose
- `set_up_game() -> None` met tout en place avant de lancer une partie
- `game() -> None` méthode principale qui lance une partie
- `players_speak(mise: float, raiser: Player) -> None` (re)lance un tour de mise avec une mise de départ de `mise`, misée par le joueur `raiser`
- `distance_to_dealer(player: Player) -> int` utile pour l’historique de jeu, c’est une donnée importante pour l’entraînement de bots.
- `active_players() -> int` nombre de joueurs qui peuvent toujours au moins suivre partiellement (i.e. ne sont pas all_in ou couchés)
- `folded_players() -> int` nombres de joueurs couchés
- `manage_pots() -> None` remet les différents pots aux gagnants qui les ont suivis