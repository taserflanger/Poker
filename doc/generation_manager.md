#bots.genetic.Generation_Manager

Classe destinée à gérer la transition entre générations. Dans le futur, cette classe pourra être indépendante du génome du bot (idée: créer une classe génome du bot).

Pour l’instant, elle prend comme paramètres W, b, f (qui sont respectivement les poids, les biais et une fonction qui permet de modifier les poids de la première couche de neurones selon leur distance dans l’historique).

## méthodes

`train(N: int, m: int, nb_players, small_blind, max_round: int) -> W, b, f` entraîne `N` générations, chacune sur `m` parties, avec `nb_players` joueurs par tables avec au maximum `max_round` tours de mises par partie.