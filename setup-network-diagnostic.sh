#!/bin/bash

# ============================================
# Quick Setup Script for Network Diagnostic
# À exécuter après décompression sur Grid5000
# ============================================

echo "📋 Setting up Network Diagnostic Integration..."
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "compile.sh" ]; then
    echo "[ERROR] Error: compile.sh not found. Are you in the pingpong directory?"
    exit 1
fi

echo "[OK] Found compile.sh - you're in the right place"
echo ""

# Rendre les scripts exécutables
echo "🔐 Making scripts executable..."
chmod +x compile.sh
chmod +x scripts/compile.sh 2>/dev/null || true
chmod +x scripts/start.sh
chmod +x scripts/deploy.sh
chmod +x scripts/test-single-site.sh
chmod +x scripts/test-all-sites.sh
chmod +x scripts/network-diagnostic.sh

echo "[OK] All scripts are now executable"
echo ""

# Vérifier la présence des fichiers
echo "📁 Checking files..."
FILES=(
    "scripts/network-diagnostic.sh"
    "scripts/start.sh"
    "scripts/test-single-site.sh"
    "NETWORK_DIAGNOSTIC_GUIDE.md"
    "INTEGRATION_SUMMARY.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  [OK] $file"
    else
        echo "  [ERROR] $file (MISSING)"
    fi
done

echo ""
echo "========================================="
echo "         Setup Complete! "
echo "========================================="
echo ""
echo "📖 Documentation:"
echo "  -> INTEGRATION_SUMMARY.md      (quick start)"
echo "  -> NETWORK_DIAGNOSTIC_GUIDE.md (detailed)"
echo ""
echo " Next steps:"
echo "  1. chmod +x compile.sh scripts/*"
echo "  2. oarsub -I -l nodes=2,walltime=0:30"
echo "  3. ./start.sh"
echo ""
echo "✨ The network diagnostic will run automatically!"
echo "========================================="
