# TS2 - Train Signalling Simulation
version 0.7

## Présentation
**Train Signalling Simulation (TS2)** est un jeu de simulation ferroviaire où vous
devez aiguiller les trains sur une zone et les garder à l'heure.

## Liens
* Site de TS2 - [ts2.github.io](http://ts2.github.io/)
* Chat TS2 (en anglais) - [irc.freenode.net#trainsigsim](irc://irc.freenode.net#trainsigsim)
* Page du projet TS2 sur Github - [github.com/ts2](http://github.com/ts2/)

## Statut
TS2 est un logiciel beta ce qui signifie qu'il est jouable, mais qu'il lui manque
encore de nombreuses fonctionnalités que l'on peut attendre d'une simulation.
Au démarrage de TS2, vous pourrez télécharger des simulations depuis notre serveur [ts2-data](https://github.com/ts2/ts2-data)

De nouvelles simulations peuvent être créées grâce à l'éditeur incorporé dans
le logiciel.

## Installation
* Versions officielles:
    - Windows 64 bits: installer à partir de l'installateur et lancer ts2.exe.
    - Autres plateformes: voir installation depuis les sources.
* Installation à partir des sources:
    - Télécharger et installer Python v3 ou supérieur depuis [www.python.org](http://www.python.org).
    - Télécharger et installer PyQt v5 ou supérieur depuis [http://www.riverbankcomputing.co.uk](http://www.riverbankcomputing.co.uk).
    - Récuperer les sources depuis [GitHub](https://github.com/ts2/ts2/releases/tag/v0.7.0).
    - Lancer start-ts2.py.
* Post installation:
    - Télécharger le serveur de simulation en ouvrant le menu "Fichier->Options" et cliquer sur "Télécharger le serveur".

## Jeu (Guide rapide)
* Charger une simulation depuis le dossier _simulation_ (ou le dossier _data_ si vous avez installé depuis les sources).
    Si vous voulez charger une simulation d'une version précédente de TS2, vous devez d'abord l'ouvrir avec l'éditeur
    puis la sauvegarder avant de la charger à nouveau dans la fenêtre principale.
* Activation des routes:
    - Pour faire passer un signal du rouge au vert, vous devez activer une route de ce signal vers le suivant.
    - Pour activer une route, cliquer sur un signal puis sur le suivant. S'il est possible d'activer une route
        entre ces deux signaux, la voie entre les deux signaux s'affiche en blanc, les aiguilles sont orientées
        automatiquement selon cette route et le signal d'entrée passe au jaune (ou au vert si le second signal
        est déjà jaune ou vert).
    - Pour annuler une route, cliquer avec le bouton droit sur le premier signal.
    - Les routes sont détruites automatiquement au passage du premier train. Cependant, vous pouvez activer une
        route de façon persistente en maintenant la touche MAJ enfoncée lorsque vous cliquez sur le deuxième
        signal. Les routes persistentes sont repérées par un petit carré blanc à côté de leur signal d'entrée.
    - Activation forcée: Il est possible de forcer l'activation d'une route en appuyant simultanément sur _ctrl_
        et _alt_ lorsque vous cliquez sur le second signal. Attention, cela va activer la route sans vérifier
        qu'il n'y a pas d'autres routes en conflit et peut engendrer des accidents de train ou d'autres effets
        non désirés.
* Données des trains:
    - Cliquer sur le code d'un train sur la carte ou dans la liste des trains pour voir ses données dans la
        fenêtre "Détails du train". La fenêtre "Détails de la mission" se mettra à jour également.
* Données des gares:
    - Cliquer sur un quai sur la carte pour afficher les horaires de la gare dans la fenêtre "Gare".
* Interagir avec les trains:
    - Cliquer avec le bouton droit sur le code d'un train sur la carte ou dans la liste des trains ou dans la
        fenêtre "Détails du train" pour afficher le menu relatif au train. Ce menu permet de:
        + Assigner une nouvelle mission au train. Sélectionner la mission dans la fenêtre qui apparait et cliquer
        sur "Ok".
        + Recommencer la mission, c'est-à-dire de signifier au machiniste de s'arrêter à nouveau à la première
        gare.
        + Inverser le sens de marche du train.
    - Les trains changent automatiquement de mission lorsque la mission actuelle est terminée.
* Vous devriez voir les trains rouler, s'arrêter aux signaux fermés et aux gares prévues dans leur mission. Ils
    doivent quitter les gares à l'horaire prévu ou passé un temps donné après leur arrivée si l'horaire de départ
    prévu est déjà passé.
* Score:
    A chaque fois qu'un train arrive en retard à une gare, s'arrête sur le mauvais quai ou est aiguillé dans une
    mauvaise direction, des points de pénalité sont ajoutés au score.

## Développement

Que vous souhaitiez écrire votre propre simulation avec l'éditeur ou développer un nouveau client pour interagir avec TS2,
allez voir notre 
[Manuel technique](https://github.com/ts2/ts2-sim-server/blob/master/docs/ts2-technical-manual.pdf)
(en anglais)

## Historique des versions

### Version 0.7:
- Nouvelle architecture client-serveur:
    - Mode multijoueur en connectant plusieurs joueurs sur la même simulation
    - API Websocket pour interagir avec la simulation

### Version 0.6:
- Nouvelle version Python3 / PyQt5
- Déplacement du projet sur GitHub
- Nouveau site
- Les simulations sont maintenant au format JSON 
- Possibilité de télécharger des simulations / signaux depuis ts2-data
- Marches à vue
- Division de train
- Nouveaux signaux paramétriques
- Signaux BAL français
- Signaux de manoeuvre UK
- Amélioration de l'interface
- Meilleure gestion des erreurs

### Version 0.5:
- Dernière version PyQt4
- Editeur amélioré incluant les caractéristiques suivantes: 
    - Sélections multiples
    - Copier/Coller
    - Edition de propriétés en masse
    - Redimensionnement des quais avec la souris
- Nouveaux signaux avec :
    - Longueur réduite
    - Code train positionable 
    - Nouveaux types de signaux (UK 4 aspects notamment)
