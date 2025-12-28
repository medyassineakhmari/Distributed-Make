#!/usr/bin/env python3
"""
plot-ethernet-vs-opa.py
Compare Ethernet vs Omni-Path performance

Usage: python3 plot-ethernet-vs-opa.py
Requires: matplotlib, pandas
"""

import matplotlib.pyplot as plt
import pandas as pd
import sys

def plot_comparison():
    """Compare Ethernet (10G) vs Omni-Path (100G)"""
    
    try:
        df_eth = pd.read_csv('pingpong-ethernet.csv')
        df_opa = pd.read_csv('pingpong-opa.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure pingpong-ethernet.csv and pingpong-opa.csv exist")
        return False
    
    # Group by size (average)
    eth = df_eth.groupby('size_kb').mean()
    opa = df_opa.groupby('size_kb').mean()
    
    # Find common sizes
    common_sizes = sorted(set(eth.index) & set(opa.index))
    
    if not common_sizes:
        print("No common message sizes to compare")
        return False
    
    try:
        # GRAPH 1: RTT Comparison
        plt.figure(figsize=(12, 7))
        
        eth_rtt = eth.loc[common_sizes, 'rtt_ms']
        opa_rtt = opa.loc[common_sizes, 'rtt_ms']
        
        plt.plot(common_sizes, eth_rtt, 'o-', label='Ethernet (10G)', 
                 linewidth=2.5, markersize=8, color='#FF6B6B')
        plt.plot(common_sizes, opa_rtt, 's-', label='Omni-Path (100G)', 
                 linewidth=2.5, markersize=8, color='#4ECDC4')
        
        plt.xlabel('Message Size (KB)', fontsize=13, fontweight='bold')
        plt.ylabel('RTT (ms)', fontsize=13, fontweight='bold')
        plt.title('Latency Comparison: Ethernet (10G) vs Omni-Path (100G)', 
                  fontsize=15, fontweight='bold', pad=20)
        plt.legend(fontsize=12, loc='best')
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.tight_layout()
        plt.savefig('comparison-ethernet-vs-opa-rtt.png', dpi=300, bbox_inches='tight')
        print('[OK] comparison-ethernet-vs-opa-rtt.png created')
        plt.close()
        
        # GRAPH 2: Throughput Comparison
        plt.figure(figsize=(12, 7))
        
        eth_thr = eth.loc[common_sizes, 'throughput_mbps']
        opa_thr = opa.loc[common_sizes, 'throughput_mbps']
        
        # Filter out zero/negative throughputs
        valid_eth = eth_thr[eth_thr > 0]
        valid_opa = opa_thr[opa_thr > 0]
        
        if len(valid_eth) > 0:
            plt.plot(valid_eth.index, valid_eth, 'o-', label='Ethernet (10G)', 
                     linewidth=2.5, markersize=8, color='#FF6B6B')
        if len(valid_opa) > 0:
            plt.plot(valid_opa.index, valid_opa, 's-', label='Omni-Path (100G)', 
                     linewidth=2.5, markersize=8, color='#4ECDC4')
        
        plt.xlabel('Message Size (KB)', fontsize=13, fontweight='bold')
        plt.ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
        plt.title('Throughput Comparison: Ethernet (10G) vs Omni-Path (100G)', 
                  fontsize=15, fontweight='bold', pad=20)
        plt.legend(fontsize=12, loc='best')
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.tight_layout()
        plt.savefig('comparison-ethernet-vs-opa-throughput.png', dpi=300, bbox_inches='tight')
        print('[OK] comparison-ethernet-vs-opa-throughput.png created')
        plt.close()
        
        # Print summary
        print("\n=== Performance Summary ===")
        print(f"Ethernet (10G):")
        print(f"  Max throughput: {eth_thr.max():.2f} MB/s")
        print(f"  Min RTT: {eth_rtt.min():.3f} ms")
        print(f"\nOmni-Path (100G):")
        print(f"  Max throughput: {opa_thr.max():.2f} MB/s")
        print(f"  Min RTT: {opa_rtt.min():.3f} ms")
        print(f"\nPerformance Gain (OPA vs Ethernet):")
        if eth_thr.max() > 0:
            speedup_thr = opa_thr.max() / eth_thr.max()
            print(f"  Throughput: {speedup_thr:.2f}x faster")
        if opa_rtt.min() > 0:
            speedup_lat = eth_rtt.min() / opa_rtt.min()
            print(f"  Latency: {speedup_lat:.2f}x better")
        
        return True
        
    except Exception as e:
        print(f"Error generating plots: {e}")
        return False

if __name__ == '__main__':
    success = plot_comparison()
    sys.exit(0 if success else 1)
