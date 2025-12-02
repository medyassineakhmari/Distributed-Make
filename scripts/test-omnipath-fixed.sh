#!/bin/bash

#############################################
# test-omnipath-fixed.sh
# Test Omni-Path avec la conversion IP corrigée
#############################################

echo "========================================="
echo "  Testing FIXED Omni-Path Resolution"
echo "========================================="
echo ""

cd ~/pingpong

# Compiler avec la nouvelle version
echo "[1/3] Compiling fixed MasterOPA..."
bash compile.sh
echo ""

# Déployer workers
echo "[2/3] Deploying workers..."
bash scripts/deploy.sh
echo ""

# Test Omni-Path avec la nouvelle résolution IP
echo "[3/3] Testing Omni-Path (with IP conversion)..."
echo ""
echo "Looking at worker IPs..."
if [ -f "$OAR_NODE_FILE" ]; then
    echo "Workers in OAR_NODE_FILE:"
    cat "$OAR_NODE_FILE" | sort -u | head -5
    echo ""
    echo "Running MasterOPA with DEBUG info..."
    java MasterOPA | tee test-opa-fixed.log
else
    echo "Error: OAR_NODE_FILE not set"
fi

echo ""
echo "Done ! Check if OPA IPs (172.18.x.x) are used now."
