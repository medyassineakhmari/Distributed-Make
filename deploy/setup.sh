#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   DISTRIBUTED WORD COUNT - Setup Script                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

mkdir -p bin

echo "Compiling Java files..."
echo "  - Compiling cluster management..."
javac -d bin src/cluster/*.java

echo "  - Compiling parser..."
javac -cp bin -d bin src/parser/*.java

echo "  - Compiling network (workers)..."
javac -cp bin -d bin src/network/worker/*.java

echo "  - Compiling network (master)..."
javac -cp bin -d bin src/network/master/*.java

echo "  - Compiling scheduler..."
javac -cp bin -d bin src/scheduler/*.java

echo ""
echo "Compiling wordcount program..."
gcc -o wordcount test/wordcount.c

echo ""
echo "Generating test data..."
bash test/generate_data.sh

echo ""
echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "  1. Reserve nodes: oarsub -I -l nodes=5"
echo "  2. Run: bash deploy/run_distributed.sh"
