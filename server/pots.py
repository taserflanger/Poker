class Pots:
    def __init__(self):
        self.amounts_to_call = [0, float("inf")]  # pour éviter les effets de bord
        self.players = [set(), set()]
        self.values = [0, 0]
        self.total = 0

    def __len__(self):
        return len(self.amounts_to_call)

    def __str__(self):
        return "\n".join(
            [f"{self.values[i]} can be won by {', '.join(map(str, self.players[i]))}"
             for i in range(1, len(self)-1)
             ]
        )

    def initialize(self):
        self.amounts_to_call = [0, float("inf")]  # pour éviter les effets de bord
        self.players = [set(), set()]
        self.values = [0, 0]

    def create_pot(self, player, amount):
        """
        Crée un pot parallèle associé au joueur player avec une valeur amount
        :param player: le joueur en question
        :param amount: la mise minimale pour suivre ce pot parallèle
        :return: void
        """
        index = sorted(self.amounts_to_call + [amount]).index(amount)
        # on détermine l'indice
        self.amounts_to_call.insert(index, amount)
        self.values.insert(index, 0)
        self.players.insert(index, self.players[index].copy())
        for i in range(1, index+1):
            self.players[i].add(player)

    def calculate(self):
        """
        A la fin d'un set, on calcule la valeur des pots, qu'on agrège dans le total
        :return:
        """
        self.initialize_pots_values()
        self.combine_pots()
        self.total += sum(self.values)

    def initialize_pots_values(self):
        """
        Met en place toutes les valeurs des pots parallèles provisoires
        :return:
        """
        for i in range(1, len(self) - 1):
            self.values[i] = (self.amounts_to_call[i] - self.amounts_to_call[i - 1]) * len(self.players[i])

    def combine_pots(self):
        """
        Combine les pots qu'exactement les mêmes joueurs suivent en prenant
        en compte s'ils ont fold (appeler après initialize_pots_values car sinon on perd
        l'information des bonnes valeurs des pots qui dépend du nombre de joueurs)
        :return:
        """
        i = 1
        while i < len(self) - 1:
            diff = self.players[i].difference(self.players[i + 1])
            # si tous les joueurs en plus dans le pot i sont couchés, on le combine avec
            # le pot i+1
            if sum([not p.folded for p in diff]) == 0:
                self.values[i + 1] += self.values[i]
                del self.values[i]
                del self.amounts_to_call[i]
                del self.players[i]
            else:
                i += 1

    def update_player(self, player, amount):
        if amount in self.amounts_to_call:
            # cas où l'on suit simplement un pot déjà existant
            index = self.amounts_to_call.index(amount) + 1
        else:
            # cas où l'on suit un autre pot
            index = sorted(self.amounts_to_call + [amount]).index(amount)
        for i in range(1, index):
            self.players[i].add(player)
