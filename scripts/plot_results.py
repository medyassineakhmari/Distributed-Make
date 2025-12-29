#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd
import sys
import numpy as np
import os

def plot_single_site():
    """Graphes: Comparaison Normal vs I/O avec Médiane et IQR"""
    
    # Vérification basique
    if not os.path.exists('pingpong-normal.csv') or not os.path.exists('pingpong-io.csv'):
        print("Erreur: Fichiers CSV introuvables.")
        return

    # Charger données
    df_normal = pd.read_csv('pingpong-normal.csv')
    df_io = pd.read_csv('pingpong-io.csv')
    
    # ========================================
    # GRAPHE 1: Latence (RTT) - Médiane & IQR
    # ========================================
    plt.figure(figsize=(12, 7))
    
    # Calcul des erreurs asymétriques pour les barres d'erreur (Q1 à Q3)
    # yerr attend [lower_error, upper_error]
    norm_lat_err = [
        df_normal['median_latency_ms'] - df_normal['p25_latency_ms'],
        df_normal['p75_latency_ms'] - df_normal['median_latency_ms']
    ]
    
    io_lat_err = [
        df_io['median_latency_ms'] - df_io['p25_latency_ms'],
        df_io['p75_latency_ms'] - df_io['median_latency_ms']
    ]
    
    # Tracer
    plt.errorbar(df_normal['size_kb'], df_normal['median_latency_ms'], 
                 yerr=norm_lat_err,
                 fmt='o-', label='Ping Pong (RAM)', linewidth=2, markersize=6, 
                 color='red', capsize=4, elinewidth=1.5, alpha=0.9)
    
    plt.errorbar(df_io['size_kb'], df_io['median_latency_ms'], 
                 yerr=io_lat_err,
                 fmt='s-', label='Ping Pong IO', linewidth=2, markersize=6, 
                 color='blue', capsize=4, elinewidth=1.5, alpha=0.9)
    
    plt.xlabel('Size (KB)', fontsize=13, fontweight='bold')
    plt.ylabel('Latency (ms)', fontsize=13, fontweight='bold')
    plt.title('Comparison: Latency (Median & IQR)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=12, loc='best')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xscale('log')
    plt.yscale('log') # Log scale souvent utile pour la latence
    plt.tight_layout()
    plt.savefig('comparison_rtt.png', dpi=300)
    print('[OK] comparison_rtt.png created')
    
    # ========================================
    # GRAPHE 2: Throughput (Débit) - Médiane & IQR
    # ========================================
    plt.figure(figsize=(12, 7))
    
    # Filtrer les valeurs positives (sécurité)
    df_norm_valid = df_normal[df_normal['median_throughput_mbps'] > 0]
    df_io_valid = df_io[df_io['median_throughput_mbps'] > 0]
    
    # Calcul des erreurs IQR pour le débit
    norm_thr_err = [
        df_norm_valid['median_throughput_mbps'] - df_norm_valid['p25_throughput_mbps'],
        df_norm_valid['p75_throughput_mbps'] - df_norm_valid['median_throughput_mbps']
    ]
    
    io_thr_err = [
        df_io_valid['median_throughput_mbps'] - df_io_valid['p25_throughput_mbps'],
        df_io_valid['p75_throughput_mbps'] - df_io_valid['median_throughput_mbps']
    ]
    
    # Tracer
    plt.errorbar(df_norm_valid['size_kb'], df_norm_valid['median_throughput_mbps'], 
                 yerr=norm_thr_err,
                 fmt='o-', label='Ping Pong (RAM)', linewidth=2, markersize=6, 
                 color='orange', capsize=4, elinewidth=1.5, alpha=0.9)
    
    plt.errorbar(df_io_valid['size_kb'], df_io_valid['median_throughput_mbps'], 
                 yerr=io_thr_err,
                 fmt='s-', label='Ping Pong IO', linewidth=2, markersize=6, 
                 color='green', capsize=4, elinewidth=1.5, alpha=0.9)
    
    plt.xlabel('Size (KB)', fontsize=13, fontweight='bold')
    plt.ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
    plt.title('Comparison: Throughput (Median & IQR)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=12, loc='best')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig('comparison_throughput.png', dpi=300)
    print('[OK] comparison_throughput.png created')

    # Note: J'ai retiré le graphe de variation détaillé car les colonnes min/max 
    # ne sont plus présentes dans le nouveau CSV Java optimisé.


def plot_sites_comparison():
    """Graphe 3: Comparaison multi-sites (si le fichier existe)"""
    if not os.path.exists('sites-comparison.csv'):
        print("Info: 'sites-comparison.csv' introuvable, graphe ignoré.")
        return

    df = pd.read_csv('sites-comparison.csv')
    df['site_short'] = df['site'].str.split(' ').str[0]
    df = df.sort_values('latency_ms')
    
    fig, ax1 = plt.subplots(figsize=(14, 7))
    x = range(len(df))
    width = 0.35
    
    # Barres latence
    ax1.bar([i - width/2 for i in x], df['latency_ms'], width, 
            label='Latency', color='steelblue', alpha=0.8)
    ax1.set_xlabel('Sites', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Latency (ms)', color='steelblue', fontsize=13, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='steelblue')
    
    # Barres throughput
    ax2 = ax1.twinx()
    ax2.bar([i + width/2 for i in x], df['throughput_mbps'], width,
            label='Throughput', color='orange', alpha=0.8)
    ax2.set_ylabel('Throughput (MB/s)', color='orange', fontsize=13, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='orange')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['site_short'], rotation=45, ha='right')
    ax1.set_title('Grid5000 Sites Comparison', fontsize=15, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('sites_comparison.png', dpi=300, bbox_inches='tight')
    print('[OK] sites_comparison.png created')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'single'
    
    if mode == 'single':
        plot_single_site()
    elif mode == 'sites':
        plot_sites_comparison()
    else:
        print('Usage: python3 plot_results.py [single|sites]')