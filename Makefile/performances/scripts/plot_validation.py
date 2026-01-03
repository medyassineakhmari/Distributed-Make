#!/usr/bin/env python3
"""
Génération des graphiques de validation du modèle
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Chemins
PERF_DIR = os.path.expanduser("~/Distributed-Make/Makefile/performances")
RESULTS_DIR = f"{PERF_DIR}/results"
GRAPHS_DIR = f"{RESULTS_DIR}/graphs"
DATA_FILE = f"{PERF_DIR}/data/raw_measurements.csv"
CALIB_FILE = f"{RESULTS_DIR}/calibration_data.npz"

os.makedirs(GRAPHS_DIR, exist_ok=True)

def load_calibration():
    """Charge les données de calibration"""
    data = np.load(CALIB_FILE, allow_pickle=True)
    return {
        'nodes': data['nodes'],
        't_exp': data['t_exp'],
        't_theo': data['t_theo'],
        'error': data['error'],
        'stats': pd.DataFrame(data['stats'].item()),
        'params_init': data['params_init'].item(),
        'params_split': data['params_split'].item(),
        'params_calc': data['params_calc'].item()
    }

def plot_model_comparison(data):
    """Graphique 1: Comparaison Théorique vs Expérimental"""
    fig, ax = plt.subplots(figsize=(12, 7))

    nodes = data['nodes']
    t_exp = data['t_exp'] / 1000
    t_theo = data['t_theo'] / 1000

    stats = data['stats']
    t_exp_q25 = stats['t_total_q25'].values / 1000
    t_exp_q75 = stats['t_total_q75'].values / 1000

    ax.errorbar(nodes, t_exp,
                yerr=[t_exp - t_exp_q25, t_exp_q75 - t_exp],
                fmt='o-', label='Expérimental (médiane ± IQR)',
                linewidth=2.5, markersize=8, color='#e74c3c',
                capsize=5, capthick=2, elinewidth=2, alpha=0.9)

    ax.plot(nodes, t_theo, 's--', label='Modèle Théorique',
            linewidth=2.5, markersize=8, color='#2980b9', alpha=0.9)

    ax.set_xlabel('Nombre de Workers', fontsize=14, fontweight='bold')
    ax.set_ylabel('Temps Total (secondes)', fontsize=14, fontweight='bold')
    ax.set_title('Validation du Modèle Théorique', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(nodes)

    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/model_comparison.png", dpi=300)
    print(f" Graphique sauvegardé: model_comparison.png")

def plot_components_breakdown(data):
    """Graphique 2: Décomposition des composantes"""
    fig, ax = plt.subplots(figsize=(14, 8))

    stats = data['stats']
    nodes = stats['nodes'].values

    t_init = stats['t_init_med'].values / 1000
    t_split = stats['t_split_med'].values / 1000
    t_calc = stats['t_calc_med'].values / 1000
    t_merge = stats['t_merge_med'].values / 1000

    width = 0.6

    ax.bar(nodes, t_init, width, label='T_init (RMI lookups)', color='#3498db', alpha=0.9)
    ax.bar(nodes, t_split, width, bottom=t_init, label='T_split (File splitting)', color='#e74c3c', alpha=0.9)
    ax.bar(nodes, t_calc, width, bottom=t_init+t_split, label='T_calc (Parallel computation)', color='#2ecc71', alpha=0.9)
    ax.bar(nodes, t_merge, width, bottom=t_init+t_split+t_calc, label='T_merge (Aggregation)', color='#f39c12', alpha=0.9)

    ax.set_xlabel('Nombre de Workers', fontsize=14, fontweight='bold')
    ax.set_ylabel('Temps (secondes)', fontsize=14, fontweight='bold')
    ax.set_title('Décomposition des Temps d\'Exécution', fontsize=16, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.set_xticks(nodes)

    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/components_breakdown.png", dpi=300)
    print(f" Graphique sauvegardé: components_breakdown.png")

def plot_speedup_analysis(data):
    """Graphique 3: Analyse du speedup"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    stats = data['stats']
    nodes = stats['nodes'].values
    
    # FIX: Utiliser t_total au lieu de t_calc
    t_total = (stats['t_init_med'] + stats['t_split_med'] + 
               stats['t_calc_med'] + stats['t_merge_med']).values / 1000

    if nodes[0] == 1:
        t_ref = t_total[0]
    else:
        params_init = data['params_init']
        params_split = data['params_split']
        params_calc = data['params_calc']
        file_size = params_split['file_size_mb']
        
        t_init_1 = (params_init['alpha'] * 1 + params_init['beta']) / 1000
        t_split_1 = params_split['t_split_ms'] / 1000
        t_calc_1 = file_size / min(1 * params_calc['V_cpu'], params_calc['BW_nfs'])
        t_ref = t_init_1 + t_split_1 + t_calc_1

    speedup_actual = t_ref / t_total
    speedup_ideal = nodes.astype(float)
    efficiency = speedup_actual / speedup_ideal * 100

    ax1.plot(nodes, speedup_ideal, '--', color='gray', linewidth=2, label='Speedup Idéal (linéaire)', alpha=0.7)
    ax1.plot(nodes, speedup_actual, 'o-', color='#2980b9', linewidth=2.5, markersize=8, label='Speedup Réel')
    ax1.fill_between(nodes, speedup_actual, speedup_ideal, color='gray', alpha=0.1)

    n_sat = data['params_calc']['n_sat']
    ax1.axvline(x=n_sat, color='red', linestyle=':', linewidth=2, label=f'Saturation NFS (n={n_sat:.1f})')

    ax1.set_xlabel('Nombre de Workers', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Speedup (facteur d\'accélération)', fontsize=13, fontweight='bold')
    ax1.set_title('Analyse du Speedup', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(nodes)

    ax2.plot(nodes, efficiency, 'o-', color='#27ae60', linewidth=2.5, markersize=8)
    ax2.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Efficacité idéale (100%)')
    ax2.axvline(x=n_sat, color='red', linestyle=':', linewidth=2, label=f'Saturation (n={n_sat:.1f})')
    ax2.fill_between(nodes, 0, efficiency, color='#27ae60', alpha=0.2)

    ax2.set_xlabel('Nombre de Workers', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Efficacité Parallèle (%)', fontsize=13, fontweight='bold')
    ax2.set_title('Efficacité du Parallélisme', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xticks(nodes)
    ax2.set_ylim([0, 110])

    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/speedup_analysis.png", dpi=300)
    print(f" Graphique sauvegardé: speedup_analysis.png")

def plot_error_analysis(data):
    """Graphique 4: Analyse des erreurs"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    nodes = data['nodes']
    error = data['error']

    bars = ax1.bar(nodes, error, color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.axhline(y=5, color='green', linestyle='--', linewidth=2, label='Excellent (< 5%)', alpha=0.7)
    ax1.axhline(y=10, color='orange', linestyle='--', linewidth=2, label='Bon (< 10%)', alpha=0.7)

    for i, bar in enumerate(bars):
        if error[i] < 5:
            bar.set_color('#2ecc71')
        elif error[i] < 10:
            bar.set_color('#f39c12')
        else:
            bar.set_color('#e74c3c')

    ax1.set_xlabel('Nombre de Workers', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Erreur Relative (%)', fontsize=13, fontweight='bold')
    ax1.set_title('Erreur du Modèle par Configuration', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax1.set_xticks(nodes)

    ax2.hist(error, bins=10, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.axvline(x=error.mean(), color='red', linestyle='--', linewidth=2.5, label=f'Moyenne = {error.mean():.2f}%')
    ax2.axvline(x=np.median(error), color='green', linestyle='--', linewidth=2.5, label=f'Médiane = {np.median(error):.2f}%')

    ax2.set_xlabel('Erreur Relative (%)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Fréquence', fontsize=13, fontweight='bold')
    ax2.set_title('Distribution des Erreurs', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/error_analysis.png", dpi=300)
    print(f" Graphique sauvegardé: error_analysis.png")

def main():
    print("╗")
    print("         GÉNÉRATION DES GRAPHIQUES DE VALIDATION          ")
    print("╝\n")

    print(" Chargement des données de calibration...")
    data = load_calibration()

    print("\n Génération des graphiques...")
    plot_model_comparison(data)
    plot_components_breakdown(data)
    plot_speedup_analysis(data)
    plot_error_analysis(data)

    print(f"\n Tous les graphiques sauvegardés dans: {GRAPHS_DIR}/")
    print("\nGraphiques générés:")
    print("  1. model_comparison.png       - Comparaison théorique vs expérimental")
    print("  2. components_breakdown.png   - Décomposition des temps")
    print("  3. speedup_analysis.png       - Analyse speedup et efficacité")
    print("  4. error_analysis.png         - Analyse des erreurs du modèle")

if __name__ == "__main__":
    main()
