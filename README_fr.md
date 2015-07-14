# TS2 - Train Signalling Simulation
version 0.5

## Présentation
"Train Signalling Simulation" (TS2) est un jeu de simulation ferroviaire où vous
devez aiguiller les trains sur une zone et les garder à l'heure.
Voir le site pour plus de détails.

## Liens
* [Site de TS2](http://ts2.sf.net/fr/)
* [Site du projet TS2 sur SourceForge.net](http://sourceforge.net/projects/ts2/)
* [Site de développement sur GitHub](https://gihub.com/npiganeau/ts2)

## Statut
TS2 est un logiciel beta ce qui signifie qu'il est jouable, mais qu'il lui manque
encore de nombreuses fonctionnalités que l'on peut attendre d'une simulation.
TS2 est livré avec deux simulations:
* Une simulation de démonstration appelée "drain"
* Une simulation complète appelée "liverpool-st"

De nouvelles simulations peuvent être créées grâce à l'éditeur incorporé dans
le logiciel.

## Installation
* Versions officielles:
    - Windows 64 bits: installer à partir de l'installateur et lancer ts2.exe.
    - Autres plateformes: voir installation depuis les sources.
* Installation à partir des sources:
    - Télécharger et installer Python v3 ou supérieur depuis [www.python.org](http://www.python.org).
    - Télécharger et installer PyQt v4.8 ou supérieur depuis [http://www.riverbankcomputing.co.uk](http://www.riverbankcomputing.co.uk).
    - Récuperer les sources depuis le site de développement sur GitHub.
    - Lancer ts2.py.

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

## Créer de nouvelles simulations

Les simulations peuvent être créées/modifiées à l'aide de l'éditeur incorporé dans TS2.

## Historique des versions
###Version 0.5:
- Editeur amélioré incluant les caractéristiques suivantes: 
    - Sélections multiples
    - Copier/Coller
    - Edition de propriétés en masse
    - Redimensionnement des quais avec la souris
- Nouveaux signaux avec :
    - Longueur réduite
    - Code train positionable 
    - Nouveaux types de signaux (UK 4 aspects notamment)

###Version 0.4.1:
- Correction d'un bug dans l'éditeur: les nouvelles "Places" sont maintenant prises en compte immédiatement
    après leur création.

###Version 0.4:
- Ajout du système de comptage du score
- Ajout de retards statistiques sur les trains
- Ajout de la possibilité de sauvegarder les jeux en cours
- Ajout d'une option pour jouer avec les circuits de voie

###Version 0.3.3:
- Ajout de la traduction française de TS2
