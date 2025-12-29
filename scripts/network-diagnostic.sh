#!/bin/bash

#############################################
# Network Diagnostic Script for Grid5000
# Détecte quel réseau est utilisé (Ethernet vs Omni-Path/InfiniBand)
#############################################

echo "========================================="
echo "   Grid5000 Network Diagnostic Report"
echo "========================================="
echo ""

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========== 1. INTERFACES RÉSEAU ==========
echo -e "${BLUE}1. Network Interfaces${NC}"
echo "---"
ip -br addr show br0 ib0 2>/dev/null
if [ $? -ne 0 ]; then
    echo "No br0/ib0 found, listing all interfaces:"
    ip -br addr
fi
echo ""

# ========== 2. TABLE DE ROUTAGE ==========
echo -e "${BLUE}2. Routing Table${NC}"
echo "---"
ip route
echo ""

# ========== 3. RÉSEAU UTILISÉ PER WORKER ==========
if [ -n "$OAR_NODE_FILE" ] && [ -f "$OAR_NODE_FILE" ]; then
    echo -e "${BLUE}3. Network Path to Each Worker (from $HOSTNAME)${NC}"
    echo "---"
    
    for node in $(cat $OAR_NODE_FILE | sort -u); do
        if [ "$node" != "$(hostname)" ]; then
            IP=$(getent hosts $node 2>/dev/null | awk '{print $1}')
            if [ -z "$IP" ]; then
                echo -e "${RED}✗ $node${NC} (cannot resolve hostname)"
            else
                ROUTE_OUTPUT=$(ip route get $IP 2>/dev/null)
                IFACE=$(echo "$ROUTE_OUTPUT" | grep -o "dev [^ ]*" | awk '{print $2}')
                
                if [[ "$IFACE" == "ib0" ]]; then
                    echo -e "${GREEN}[OK] $node${NC} ($IP) -> ${GREEN}ib0 (Omni-Path/InfiniBand - FAST)${NC}"
                elif [[ "$IFACE" == "br0" ]] || [[ "$IFACE" == eth* ]]; then
                    echo -e "${YELLOW}⊙ $node${NC} ($IP) -> ${YELLOW}$IFACE (Ethernet - STANDARD)${NC}"
                else
                    echo -e "? $node ($IP) -> $IFACE"
                fi
            fi
        fi
    done
    echo ""
fi

# ========== 4. OMNI-PATH / INFINIBAND INFO ==========
echo -e "${BLUE}4. High-Speed Interconnect (Omni-Path/InfiniBand)${NC}"
echo "---"

if [ -d "/sys/class/infiniband/hfi1_0" ]; then
    echo -e "${GREEN}Omni-Path detected (Intel HFI1)${NC}"
    RATE=$(cat /sys/class/infiniband/hfi1_0/ports/1/rate 2>/dev/null)
    STATE=$(cat /sys/class/infiniband/hfi1_0/ports/1/state 2>/dev/null)
    PHYS=$(cat /sys/class/infiniband/hfi1_0/ports/1/phys_state 2>/dev/null)
    echo "  Rate: $RATE"
    echo "  State: $STATE"
    echo "  Physical State: $PHYS"
elif [ -d "/sys/class/infiniband" ] && [ "$(ls -1 /sys/class/infiniband 2>/dev/null | wc -l)" -gt 0 ]; then
    echo -e "${GREEN}InfiniBand detected${NC}"
    for device in /sys/class/infiniband/*; do
        DEV_NAME=$(basename "$device")
        RATE=$(cat "$device/ports/1/rate" 2>/dev/null)
        STATE=$(cat "$device/ports/1/state" 2>/dev/null)
        echo "  Device: $DEV_NAME"
        echo "    Rate: $RATE"
        echo "    State: $STATE"
    done
else
    echo -e "${YELLOW}No Omni-Path or InfiniBand detected${NC}"
fi
echo ""

# ========== 5. ETHERNET INFO ==========
echo -e "${BLUE}5. Ethernet Speed${NC}"
echo "---"

    if [ -d "/sys/class/net/br0/brif" ]; then
        IFACES=$(ls /sys/class/net/br0/brif/ 2>/dev/null)
        if [ -n "$IFACES" ]; then
            for iface in $IFACES; do
                # Try to read speed from sysfs (no sudo required on most systems)
                SPEED_FILE="/sys/class/net/$iface/speed"
                OPERSTATE_FILE="/sys/class/net/$iface/operstate"
                CARRIER_FILE="/sys/class/net/$iface/carrier"

                SPEED="unknown"
                if [ -r "$SPEED_FILE" ]; then
                    SPEED_VAL=$(cat "$SPEED_FILE" 2>/dev/null)
                    if [ "$SPEED_VAL" != "-1" ]; then
                        SPEED="${SPEED_VAL}Mb/s"
                    fi
                fi

                OPERSTATE="$(cat "$OPERSTATE_FILE" 2>/dev/null || echo unknown)"
                CARRIER="$(cat "$CARRIER_FILE" 2>/dev/null || echo unknown)"

                echo "  Interface $iface (behind br0):"
                echo "    Speed: $SPEED"
                echo "    Operstate: $OPERSTATE"
                echo "    Carrier: $CARRIER"
            done
        fi
    elif [ -n "$(ip -br link | grep -E '(^| )eth0( |$)')" ]; then
        iface=eth0
        SPEED_FILE="/sys/class/net/$iface/speed"
        OPERSTATE_FILE="/sys/class/net/$iface/operstate"
        SPEED="unknown"
        if [ -r "$SPEED_FILE" ]; then
            SPEED_VAL=$(cat "$SPEED_FILE" 2>/dev/null)
            if [ "$SPEED_VAL" != "-1" ]; then
                SPEED="${SPEED_VAL}Mb/s"
            fi
        fi
        OPERSTATE="$(cat "$OPERSTATE_FILE" 2>/dev/null || echo unknown)"
        echo "  Interface $iface:"
        echo "    Speed: $SPEED"
        echo "    Operstate: $OPERSTATE"
    else
        echo "  No Ethernet interface found or permission denied to read sysfs entries"
    fi
echo ""

# ========== 6. RÉSUMÉ & RECOMMANDATIONS ==========
echo -e "${BLUE}6. Summary & Recommendations${NC}"
echo "---"

# Déterminer quel réseau sera utilisé par défaut
DEFAULT_ROUTE=$(ip route | grep "^default" | awk '{print $3}' | head -1)
DEFAULT_IFACE=$(ip route | grep "^default" | awk '{print $5}' | head -1)

if [[ "$DEFAULT_IFACE" == "ib0" ]]; then
    echo -e "${GREEN}Default route uses ib0 (Omni-Path/InfiniBand)${NC}"
    echo "[OK] Your PingPong tests will use the FAST network"
elif [[ "$DEFAULT_IFACE" == "br0" ]] || [[ "$DEFAULT_IFACE" == eth* ]]; then
    echo -e "${YELLOW}Default route uses $DEFAULT_IFACE (Ethernet)${NC}"
    
    # Vérifier si Omni-Path/IB est disponible mais pas utilisé
    if [ -d "/sys/class/infiniband/hfi1_0" ] || [ -d "/sys/class/infiniband" ]; then
        echo -e "${YELLOW}⚠ Warning: Omni-Path/InfiniBand is available but NOT the default route${NC}"
        echo "  Your hostnames may resolve to Ethernet IPs (172.16.x.x)"
        echo "  Recommendation: Verify if you should be using the HPC network"
    fi
fi
echo ""

# IP resolution check
if [ -n "$OAR_NODE_FILE" ] && [ -f "$OAR_NODE_FILE" ]; then
    SAMPLE_NODE=$(cat $OAR_NODE_FILE | grep -v "$(hostname)" | head -1)
    if [ -n "$SAMPLE_NODE" ]; then
        echo -e "Example hostname resolution:"
        echo "  Hostname: $SAMPLE_NODE"
        SAMPLE_IPS=$(getent ahosts $SAMPLE_NODE 2>/dev/null)
        echo "  IPs returned by getent:"
        echo "$SAMPLE_IPS" | sed 's/^/    /'
    fi
fi

echo ""
echo "========================================="
echo "Diagnostic complete"
echo "========================================="
