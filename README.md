# Poker

---

Mini jeu de poker en ligne.  


---

## Installation

```
pip install nptyping
pip install PyQt5
```

## Utilisation

### Partie Rapide

Pour lancer en local une partie à 2 joueurs (+1 bot), lancer la commande depuis la racine:

**Windows**
```shell
scripts/launchgame.bat
```
**Linux**
```shell
scripts/launchgame.sh
```

### Customisation du serveur

Pour lancer le serveur:

```shell
python -m scripts.main_server <local|distant> <PORT> <Nb BotProba> <Nb BotGenetic>
```


### Client

Pour lancer le programme client et sa GUI, exécuter sur votre machine:
```shell
python -m scripts.main_client <local|distant> <PORT>
```
