#!/bin/bash
#OAR -l nodes=4,walltime=1:00:00
#OAR -n NFSvsSCPBenchmark
#OAR -O nfs_scp_%jobid%.out
#OAR -E nfs_scp_%jobid%.err

# Charger Java si nécessaire
module load java || true

# Afficher les informations du job
echo "Job ID: $OAR_JOB_ID"
echo "Nodes alloués:"
cat $OAR_NODE_FILE | sort | uniq
echo ""

# Configurer SSH sans mot de passe (déjà fait normalement sur Grid5000)
echo "Configuration SSH..."

# Compiler le code Java
echo "Compilation du code Java..."
javac Metric.java NFSvsSCPBenchmark.java

if [ $? -ne 0 ]; then
    echo "ERREUR: Échec de la compilation"
    exit 1
fi

echo "Compilation réussie!"
echo ""

# Exécuter le benchmark
echo "Lancement du benchmark..."
java NFSvsSCPBenchmark

# Générer les graphiques
if [ -f "results.csv" ]; then
    echo ""
    echo "Génération des graphiques..."
    python3 plot_results.py
fi

echo ""
echo "=== Job terminé ==="
echo "Résultats disponibles dans:"
echo "  - nfs-results.txt"
echo "  - scp-results.txt"
echo "  - nfs_vs_scp_comparison.png"