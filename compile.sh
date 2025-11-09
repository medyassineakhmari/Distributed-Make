#!/bin/bash
echo "Compiling all Java files..."
javac src/*.java
if [ $? -eq 0 ]; then
    echo "✓ Compilation successful"
else
    echo "❌ Compilation failed"
    exit 1
fi