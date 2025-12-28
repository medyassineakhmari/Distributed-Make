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
import os

def plot_comparison():
    """Compare Ethernet (10G) vs Omni-Path (100G) with error bars"""
    
    try:
        df_eth = pd.read_csv('pingpong-ethernet.csv')
        df_opa = pd.read_csv('pingpong-opa.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure pingpong-ethernet.csv and pingpong-opa.csv exist")
        return False
    
    # Extract median and percentile values for Ethernet
    eth_grouped = df_eth.groupby('size_kb').agg({
        'median_latency_ms': 'mean',
        'p25_latency_ms': 'mean',
        'p75_latency_ms': 'mean',
        'median_throughput_mbps': 'mean',
        'p25_throughput_mbps': 'mean',
        'p75_throughput_mbps': 'mean'
    }).reset_index()
    
    # OPA now also has percentile columns
    opa_grouped = df_opa.groupby('size_kb').agg({
        'median_latency_ms': 'mean',
        'p25_latency_ms': 'mean',
        'p75_latency_ms': 'mean',
        'median_throughput_mbps': 'mean',
        'p25_throughput_mbps': 'mean',
        'p75_throughput_mbps': 'mean'
    }).reset_index()
    
    # Merge on common sizes
    merged = pd.merge(eth_grouped, opa_grouped, on='size_kb', how='inner', suffixes=('_eth', '_opa'))
    
    if len(merged) == 0:
        print("Error: No common message sizes between Ethernet and OPA")
        return False
    
    print(f"Found {len(merged)} common sizes for comparison")
    
    try:
        sizes = merged['size_kb']
        
        # GRAPH 1: Latency Comparison with Error Bars
        plt.figure(figsize=(12, 7))
        
        eth_lat = merged['median_latency_ms_eth']
        eth_lat_err_low = eth_lat - merged['p25_latency_ms_eth']
        eth_lat_err_high = merged['p75_latency_ms_eth'] - eth_lat
        
        opa_lat = merged['median_latency_ms_opa']
        opa_lat_err_low = opa_lat - merged['p25_latency_ms_opa']
        opa_lat_err_high = merged['p75_latency_ms_opa'] - opa_lat
        
        plt.errorbar(sizes, eth_lat, yerr=[eth_lat_err_low, eth_lat_err_high], 
                     fmt='o-', label='Ethernet (10G)', 
                     linewidth=2.5, markersize=8, color='#FF6B6B', capsize=5, capthick=2)
        plt.errorbar(sizes, opa_lat, yerr=[opa_lat_err_low, opa_lat_err_high],
                     fmt='s-', label='Omni-Path (100G)', 
                     linewidth=2.5, markersize=8, color='#4ECDC4', capsize=5, capthick=2)
        
        plt.xlabel('Message Size (KB)', fontsize=13, fontweight='bold')
        plt.ylabel('Latency (ms)', fontsize=13, fontweight='bold')
        plt.title('Latency Comparison: Ethernet (10G) vs Omni-Path (100G)\n(Before RMI Optimization)', 
                  fontsize=15, fontweight='bold', pad=20)
        plt.legend(fontsize=12, loc='best')
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.text(0.98, 0.02, 'Baseline Test - RMI Optimization TBD', 
                ha='right', va='bottom', transform=plt.gca().transAxes,
                fontsize=10, style='italic', color='gray', alpha=0.7)
        plt.tight_layout()
        plt.savefig('comparison-ethernet-vs-opa-latency.png', dpi=300, bbox_inches='tight')
        print('✓ comparison-ethernet-vs-opa-latency.png created')
        plt.close()
        
        # GRAPH 2: Throughput Comparison with Error Bars
        plt.figure(figsize=(12, 7))
        
        eth_thr = merged['median_throughput_mbps_eth']
        eth_thr_err_low = eth_thr - merged['p25_throughput_mbps_eth']
        eth_thr_err_high = merged['p75_throughput_mbps_eth'] - eth_thr
        
        opa_thr = merged['median_throughput_mbps_opa']
        opa_thr_err_low = opa_thr - merged['p25_throughput_mbps_opa']
        opa_thr_err_high = merged['p75_throughput_mbps_opa'] - opa_thr
        
        plt.errorbar(sizes, eth_thr, yerr=[eth_thr_err_low, eth_thr_err_high], 
                     fmt='o-', label='Ethernet (10G)', 
                     linewidth=2.5, markersize=8, color='#FF6B6B', capsize=5, capthick=2)
        plt.errorbar(sizes, opa_thr, yerr=[opa_thr_err_low, opa_thr_err_high],
                     fmt='s-', label='Omni-Path (100G)', 
                     linewidth=2.5, markersize=8, color='#4ECDC4', capsize=5, capthick=2)
        
        plt.xlabel('Message Size (KB)', fontsize=13, fontweight='bold')
        plt.ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
        plt.title('Throughput Comparison: Ethernet (10G) vs Omni-Path (100G)\n(Before RMI Optimization)', 
                  fontsize=15, fontweight='bold', pad=20)
        plt.legend(fontsize=12, loc='best')
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.yscale('log')
        plt.text(0.98, 0.02, 'Baseline Test - RMI Optimization TBD', 
                ha='right', va='bottom', transform=plt.gca().transAxes,
                fontsize=10, style='italic', color='gray', alpha=0.7)
        plt.tight_layout()
        plt.savefig('comparison-ethernet-vs-opa-throughput.png', dpi=300, bbox_inches='tight')
        print('✓ comparison-ethernet-vs-opa-throughput.png created')
        plt.close()
        
        # Print summary statistics
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)
        print(f"\nEthernet (10G):")
        print(f"  Max throughput: {eth_thr.max():.2f} MB/s (at {merged.loc[eth_thr.idxmax(), 'size_kb']:.0f} KB)")
        print(f"  Min latency: {eth_lat.min():.4f} ms (at {merged.loc[eth_lat.idxmin(), 'size_kb']:.0f} KB)")
        print(f"\nOmni-Path (100G):")
        print(f"  Max throughput: {opa_thr.max():.2f} MB/s (at {merged.loc[opa_thr.idxmax(), 'size_kb']:.0f} KB)")
        print(f"  Min latency: {opa_lat.min():.4f} ms (at {merged.loc[opa_lat.idxmin(), 'size_kb']:.0f} KB)")
        print(f"\nPerformance Comparison (OPA vs Ethernet):")
        speedup_thr = opa_thr.max() / eth_thr.max() if eth_thr.max() > 0 else 0
        speedup_lat = eth_lat.min() / opa_lat.min() if opa_lat.min() > 0 else 0
        print(f"  Throughput speedup: {speedup_thr:.2f}x faster")
        print(f"  Latency speedup: {speedup_lat:.2f}x faster")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"Error generating plots: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = plot_comparison()
    sys.exit(0 if success else 1)
