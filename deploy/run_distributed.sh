#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   DISTRIBUTED WORD COUNT - Deployment Script            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ -z "$OAR_NODEFILE" ]; then
    echo "❌ Error: OAR_NODEFILE not found"
    echo "Please reserve nodes first: oarsub -I -l nodes=5"
    exit 1
fi

HOSTNAMES=$(uniq $OAR_NODEFILE)
MASTER_NODE=$(hostname)

echo "Master node: $MASTER_NODE"
echo ""
echo "Worker nodes:"
echo "$HOSTNAMES" | grep -v "$MASTER_NODE"
echo ""

echo "Copying files to all nodes..."
for hostname in $HOSTNAMES; do
    if [ "$hostname" != "$MASTER_NODE" ]; then
        echo "  - Copying to $hostname..."
        scp -r bin wordcount part*.txt wordcount.c $hostname:~ 2>/dev/null
    fi
done

echo ""
echo "Starting workers..."

for hostname in $HOSTNAMES; do
    if [ "$hostname" != "$MASTER_NODE" ]; then
        echo "  - Starting worker on $hostname..."
        ssh $hostname "cd ~ && java -cp bin network.worker.WorkerNode $hostname > worker.log 2>&1" &
        sleep 2
    fi
done

echo ""
echo "✅ All workers started!"
echo ""

WORKER_LIST=$(echo "$HOSTNAMES" | grep -v "$MASTER_NODE" | awk '{printf "\"%s\",", $0}' | sed 's/,$//')

echo "Starting master coordinator..."
echo "Worker list: [$WORKER_LIST]"
echo ""

java -cp bin scheduler.Main "[$WORKER_LIST]"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Execution completed!"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ -f total.txt ]; then
    TOTAL=$(cat total.txt)
    echo "📊 Total word count: $TOTAL"
    echo ""
    echo "Individual counts:"
    for i in {1..5}; do
        if [ -f count$i.txt ]; then
            COUNT=$(cat count$i.txt)
            echo "  - part$i.txt: $COUNT words"
        fi
    done
fi

echo ""
echo "Stopping workers..."
for hostname in $HOSTNAMES; do
    if [ "$hostname" != "$MASTER_NODE" ]; then
        ssh $hostname "pkill -f WorkerNode" 2>/dev/null
    fi
done

echo "✅ All done!"
