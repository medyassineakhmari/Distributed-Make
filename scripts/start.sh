# ========== Network Diagnostic ==========
echo "Running network diagnostic..."
bash scripts/network-diagnostic.sh

# Save diagnostic output to file
bash scripts/network-diagnostic.sh > ~/pingpong/network-diagnostic-report.txt 2>&1

echo ""
echo "========== Compiling =========="
bash compile.sh

echo ""
echo "========== Running Tests =========="
echo ""
echo "Choose test mode:"
echo "  1) Single site (Normal + I/O) - DEFAULT"
echo "  2) Omni-Path vs Ethernet comparison"
echo "  3) RMI Optimized - Test with JVM tuning"
echo ""

# Default to single site if no input or if called without TTY
if [ -t 0 ]; then
    read -p "Enter choice [1-3] (default: 1): " choice
else
    choice=1
fi

case "${choice:-1}" in
    2)
        echo "Running Omni-Path vs Ethernet comparison test..."
        bash scripts/test-omnipath.sh
        ;;
    3)
        echo "Running RMI Optimized test (with JVM tuning)..."
        bash scripts/test-rmi-optimized.sh
        ;;
    *)
        echo "Running single site test (Normal + I/O)..."
        bash scripts/test-single-site.sh
        ;;
esac

echo ""
echo "========== Cleanup =========="
rm ~/pingpong.tar.gz