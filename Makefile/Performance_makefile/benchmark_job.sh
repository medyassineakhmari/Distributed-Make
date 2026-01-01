#!/bin/bash

PROJECT_DIR="$HOME/wordcount-distributed"
INPUT_FILE="huge_input.txt"
CSV_FILE="$PROJECT_DIR/benchmark_results.csv"
ITERATIONS=3

cd "$PROJECT_DIR"

if [ ! -f "$CSV_FILE" ]; then
    echo "Nodes,Iteration,Split_Time_ms,Distrib_Exec_Start_ms,Total_Time_ms" > "$CSV_FILE"
fi

NODE_COUNT=$(cat $OAR_NODEFILE | uniq | wc -l)
echo "Demarrage du benchmark pour $NODE_COUNT noeuds ($ITERATIONS iterations)"

for ((i=1; i<=ITERATIONS; i++)); do
    echo "------------------------------------------------"
    echo "Iteration $i/$ITERATIONS sur $NODE_COUNT noeuds..."

    OUTPUT=$(bash deploy/run_nfs_home.sh "$INPUT_FILE" 2>&1)

    if echo "$OUTPUT" | grep -q "Execution completed!"; then

        T_SPLIT=$(echo "$OUTPUT" | grep "FILE_SPLITTED" | tr -d -c 0-9)

        T_DIST_START=$(echo "$OUTPUT" | grep "DISTRIBUTED_EXECUTION_START" | tr -d -c 0-9)

        T_TOTAL=$(echo "$OUTPUT" | grep "EXECUTION_COMPLETED" | tr -d -c 0-9)

        if [[ -n "$T_SPLIT" && -n "$T_DIST_START" && -n "$T_TOTAL" ]]; then
            echo "Succes: Split=${T_SPLIT}ms, StartDist=${T_DIST_START}ms, Total=${T_TOTAL}ms"

            echo "$NODE_COUNT,$i,$T_SPLIT,$T_DIST_START,$T_TOTAL" >> "$CSV_FILE"
        else
            echo "Erreur de parsing des logs pour l'iteration $i"
            echo "Extrait du log : $(echo "$OUTPUT" | grep "TIMING REPORT" -A 10)"
        fi
    else
        echo "Echec de l'execution lors de l'iteration $i"
        echo "$OUTPUT" > "error_log_${NODE_COUNT}_nodes_iter_${i}.txt"
    fi

    sleep 5
done

echo "Benchmark termine pour $NODE_COUNT noeuds."