# server.Player

Classe de base pour tout type de joueur. Un joueur s’interface avec une table à travers
Player.speaks. Un Player est par défaut considéré comme contrôlé par un client du jeu,
et on attend de lui qu’il réponde aux requêtes du serveur.
Cependant, des classes de bots peuvent override l’interface table/joueur, ce qui permet de laisser
la décision d’une action au serveur lui-même plutôt qu’à un client. Cela évite de devoir saturer
les communications par les bots, notamment lorsqu’il y en a beaucoup qui jouent

## attributs

- `table (Table)` référence à la table sur laquelle se situe le joueur
- `salon (Salon)` référence au salon dans lequel se situe le joueur

## méthodes

- `speaks(amount_to_call: float, blind: bool) -> Tuple[str, float, int]` demande l’action que choisit de faire un joueur, étant donné une mise `amount_to_call` à suivre. Renvoyé sous la forme "f"|"c"|"r", amount, decision_time; ou amount est la quantité misée et decision_time la durée de décision