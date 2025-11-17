#!/bin/bash
set -e

cd $HOME/pingpong

# Compile Java sources
echo "Compiling Java sources..."
javac -d . src/*.java

# Deploy workers on all nodes
echo "Deploying workers..."
bash scripts/deploy.sh

# Wait for workers to start
sleep 2

# Run sites comparison test
echo "Running sites comparison..."
java -cp . SitesComparaison

# Stop workers on remote nodes
echo "Stopping workers..."
for node in $(cat $OAR_NODE_FILE | uniq); do
    if [ "$node" != "$(hostname)" ]; then
        ssh $node "pkill -9 -f Worker" 2>/dev/null || true
    fi
done
echo "✓ Workers stopped"