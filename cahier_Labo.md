# Cahier de Laboratoire

## Informations Générales

Ce document recense l’ensemble des informations pertinentes de notre projet, mettant en relief nos essais, nos erreurs et nos tâtonnements, sur toute la durée de la mise en œuvre du projet.
 
**Plateforme** : Grid5000  
**Aperçu** : Mesurer et comparer les performances réseau (latence et débit) entre différents nœuds et sites de Grid5000 en utilisant une architecture Master-Worker avec Java RMI.

## Architecture du Système

Le système utilise une architecture distribuée Master-Worker où :
- Un nœud Master coordonne les tests et collecte les résultats
- Des nœuds Workers exécutent les opérations de ping/pong via RMI
- Les tests mesurent la latence (RTT) et le débit pour différentes tailles de payload (1KB à 10MB)

## Prérequis Techniques

### Accès et Configuration
- Compte utilisateur Grid5000 actif
- Clé SSH configurée (`~/.ssh/id_rsa`)
- Outils installés : `tar`, `scp`, `ssh`
- Permissions d'exécution pour les scripts

### Configuration SSH Recommandée
Le fichier `config_ssh` fournit une configuration optimisée avec multiplexage de connexions pour accélérer les opérations SSH répétées.

## Protocole Expérimental

### Phase 1 : Déploiement Initial

**1. Création de l'archive**
```bash
tar czf pingpong.tar.gz .
```

**2. Transfert vers Grid5000**
```bash
scp -i ~/.ssh/id_rsa -o "ProxyJump=<username>@access.grid5000.fr" pingpong.tar.gz <username>@<site>:
```

**3. Connexion et extraction**
```bash
ssh -i ~/.ssh/id_rsa <username>@access.grid5000.fr  
ssh <site>  
mkdir pingpong  
tar xzf pingpong.tar.gz -C pingpong  
cd pingpong
```

### Phase 2 : Exécution des Tests

**1. Préparation des scripts**
```bash
chmod +x compile.sh scripts/*
```

**2. Allocation des ressources OAR**
```bash
oarsub -I -l nodes=2,walltime=0:30
```

**3. Lancement de l'application**
```bash
./start.sh
```

### Phase 3 : Tests Multi-Sites

Le script `test-all-sites.sh` automatise les tests sur plusieurs sites Grid5000.

**Sites testés** : grenoble, lyon, nancy, lille, nantes, rennes

**Configuration** :
- Nombre de nœuds : 2
- Durée maximale (walltime) : 15 minutes

**Processus automatisé** :
1. Copie des fichiers vers chaque site
2. Soumission du job OAR
3. Surveillance de l'état du job
4. Récupération des résultats CSV
5. Agrégation dans un fichier global

### Phase 4 : Collecte des Résultats

**Récupération locale des graphiques**
```bash
scp -i ~/.ssh/id_rsa -o "ProxyJump=<username>@access.grid5000.fr" <username>@<site>.grid5000.fr:~/pingpong/comparison_*.png ./
```

## Métriques Collectées

Les tests génèrent les métriques suivantes :
- **Latence (RTT)** : Temps d'aller-retour en millisecondes
- **Débit** : Throughput en Mbps
- **Tailles de payload** : 13 tailles de 1KB à 10MB

Les résultats sont agrégés dans `sites-comparison.csv` avec l'en-tête : `site,latency_ms,throughput_mbps`

## Visualisation des Résultats

Le script Python `plot_results.py` génère des graphiques de comparaison. Les fichiers de sortie incluent :
- `comparison_rtt.png` : Comparaison RTT Normal vs I/O
- `comparison_throughput.png` : Comparaison débit Normal vs I/O
- `sites_comparison.png` : Analyse visuelle des performances inter-sites

### Partie Makefile :
(à compléter)

## Notes Importantes

- **Méthodologie de mesure** : Chaque taille de payload est testée 9 fois, la médiane est sélectionnée pour minimiser l'impact des valeurs aberrantes
- **..** :
