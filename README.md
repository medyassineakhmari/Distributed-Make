# PingPong - Déploiement sur Grid5000

Ce projet permet de déployer et exécuter l’application **PingPong** sur la plateforme **Grid5000**, en utilisant plusieurs nœuds pour mesurer les performances réseau.

---

## Table des matières
- [Pré-requis](#pré-requis)  
- [Déploiement sur Grid5000](#déploiement-sur-grid5000)  
- [Compilation et exécution](#compilation-et-exécution)  
- [Téléchargement des résultats](#téléchargement-des-résultats)  

---

## Pré-requis

- Accès à Grid5000 avec un compte utilisateur.  
- Clé SSH (`~/.ssh/id_rsa`) configurée pour l’accès au site.  
- Permissions nécessaires pour exécuter des scripts (`chmod +x`).  
- `tar`, `scp`, `ssh` installés sur la machine locale.  

---

## Déploiement sur Grid5000

1. **Créer une archive de l’application :**
```bash
tar czf pingpong.tar.gz .
```

2. **Transférer l’archive vers Grid5000 :**
```bash
scp -i ~/.ssh/id_rsa -o "ProxyJump=<your_username>@access.grid5000.fr" pingpong.tar.gz <your_username>@<site>:
```

3. **Se connecter à la machine Grid5000 :**
```bash
ssh -i ~/.ssh/id_rsa <your_username>@access.grid5000.fr
ssh <site>
```

4. **Décompresser l’archive :**
```bash
tar xzf pingpong.tar.gz
```

## Compilation et exécution

1. **Rendre les scripts exécutables :**
```bash
chmod +x compile.sh scripts/*
```

2. **Allouer les nœuds avec OAR (interactif) :**
```bash
oarsub -I -l nodes=2,walltime=0:30
```

3. **Lancer l’application :**
```bash
./start.sh
```

## Téléchargement des résultats
Pour récupérer les images générées (comparison_*.png) sur ta machine locale, utilise depuis un autre terminal :

```bash
scp -i ~/.ssh/id_rsa -o "ProxyJump=<your_username>@access.grid5000.fr" <your_username>@<site>.grid5000.fr:~/pingpong/comparison_*.png ./
```