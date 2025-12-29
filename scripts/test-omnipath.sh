#!/bin/bash

#############################################
# test-omnipath.sh
# Test Omni-Path (100G) vs Ethernet (10G)
# Compare performance between two networks
#
# Usage: bash scripts/test-omnipath.sh
# Requirements: Must be run inside an OAR job with 2+ nodes
#############################################

set -e

echo "========================================="
echo "  Omni-Path vs Ethernet Network Test"
echo "========================================="
echo ""

cd ~/pingpong

# ===== 1. COMPILER =====
echo "[1/6] Compiling Java code..."
bash compile.sh
echo ""

# ===== 2. NETWORK DIAGNOSTIC =====
echo "[2/6] Running network diagnostic..."
bash scripts/network-diagnostic.sh > network-diagnostic-omnipath-test.txt 2>&1
echo "[OK] Diagnostic saved to: network-diagnostic-omnipath-test.txt"
echo ""

# ===== 3. DÉPLOYER WORKERS =====
echo "[3/6] Deploying workers on all nodes..."
bash scripts/deploy.sh
echo ""

# ===== 4. TEST ETHERNET =====
echo "========================================="
echo "  Test 1: ETHERNET (172.16.x.x)"
echo "========================================="
echo ""

echo "Running PingPong on Ethernet network..."
if java Master > test-ethernet.log 2>&1; then
    echo "[OK] Ethernet test completed"
    if [ -f "pingpong-normal.csv" ]; then
        mv pingpong-normal.csv pingpong-ethernet.csv
        echo "  Results: pingpong-ethernet.csv"
    fi
else
    echo "✗ Ethernet test failed"
    cat test-ethernet.log
fi
echo ""

# ===== 5. TEST OMNI-PATH =====
echo "========================================="
echo "  Test 2: OMNI-PATH (172.18.x.x - 100G)"
echo "========================================="
echo ""

echo "Running PingPong on Omni-Path network..."
if java MasterOPA > test-opa.log 2>&1; then
    echo "[OK] Omni-Path test completed"
    if [ -f "pingpong-opa.csv" ]; then
        echo "  Results: pingpong-opa.csv"
    fi
else
    echo "✗ Omni-Path test failed or not available"
    echo "  This is normal if no Omni-Path network is configured"
    cat test-opa.log
fi
echo ""

# ===== 6. GÉNÉRER LES GRAPHIQUES =====
echo "[6/6] Generating comparison graphs..."
if [ -f "pingpong-ethernet.csv" ] && [ -f "pingpong-opa.csv" ]; then
    if python3 scripts/plot-ethernet-vs-opa.py; then
        echo "[OK] Comparison plots generated"
    else
        echo "⚠ Failed to generate plots (matplotlib/pandas may not be available)"
    fi
elif [ -f "pingpong-ethernet.csv" ]; then
    echo "⚠ Only Ethernet results available (no Omni-Path)"
fi
echo ""

# ===== 7. ARRÊTER LES WORKERS =====
echo "Stopping workers..."
for node in $(cat $OAR_NODE_FILE 2>/dev/null | sort -u); do
    if [ "$node" != "$(hostname)" ]; then
        ssh "$node" "pkill -9 -f Worker" 2>/dev/null || true
    fi
done
echo ""

# ===== 8. RÉSUMÉ =====
echo "========================================="
echo "  Test Summary"
echo "========================================="
echo ""
echo "Test logs:"
echo "  - test-ethernet.log"
echo "  - test-opa.log"
echo ""

if [ -f "pingpong-ethernet.csv" ]; then
    ETH_MAX=$(tail -n +2 pingpong-ethernet.csv 2>/dev/null | awk -F',' '{print $4}' | sort -n | tail -1 || echo "?")
    echo "Ethernet (10G):"
    echo "  CSV: pingpong-ethernet.csv"
    echo "  Max throughput: $ETH_MAX MB/s"
fi

if [ -f "pingpong-opa.csv" ]; then
    OPA_MAX=$(tail -n +2 pingpong-opa.csv 2>/dev/null | awk -F',' '{print $4}' | sort -n | tail -1 || echo "?")
    echo ""
    echo "Omni-Path (100G):"
    echo "  CSV: pingpong-opa.csv"
    echo "  Max throughput: $OPA_MAX MB/s"
fi

if [ -f "pingpong-ethernet.csv" ] && [ -f "pingpong-opa.csv" ]; then
    echo ""
    echo "Comparison plots:"
    ls -1 comparison-ethernet-vs-opa-*.png 2>/dev/null | sed 's/^/  - /' || echo "  (not generated)"
fi

echo ""
echo "Network diagnostic:"
echo "  - network-diagnostic-omnipath-test.txt"
echo ""
echo "========================================="
