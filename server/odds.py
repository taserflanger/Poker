import random
from hand_5 import Hand_5
from itertools import combinations
from deck import Deck

def get_final_hand(player_cards, board):
    """ Assigne à un joueur sa meilleure combinaison de 5 cartes"""
    possible_hands = [Hand_5(i) for i in combinations(player_cards + board, 5)]
    return max(possible_hands)


def get_winner(opponents_cards, bot_cards, board):
    """Prend une liste de joueurs en entrée, renvoie les vainqueurs (meilleures mains finales)"""
    bot_hand=get_final_hand(bot_cards, board)
    opponents_hand=[]
    for card in opponents_cards:
        opponents_hand.append(get_final_hand(card, board))
    best_opponents_hand=max(opponents_hand)
    if bot_hand > best_opponents_hand:
        return "bot wins"
    elif bot_hand < best_opponents_hand:
        return "bot loses"
    else: 
        return "null"


# Determines the user's chance of winning given current hole cards and
# community cards, assuming that all unseen cards (undealt community cards
# and opponents' hole cards) are distributed randomly.
def give_odds(hand, board, num_opponents):
    cards_left=Deck()
    cards_left.remove(hand[0]), cards_left.remove(hand[1])
    for i in range(len(board)):
        cards_left.remove(board[i])

    monte_carlo_rounds=1000
    wins = 0
    ties = 0
    to_flop = 5 - len(board)
    to_draw = to_flop + 2 * num_opponents
    total_rounds = monte_carlo_rounds

    # Monte Carlo simulation
    for _ in range(monte_carlo_rounds):
        # Draw a random combination of unseen cards (remaining community
        # cards + 2 hole cards per opponent)
        drawn_cards = random.sample(cards_left.cards, to_draw)
        complete_board = board + drawn_cards[:to_flop]
        opponents_cards=[]
        for i in range(num_opponents):
            opponents_cards.append( drawn_cards[to_flop+2*i:to_flop+2*i+2] )
        result=get_winner(opponents_cards, hand, complete_board)
        if result=="bot wins":
            wins+=1
        elif result=="null":
            ties+=1

    win_ratio = wins/total_rounds
    exp_winnings = win_ratio * (num_opponents+1) - 1
    ties_ratio=ties/total_rounds

    return win_ratio, exp_winnings, ties_ratio


""" test
from card import Card
hand=[Card(12, 3), Card(9, 2)]
board=[Card(11, 3), Card(7, 2), Card(2, 1), Card(13, 3)]
print(give_odds(hand, board, 2))
"""
