#!/bin/bash
# Test sur UN SEUL site pour comparer Normal vs I/O

echo "========================================="
echo "  Single Site Test: Normal vs I/O"
echo "========================================="
echo ""

cd ~/pingpong

# Compiler
bash compile.sh
echo ""

# Déployer workers
bash scripts/deploy.sh
echo ""

# Test NORMAL
echo "Running Ping-Pong NORMAL..."
java Master
echo ""

# Test I/O
echo "Running Ping-Pong WITH I/O..."
java MasterIO
echo ""

# Générer les graphiques
echo "Generating plots..."
python3 scripts/plot_results.py single
echo ""

# Arrêter workers
echo "Stopping workers..."
for node in $(cat $OAR_NODE_FILE | uniq); do
    if [ "$node" != "$(hostname)" ]; then
        ssh $node "pkill -9 -f Worker" 2>/dev/null
    fi
done

echo "✓ Test completed!"
echo "Results:"
echo "  - pingpong-normal.csv"
echo "  - pingpong-io.csv"
echo "  - comparison_rtt.png"
echo "  - comparison_throughput.png"