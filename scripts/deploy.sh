#!/bin/bash
echo "Deploying workers..."

for node in $(cat $OAR_NODE_FILE | uniq); do
    if [ "$node" != "$(hostname)" ]; then
        echo "  → Deploying to $node"
        scp -q ~/pingpong/src/*.class $node:~/pingpong/
        ssh $node "cd ~/pingpong && java Worker > /tmp/worker.log 2>&1" &
    fi
done

echo "Waiting for workers to start..."
sleep 5
echo "✓ Workers ready"