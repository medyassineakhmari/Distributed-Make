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
    """Graphe 3: Comparaison multi-sites (version corrigée)"""
    df = pd.read_csv('sites-comparison.csv')
    
    # Extraire juste le nom du site (avant le premier espace ou parenthèse)
    df['site_short'] = df['site'].str.split(' ').str[0]
    
    # Trier par latence croissante pour meilleure lisibilité
    df = df.sort_values('latency_ms')
    
    fig, ax1 = plt.subplots(figsize=(14, 7))
    x = range(len(df))
    width = 0.35
    
    # Barres latence (axe gauche)
    bars1 = ax1.bar([i - width/2 for i in x], df['latency_ms'], width, 
                     label='Latency', color='steelblue', alpha=0.8)
    ax1.set_xlabel('Sites', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Latency (ms)', color='steelblue', fontsize=13, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='steelblue', labelsize=11)
    
    # Forcer l'axe Y gauche à commencer à 0
    ax1.set_ylim(bottom=0, top=df['latency_ms'].max() * 1.15)
    
    # Barres throughput (axe droit)
    ax2 = ax1.twinx()
    bars2 = ax2.bar([i + width/2 for i in x], df['throughput_mbps'], width,
                     label='Throughput', color='orange', alpha=0.8)
    ax2.set_ylabel('Throughput (Mbytes/s)', color='orange', fontsize=13, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='orange', labelsize=11)
    
    # Forcer l'axe Y droit à commencer à 0
    ax2.set_ylim(bottom=0, top=df['throughput_mbps'].max() * 1.15)
    
    # Labels des sites
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['site_short'], rotation=45, ha='right', fontsize=11)
    
    # Titre
    ax1.set_title('Latency and Throughput Comparison Across Grid5000 Sites', 
                  fontsize=15, fontweight='bold', pad=20)
    
    # Ajouter valeurs sur les barres
    for i, (lat, thr) in enumerate(zip(df['latency_ms'], df['throughput_mbps'])):
        # Valeur latence
        ax1.text(i - width/2, lat + df['latency_ms'].max()*0.02, 
                f'{lat:.3f}', ha='center', va='bottom', fontsize=9, color='steelblue')
        # Valeur throughput
        ax2.text(i + width/2, thr + df['throughput_mbps'].max()*0.02, 
                f'{thr:.0f}', ha='center', va='bottom', fontsize=9, color='orange')
    
    # Légende combinée
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
    
    # Grille pour meilleure lisibilité
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    fig.tight_layout()
    plt.savefig('sites_comparison.png', dpi=300, bbox_inches='tight')
    print('✓ sites_comparison.png created')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'single'
    
    if mode == 'single':
        plot_single_site()
    elif mode == 'sites':
        plot_sites_comparison()
    else:
        print('Usage: python3 plot_results.py [single|sites]')