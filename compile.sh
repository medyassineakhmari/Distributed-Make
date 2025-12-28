#!/bin/bash
echo "Compiling all Java files..."
javac src/*.java
if [ $? -eq 0 ]; then
    echo "[OK] Compilation successful"
else
    echo "[ERROR] Compilation failed"
    exit 1
fi