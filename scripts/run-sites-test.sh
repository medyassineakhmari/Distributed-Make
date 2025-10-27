#!/bin/bash
cd ~/pingpong

# Compiler
javac *.java

# Déployer workers
bash scripts/deploy.sh

# Lancer test de comparaison
java SitesComparison

# Arrêter workers
for node in $(cat $OAR_NODE_FILE | uniq); do
    if [ "$node" != "$(hostname)" ]; then
        ssh $node "pkill -9 -f Worker" 2>/dev/null
    fi
done