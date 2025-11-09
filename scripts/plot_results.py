#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd
import sys

def plot_single_site():
    """Graphes 1 & 2: Comparaison Normal vs I/O"""
    
    # Charger données
    df_normal = pd.read_csv('pingpong-normal.csv')
    df_io = pd.read_csv('pingpong-io.csv')
    
    # Grouper par taille (moyenne)
    normal = df_normal.groupby('size_kb').mean()
    io = df_io.groupby('size_kb').mean()
    
    # GRAPHE 1: RTT
    plt.figure(figsize=(10, 6))
    plt.plot(normal.index, normal['rtt_ms'], 'o-', label='Ping Pong', linewidth=2, markersize=6, color='red')
    plt.plot(io.index, io['rtt_ms'], 's-', label='Ping Pong IO', linewidth=2, markersize=6, color='blue')
    plt.xlabel('Size (KB)', fontsize=12)
    plt.ylabel('RTT (ms)', fontsize=12)
    plt.title('Comparison of Ping Pong vs Ping Pong IO', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig('comparison_rtt.png', dpi=300)
    print('✓ comparison_rtt.png created')
    
    # GRAPHE 2: Throughput
    plt.figure(figsize=(10, 6))
    valid_normal = normal[normal['throughput_mbps'] > 0]
    valid_io = io[io['throughput_mbps'] > 0]
    
    plt.plot(valid_normal.index, valid_normal['throughput_mbps'], 
             'o-', label='Ping Pong', linewidth=2, markersize=6, color='orange')
    plt.plot(valid_io.index, valid_io['throughput_mbps'], 
             's-', label='Ping Pong IO', linewidth=2, markersize=6, color='green')
    plt.xlabel('Size (KB)', fontsize=12)
    plt.ylabel('Throughput (Mbits/s)', fontsize=12)
    plt.title('Comparison of Ping Pong vs Ping Pong IO', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig('comparison_throughput.png', dpi=300)
    print('✓ comparison_throughput.png created')

def plot_sites_comparison():
    """Graphe 3: Comparaison multi-sites"""
    
    df = pd.read_csv('sites-comparison.csv')
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    width = 0.35
    
    # Barres latence (axe gauche)
    ax1.bar([i - width/2 for i in x], df['latency_ms'], width, 
            label='Latency', color='steelblue')
    ax1.set_xlabel('Sites', fontsize=12)
    ax1.set_ylabel('Latency (ms)', color='steelblue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='steelblue')
    
    # Barres throughput (axe droit)
    ax2 = ax1.twinx()
    ax2.bar([i + width/2 for i in x], df['throughput_mbps'], width,
            label='Throughput', color='orange')
    ax2.set_ylabel('Throughput (Mbytes/s)', color='orange', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='orange')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['site'], rotation=45, ha='right')
    ax1.set_title('Latency and Throughput Comparison', fontsize=14, fontweight='bold')
    
    fig.tight_layout()
    plt.savefig('sites_comparison.png', dpi=300)
    print('✓ sites_comparison.png created')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'single'
    
    if mode == 'single':
        plot_single_site()
    elif mode == 'sites':
        plot_sites_comparison()
    else:
        print('Usage: python3 plot_results.py [single|sites]')