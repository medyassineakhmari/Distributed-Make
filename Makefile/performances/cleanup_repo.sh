#!/bin/bash

echo "=== NETTOYAGE DU REPO ==="

# 1. Garder seulement les résultats finaux
echo "1. Archivage des anciens résultats..."
mkdir -p archived_campaigns/campaign_10iter_$(date +%Y%m%d_%H%M%S)
cp -r results/ archived_campaigns/campaign_10iter_$(date +%Y%m%d_%H%M%S)/
cp data/raw_measurements_clean_10iter.csv archived_campaigns/campaign_10iter_$(date +%Y%m%d_%H%M%S)/

# 2. Supprimer les fichiers temporaires
echo "2. Suppression des fichiers temporaires..."
cd data
rm -f raw_measurements.csv
rm -f save_run1.csv
rm -f raw_measurements_backup_*.csv
rm -f raw_measurements_partial*.csv
rm -f campaign_*.txt
rm -f *.pyc
rm -f create_save_run1.py
rm -f clean_10iter.py
rm -f extract_*.sh
rm -f clean_*.py
rm -f process_*.py

# 3. Supprimer les logs OAR
echo "3. Suppression des logs OAR..."
cd ../scripts
rm -f OAR.bench*.stdout
rm -f OAR.bench*.stderr

# 4. Garder seulement les scripts essentiels
echo "4. Nettoyage des scripts temporaires..."
rm -f benchmark_model_clean.sh
rm -f benchmark_model_simple.sh
rm -f test_*.sh

echo ""
echo "=== STRUCTURE FINALE ==="
cd ~/Distributed-Make/Makefile/performances
tree -L 2 -h

echo ""
echo "✓ Nettoyage terminé !"
