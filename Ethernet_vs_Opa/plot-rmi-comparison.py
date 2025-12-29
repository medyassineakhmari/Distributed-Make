#!/usr/bin/env python3
"""
plot-rmi-comparison.py
Compare RMI Baseline (no optimizations) vs Optimized (with 4 JVM properties)
"""

import matplotlib.pyplot as plt
import pandas as pd
import sys

def plot_rmi_comparison():
    try:
        df_base = pd.read_csv('pingpong-rmi-baseline.csv')
        df_opt = pd.read_csv('pingpong-rmi-optimized.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    
    base_grouped = df_base.groupby('size_kb').agg({
        'median_latency_ms': 'mean',
        'median_throughput_mbps': 'mean'
    }).reset_index()
    
    opt_grouped = df_opt.groupby('size_kb').agg({
        'median_latency_ms': 'mean',
        'median_throughput_mbps': 'mean'
    }).reset_index()
    
    merged = pd.merge(base_grouped, opt_grouped, on='size_kb', how='inner', suffixes=('_baseline', '_optimized'))
    
    if len(merged) == 0:
        print("Error: No common sizes")
        return False
    
    print(f"Found {len(merged)} common sizes for comparison")
    
    sizes = merged['size_kb']
    base_thr = merged['median_throughput_mbps_baseline']
    opt_thr = merged['median_throughput_mbps_optimized']
    thr_improvement = ((opt_thr - base_thr) / base_thr * 100)
    
    # Graph 1: Throughput Comparison
    plt.figure(figsize=(14, 8))
    bars_base = plt.bar(range(len(sizes)), base_thr, width=0.35, label='Baseline (No Optimization)', 
                       color='#FF6B6B', alpha=0.8)
    bars_opt = plt.bar([x + 0.35 for x in range(len(sizes))], opt_thr, width=0.35, 
                      label='Optimized (4 JVM Properties)', color='#4ECDC4', alpha=0.8)
    
    for i, (b, o) in enumerate(zip(base_thr, opt_thr)):
        improvement = thr_improvement.iloc[i]
        color = 'green' if improvement > 0 else 'red'
        symbol = '↑' if improvement > 0 else '↓'
        plt.text(i + 0.175, max(b, o) * 1.05, f'{symbol}{abs(improvement):.0f}%', 
                ha='center', fontsize=9, color=color, fontweight='bold')
    
    plt.xlabel('Message Size (KB)', fontsize=13, fontweight='bold')
    plt.ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
    plt.title('RMI Optimization Impact: Baseline vs 4 JVM Properties\n(DirectByteBuffer, No Proxy, Reduced Timeouts)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xticks(range(len(sizes)), [f'{int(s):,}' if s < 1024 else f'{s//1024}M' for s in sizes], rotation=45, ha='right')
    plt.legend(fontsize=12, loc='upper left')
    plt.grid(True, alpha=0.3, axis='y')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('comparison-rmi-baseline-vs-optimized-throughput.png', dpi=300, bbox_inches='tight')
    print('[OK] comparison-rmi-baseline-vs-optimized-throughput.png created')
    plt.close()
    
    # Graph 2: Improvement %
    plt.figure(figsize=(14, 7))
    colors = ['green' if x > 0 else 'red' for x in thr_improvement]
    bars = plt.bar(range(len(sizes)), thr_improvement, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    for i, (bar, val) in enumerate(zip(bars, thr_improvement)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontweight='bold')
    
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    plt.xlabel('Message Size (KB)', fontsize=13, fontweight='bold')
    plt.ylabel('Throughput Improvement (%)', fontsize=13, fontweight='bold')
    plt.title('RMI Optimization Improvement by Message Size', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xticks(range(len(sizes)), [f'{int(s):,}' if s < 1024 else f'{s//1024}M' for s in sizes], rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('comparison-rmi-optimization-improvement.png', dpi=300, bbox_inches='tight')
    print('[OK] comparison-rmi-optimization-improvement.png created')
    plt.close()
    
    # Summary
    print("\n" + "="*80)
    print("RMI OPTIMIZATION ANALYSIS SUMMARY")
    print("="*80)
    
    small_msgs = thr_improvement[merged['size_kb'] < 100].mean()
    medium_msgs = thr_improvement[(merged['size_kb'] >= 100) & (merged['size_kb'] < 1024)].mean()
    large_msgs = thr_improvement[merged['size_kb'] >= 1024].mean()
    overall = thr_improvement.mean()
    
    print(f"\nAverage Improvements by Message Size Category:")
    print(f"  Small messages   (< 100 KB):      {small_msgs:+.1f}%")
    print(f"  Medium messages  (100 KB - 1 MB): {medium_msgs:+.1f}%")
    print(f"  Large messages   (> 1 MB):        {large_msgs:+.1f}%")
    print(f"  OVERALL AVERAGE:                  {overall:+.1f}%")
    print("="*80)
    
    if overall > 15:
        print(f" VERDICT: RMI Optimizations provide {overall:.1f}% improvement - HIGHLY RECOMMENDED")
    elif overall > 0:
        print(f"⚠ VERDICT: Mixed results ({overall:.1f}%) - Use message-size-aware strategy")
    else:
        print(f"[ERROR] VERDICT: Optimizations not effective ({overall:.1f}%)")
    
    print("="*80)
    
    return True

if __name__ == '__main__':
    success = plot_rmi_comparison()
    sys.exit(0 if success else 1)
