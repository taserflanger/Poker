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
    key_of_max_l = key(max(l, key))
    return [value for value in l if key(value) == key_of_max_l]

def rank_dict(l):
    """Prend une liste en entrée et renvoie un dictionnaire avec pour chaque indice le rang de sa valeur parmi toutes
    les valeurs (0 correspond au max) : correspond à une liste ordonnée mais prend en compte les égalités"""
    sorted_ids = sort_ids(l)[::-1]
    rk_dict = {}
    rk = -1
    prev = None
    for ind in sorted_ids:
        if prev is None or l[ind] != prev:
            rk += 1
            prev = l[ind]
        rk_dict[ind] = rk
    return rk_dict

