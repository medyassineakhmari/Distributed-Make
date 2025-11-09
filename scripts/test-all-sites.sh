#!/bin/bash
# Test sur PLUSIEURS sites

SITES=("grenoble" "lyon" "nancy" "lille" "nantes" "rennes")
NUM_NODES=2
WALLTIME="0:15"

echo "========================================="
echo "  Multi-Sites Comparison"
echo "========================================="
echo ""

# Nettoyer fichiers précédents
rm -f sites-comparison.csv

for SITE in "${SITES[@]}"; do
    echo "-----------------------------------"
    echo "Testing site: $SITE"
    echo "-----------------------------------"
    
    SITE_FULL="$SITE.grid5000.fr"
    
    # Copier projet
    echo "Copying files to $SITE..."
    scp -r ~/pingpong $SITE_FULL:~/
    
    # Soumettre job
    echo "Submitting job..."
    JOB_ID=$(ssh $SITE_FULL "cd ~/pingpong && oarsub -l nodes=$NUM_NODES,walltime=$WALLTIME 'bash scripts/run-sites-test.sh'" | grep "OAR_JOB_ID" | cut -d= -f2)
    
    if [ -z "$JOB_ID" ]; then
        echo "Failed to submit job on $SITE"
        continue
    fi
    
    echo "Job ID: $JOB_ID"
    
    # Attendre fin
    while true; do
        STATUS=$(ssh $SITE_FULL "oarstat -s -j $JOB_ID")
        if [[ "$STATUS" =~ ": Terminated" ]]; then
            break
        fi
        sleep 10
    done
    
    # Récupérer résultats
    echo "Retrieving results..."
    scp $SITE_FULL:~/pingpong/sites-comparison.csv /tmp/site-$SITE.csv
    
    # Ajouter au fichier global
    if [ -f "/tmp/site-$SITE.csv" ]; then
        tail -n +2 /tmp/site-$SITE.csv >> sites-comparison.csv
    fi
    
    echo "✓ Site $SITE completed"
    echo ""
done

# Ajouter header
echo "site,latency_ms,throughput_mbps" | cat - sites-comparison.csv > temp && mv temp sites-comparison.csv

# Générer graphique
echo "Generating comparison plot..."
python3 scripts/plot_results.py sites

echo ""
echo "✓ Multi-sites test completed!"
echo "Results: sites-comparison.csv"
echo "Plot: sites_comparison.png"