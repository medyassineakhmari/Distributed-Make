#!/usr/bin/env python3
"""
Génération de graphiques scientifiques pour validation de modèle théorique
Projet: Système Make Distribué avec NFS
Version: Finale - Zoom Optimal (Y=3) et Efficacité Théorique incluse
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

# Configuration matplotlib pour qualité publication
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.markersize'] = 7

# Chemins
PERF_DIR = os.path.expanduser("~/Distributed-Make/Makefile/performances")
RESULTS_DIR = f"{PERF_DIR}/results"
GRAPHS_DIR = f"{RESULTS_DIR}/graphs"
CALIB_FILE = f"{RESULTS_DIR}/calibration_data.npz"

os.makedirs(GRAPHS_DIR, exist_ok=True)

# Palette de couleurs scientifique
COLORS = {
    'primary': '#2E86AB',    # Bleu (Mesures Speedup)
    'secondary': '#A23B72',  # Magenta (Théorie)
    'success': '#06A77D',    # Vert (Mesures Efficacité)
    'warning': '#F18F01',    # Orange
    'danger': '#C73E1D',     # Rouge
    'neutral': '#6C757D'     # Gris
}

def load_data():
    """Charge les données de calibration"""
    try:
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
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {CALIB_FILE} est introuvable.")
        exit(1)

def calculate_reference_time(data):
    """Calcul de T(1) pour les références de speedup"""
    params_init = data['params_init']
    params_split = data['params_split']
    params_calc = data['params_calc']
    file_size = params_split['file_size_mb']

    t_init_1 = (params_init['alpha'] * 1 + params_init['beta']) / 1000
    t_split_1 = params_split['t_split_med'] / 1000 
    t_calc_1 = file_size / min(1 * params_calc['V_cpu'], params_calc['BW_nfs'])
    t_merge_1 = 0 

    t_ref = t_init_1 + t_split_1 + t_calc_1 + t_merge_1
    return t_ref, {'t_init_1': t_init_1}

# --- FONCTIONS DE DESSIN ---

def plot_1_model_validation(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    nodes = data['nodes']
    t_exp = data['t_exp'] / 1000
    t_theo = data['t_theo'] / 1000
    stats_df = data['stats']
    t_q25 = stats_df['t_total_q25'].values / 1000
    t_q75 = stats_df['t_total_q75'].values / 1000

    ax.errorbar(nodes, t_exp, yerr=[t_exp - t_q25, t_q75 - t_exp],
                fmt='o', label='Données expérimentales',
                color=COLORS['danger'], capsize=5, markersize=7)
    ax.plot(nodes, t_theo, 's--', label='Modèle théorique',
            color=COLORS['primary'], markersize=7)
    ax.fill_between(nodes, t_q25, t_q75, alpha=0.15, color=COLORS['danger'])

    ax.set_xlabel('Nombre de workers', fontweight='bold')
    ax.set_ylabel('Temps d\'exécution total (s)', fontweight='bold')
    ax.set_title('Validation du Modèle Théorique', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_xticks(nodes)
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig1_model_validation.png", dpi=300)
    print(" Figure 1: Validation")

def plot_2_speedup_efficiency_separated(data):
    """Figure 2: Speedup et Efficacité (Mesuré vs Théorique)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    t_total = (stats_df['t_init_med'] + stats_df['t_split_med'] +
               stats_df['t_calc_med'] + stats_df['t_merge_med']).values / 1000
    t_theo = data['t_theo'] / 1000
    t_ref, _ = calculate_reference_time(data)

    # Calculs Speedup
    speedup_measured = t_ref / t_total
    speedup_theo = t_ref / t_theo
    
    # Calculs Efficacité
    efficiency_measured = (speedup_measured / nodes) * 100
    efficiency_theo = (speedup_theo / nodes) * 100
    
    n_sat = data['params_calc']['n_sat']

    # --- PANNEAU 1 : SPEEDUP ---
    y_limit_zoom = 3.0 # Zoom sur les données réelles

    ax1.plot(nodes, nodes, '--', color=COLORS['neutral'],
             linewidth=1.5, label='Speedup idéal', alpha=0.4)
    
    ax1.plot(nodes, speedup_theo, 'x--', color=COLORS['secondary'],
             linewidth=2.0, markersize=7, label='Modèle Théorique', alpha=0.9)

    ax1.plot(nodes, speedup_measured, 'o-', color=COLORS['primary'],
             linewidth=2.5, markersize=8, label='Mesures Expérimentales', zorder=10)

    ax1.axvline(x=n_sat, color=COLORS['danger'], linestyle=':',
                linewidth=2.5, label=f'Saturation NFS (n≈{n_sat:.0f})')
    
    ax1.axvspan(0, n_sat, alpha=0.05, color=COLORS['success'])
    ax1.axvspan(n_sat, nodes[-1], alpha=0.05, color=COLORS['warning'])

    ax1.set_xlabel('Nombre de workers', fontweight='bold')
    ax1.set_ylabel('Speedup (x)', fontweight='bold')
    ax1.set_title('(a) Validation du Speedup', fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.set_xticks(nodes)
    ax1.set_ylim([0, y_limit_zoom]) 

    # --- PANNEAU 2 : EFFICACITÉ ---
    ax2.axhline(y=100, color=COLORS['neutral'], linestyle='--', 
                linewidth=1.5, alpha=0.6, label='Idéal (100%)')
    
    # Efficacité Théorique (Magenta, croix)
    ax2.plot(nodes, efficiency_theo, 'x--', color=COLORS['secondary'],
             linewidth=2.0, markersize=7, label='Efficacité Théorique', alpha=0.9)
    
    # Efficacité Mesurée (Vert, ronds)
    ax2.plot(nodes, efficiency_measured, 'o-', color=COLORS['success'],
             linewidth=2.5, markersize=8, label='Efficacité Mesurée', zorder=10)
    
    ax2.axvline(x=n_sat, color=COLORS['danger'], linestyle=':', linewidth=2.5)
    ax2.fill_between(nodes, 0, efficiency_measured, color=COLORS['success'], alpha=0.2)
    
    ax2.set_xlabel('Nombre de workers', fontweight='bold')
    ax2.set_ylabel('Efficacité (%)', fontweight='bold')
    ax2.set_title('(b) Validation de l\'Efficacité', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, linestyle=':')
    ax2.set_xticks(nodes)
    ax2.set_ylim([0, 110])

    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig2_speedup_efficiency.png", dpi=300)
    print(" Figure 2: Speedup + Efficacité (Théorie incluse partout)")

def plot_3_time_decomposition(data):
    fig, ax = plt.subplots(figsize=(12, 6))
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    t_init = stats_df['t_init_med'].values / 1000
    t_split = stats_df['t_split_med'].values / 1000
    t_calc = stats_df['t_calc_med'].values / 1000
    t_merge = stats_df['t_merge_med'].values / 1000
    
    x = np.arange(len(nodes))
    width = 0.65

    ax.bar(x, t_init, width, label='T_init', color='#3498DB')
    ax.bar(x, t_split, width, bottom=t_init, label='T_split', color='#E74C3C')
    ax.bar(x, t_calc, width, bottom=t_init+t_split, label='T_calc', color='#2ECC71')
    ax.bar(x, t_merge, width, bottom=t_init+t_split+t_calc, label='T_merge', color='#F39C12')

    ax.set_xlabel('Nombre de workers', fontweight='bold')
    ax.set_ylabel('Temps (s)', fontweight='bold')
    ax.set_title('Décomposition Temporelle', fontweight='bold')
    ax.legend(ncol=2)
    ax.set_xticks(x)
    ax.set_xticklabels(nodes)
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig3_time_decomposition.png", dpi=300)
    print(" Figure 3: Décomposition")

def plot_4_error_distribution(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    nodes = data['nodes']
    error = data['error']

    bars = ax1.bar(range(len(nodes)), error, color=COLORS['neutral'], edgecolor='black')
    for bar, err in zip(bars, error):
        bar.set_color(COLORS['success'] if err < 5 else COLORS['danger'])
    
    ax1.set_xlabel('Workers', fontweight='bold')
    ax1.set_ylabel('Erreur (%)', fontweight='bold')
    ax1.set_title('Erreur par config', fontweight='bold')
    ax1.set_xticks(range(len(nodes)))
    ax1.set_xticklabels(nodes)

    ax2.hist(error, bins=8, color=COLORS['primary'], edgecolor='black')
    ax2.set_xlabel('Erreur (%)', fontweight='bold')
    ax2.set_title('Distribution', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig4_error_analysis.png", dpi=300)
    print(" Figure 4: Erreurs")

def plot_5_amdahl_law(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    t_split = stats_df['t_split_med'].values / 1000
    t_total = (stats_df['t_init_med'] + stats_df['t_split_med'] + 
               stats_df['t_calc_med'] + stats_df['t_merge_med']).values / 1000
    t_ref, _ = calculate_reference_time(data)
    speedup = t_ref / t_total

    n_range = np.linspace(1, 20, 100)
    for f, c in zip([0.1, 0.5, 0.75, 0.9], ['green', 'blue', 'orange', 'purple']):
        ax.plot(n_range, 1/(f+(1-f)/n_range), '--', color=c, alpha=0.5, label=f'Amdahl {f:.0%}')
    
    ax.plot(nodes, speedup, 'o-', color=COLORS['danger'], linewidth=3, label='Mesuré')
    ax.plot(n_range, n_range, 'k:', alpha=0.5)
    
    ax.set_xlabel('Workers', fontweight='bold')
    ax.set_ylabel('Speedup', fontweight='bold')
    ax.set_title('Loi d\'Amdahl', fontweight='bold')
    ax.legend()
    ax.set_ylim([0, 10])
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig5_amdahl_law.png", dpi=300)
    print(" Figure 5: Amdahl")

def plot_6_nfs_saturation(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    t_calc = stats_df['t_calc_med'].values / 1000
    
    params = data['params_calc']
    n_range = np.linspace(1, 20, 200)
    file_size = data['params_split']['file_size_mb']
    t_calc_theo = file_size / np.minimum(n_range * params['V_cpu'], params['BW_nfs'])

    ax.plot(n_range, t_calc_theo, '--', color=COLORS['primary'], label='Modèle')
    ax.plot(nodes, t_calc, 'o', color=COLORS['danger'], label='Mesures')
    ax.axvline(x=params['n_sat'], color='red', linestyle=':')
    
    ax.set_xlabel('Workers', fontweight='bold')
    ax.set_ylabel('Temps Calcul (s)', fontweight='bold')
    ax.set_title('Saturation NFS', fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig6_nfs_saturation.png", dpi=300)
    print(" Figure 6: Saturation")

def main():
    print("\n=== GÉNÉRATION GRAPHIQUES ===")
    data = load_data()
    plot_1_model_validation(data)
    plot_2_speedup_efficiency_separated(data)
    plot_3_time_decomposition(data)
    plot_4_error_distribution(data)
    plot_5_amdahl_law(data)
    plot_6_nfs_saturation(data)
    print(f"\nTerminé ! Images dans : {GRAPHS_DIR}")

if __name__ == "__main__":
    main()
