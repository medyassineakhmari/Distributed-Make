#!/bin/bash
set -e
ITERATIONS=${1:-3}
PROJECT_DIR="$HOME/Distributed-Make/Makefile"
CSV="$PROJECT_DIR/performances/data/raw_measurements.csv"
INPUT="$HOME/nfs_wordcount/huge_input.txt"

[ -z "$OAR_NODEFILE" ] && exit 1
NODES=$(cat $OAR_NODEFILE | sort -u | wc -l)

[ ! -f "$CSV" ] && echo "nodes,iteration,t_init_ms,t_split_ms,t_calc_ms,t_merge_ms,t_total_ms" > "$CSV"

for i in $(seq 1 $ITERATIONS); do
    rm -rf ~/nfs_wordcount/{part,count,total}*.txt ~/nfs_wordcount/Makefile.generated 2>/dev/null || true
    OUT=$(bash "$PROJECT_DIR/deploy/run_nfs_home.sh" "$INPUT" 2>&1)
    M=$(echo "$OUT" | grep "^\[METRICS_CSV\]" -A1 | tail -1)
    [ -z "$M" ] && continue
    echo "$NODES,$i,$(echo $M | cut -d, -f2-6)" >> "$CSV"
done
