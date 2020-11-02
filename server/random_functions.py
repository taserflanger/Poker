"""
Fonctions quelconques utilisées dans les autres fichiers du projet
"""

def ids_of_value(l, value):
    """Prend une liste et une valeur en entrée, et renvoit les indices tels que """
    return [i for i in range(len(l)) if l[i] == value]

def sort_ids(l):
    m = [i for i in range(len(l))]
    m.sort(key=lambda i: l[i])
    return m

def maxes(l, key=lambda x: x):
    """Fonction max native, mais au lieu de renvoyer un élément max, renvoie tous les éléments max"""
    key_of_max_l = key(max(l, key))
    return [value for value in l if key(value) == key_of_max_l]


def rank_dict(l):
    """Prend une liste en entrée, et renvoie un dictionnaire avec chaque indice de la liste en clé, et le rang
    de cet indice dans la liste en valeur"""
    ids_of_equal_value = [ids_of_value(l, value) for value in ]
