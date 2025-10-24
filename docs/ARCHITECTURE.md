# Architecture Détaillée

## Modules

### 1. Parser (`src/parser/`)
- **MakefileParser.java** : Analyse le Makefile
- **Task.java** : Représente une tâche
- **TaskStatus.java** : États (NOT_STARTED, IN_PROGRESS, FINISHED, FAILED)

### 2. Scheduler (`src/scheduler/`)
- **TaskScheduler.java** : Ordonnance selon dépendances
- **Main.java** : Point d'entrée

### 3. Network (`src/network/`)
- **Worker** : Exécute les commandes via RMI
- **Master** : Coordonne les workers

### 4. Cluster (`src/cluster/`)
- **ClusterManager.java** : Gère les nœuds disponibles
- **ComputeNode.java** : Représente un worker

## Flux d'exécution

1. Main initialise le cluster
2. Parser crée le graphe de dépendances
3. Scheduler identifie les tâches prêtes
4. Master distribue sur workers via RMI
5. Workers exécutent et retournent résultats
