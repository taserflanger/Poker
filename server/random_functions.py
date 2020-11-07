"""
Fonctions quelconques utilisées dans les autres fichiers du projet
"""

def sort_ids(l):
    """Retourne la liste des indices de l triés par ordre croissant"""
    m = [i for i in range(len(l))]
    m.sort(key=lambda i: l[i])
    return m

def maxes(l, key=lambda x: x):
    """Fonction max native, mais au lieu de renvoyer un élément max, renvoie tous les éléments max"""
    key_of_max_l = key(max(l, key=key))
    return [value for value in l if key(value) == key_of_max_l]

