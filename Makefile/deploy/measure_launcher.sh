#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   MESURE DU TEMPS DE LANCEUR                           ║"
echo "╚══════════════════════════════════════════════════════════╝"

PROJECT_DIR="$HOME/wordcount-distributed"
RESULTS_DIR="$PROJECT_DIR/launcher_results"
mkdir -p "$RESULTS_DIR"

CSV_FILE="$RESULTS_DIR/launcher_$(date +%Y%m%d_%H%M%S).csv"
echo "Test,Workers,StartTime,WorkersReady,MasterConnected,LauncherTime" > "$CSV_FILE"

WORKER_COUNTS=(2 3 4 5 6 7 8)

TOTAL_AVAILABLE=$(cat "$OAR_NODEFILE" | sort -u | wc -l)

MAX_WORKERS_REQUESTED=0
for n in "${WORKER_COUNTS[@]}"; do
    if (( n > MAX_WORKERS_REQUESTED )); then
        MAX_WORKERS_REQUESTED=$n
    fi
done

REQUIRED_NODES=$((MAX_WORKERS_REQUESTED + 1))

if [ "$TOTAL_AVAILABLE" -lt "$REQUIRED_NODES" ]; then
    echo ""
    echo "ERREUR CRITIQUE : Nombre de noeuds insuffisant !"
    echo "---------------------------------------------------"
    echo "   Noeuds reserves (OAR) : $TOTAL_AVAILABLE"
    echo "   Noeuds requis         : $REQUIRED_NODES (1 Master + $MAX_WORKERS_REQUESTED Workers)"
    echo "---------------------------------------------------"
    echo "Solution : Refaites votre reservation avec plus de noeuds."
    echo "   Commande : oarsub -I -l nodes=$REQUIRED_NODES,walltime=00:30"
    echo ""
    exit 1
fi

echo "Verification capacite : $TOTAL_AVAILABLE noeuds disponibles pour un besoin de $REQUIRED_NODES. OK."

for num_workers in "${WORKER_COUNTS[@]}"; do
    echo ""
    echo "Test avec $num_workers workers..."

    for run in {1..3}; do
        echo "  Execution $run/3"

        for hostname in $(cat $OAR_NODEFILE | head -n $((num_workers + 1)) | tail -n $num_workers); do
            ssh $hostname "pkill -f WorkerNode" 2>/dev/null || true
        done

        start_workers=$(date +%s.%N)

        worker_hosts=$(cat $OAR_NODEFILE | head -n $((num_workers + 1)) | tail -n $num_workers)
        for hostname in $worker_hosts; do
            ssh $hostname "nohup java -cp $PROJECT_DIR/bin network.worker.WorkerNode $hostname 3000 > launcher_worker.log 2>&1 &" &
        done

        workers_ready=$(date +%s.%N)

        all_ready=false
        timeout_counter=0
        while [ "$all_ready" = false ] && [ $timeout_counter -lt 60 ]; do
            ready_count=0
            for hostname in $worker_hosts; do
                if ssh $hostname "netstat -ln | grep :3000" >/dev/null 2>&1; then
                    ready_count=$((ready_count + 1))
                fi
            done

            if [ $ready_count -eq $num_workers ]; then
                all_ready=true
            else
                sleep 1
                timeout_counter=$((timeout_counter + 1))
            fi
        done

        if [ "$all_ready" = false ]; then
            echo "Timeout: workers non prets"
            continue
        fi

        master_connected=$(date +%s.%N)

        master_host=$(cat $OAR_NODEFILE | head -n 1)
        worker_list=$(echo $worker_hosts | awk '{printf "\"%s:3000\",", $0}' | sed 's/,$//')

        cd $PROJECT_DIR
        timeout 10 java -cp bin scheduler.Main "[$worker_list]" >/dev/null 2>&1 || true

        end_time=$(date +%s.%N)

        launcher_time=$(awk "BEGIN {printf \"%.3f\", $end_time - $start_workers}")

        echo "launcher_${num_workers}w,$num_workers,$start_workers,$workers_ready,$master_connected,$launcher_time" >> "$CSV_FILE"

        echo "Temps de lanceur: ${launcher_time}s"

        for hostname in $worker_hosts; do
            ssh $hostname "pkill -f WorkerNode" 2>/dev/null || true
        done

        sleep 2
    done
done

echo ""
echo " Mesures terminees!"
echo " Resultats: $CSV_FILE"
echo ""
echo " Generer les graphiques avec:"
echo "   python3 measurements/plot_launcher_time.py $CSV_FILE"