"""
Fonctions quelconques utilisées dans les autres fichiers du projet
"""

def max_with_ids(l):
    max_ids = []
    max_l = max(l)
    for i in l:
        if l[i] == max:
            max_ids.append(i)
    return max_l, max_ids