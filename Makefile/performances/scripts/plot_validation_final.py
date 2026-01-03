#!/usr/bin/env python3
"""
Génération de graphiques scientifiques pour validation de modèle théorique
Projet: Système Make Distribué avec NFS
Version: Finale Corrigée
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

# Configuration matplotlib pour qualité publication
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.markersize'] = 8

# Chemins
PERF_DIR = os.path.expanduser("~/Distributed-Make/Makefile/performances")
RESULTS_DIR = f"{PERF_DIR}/results"
GRAPHS_DIR = f"{RESULTS_DIR}/graphs"
CALIB_FILE = f"{RESULTS_DIR}/calibration_data.npz"

os.makedirs(GRAPHS_DIR, exist_ok=True)

# Palette de couleurs scientifique
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'neutral': '#6C757D'
}

def load_data():
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

def calculate_reference_time(data):
    """
    Calcul rigoureux de T(1) - temps avec 1 worker
    Formule: T(1) = T_init(1) + T_split + T_calc(1) + T_merge
    """
    params_init = data['params_init']
    params_split = data['params_split']
    params_calc = data['params_calc']
    
    file_size = params_split['file_size_mb']
    
    # Toutes les phases pour n=1 (en secondes)
    t_init_1 = (params_init['alpha'] * 1 + params_init['beta']) / 1000
    t_split_1 = params_split['t_split_med'] / 1000  # Clé corrigée
    t_calc_1 = file_size / min(1 * params_calc['V_cpu'], params_calc['BW_nfs'])
    t_merge_1 = 0  # Négligeable selon les mesures
    
    t_ref = t_init_1 + t_split_1 + t_calc_1 + t_merge_1
    
    return t_ref, {
        't_init_1': t_init_1,
        't_split_1': t_split_1,
        't_calc_1': t_calc_1,
        't_merge_1': t_merge_1
    }

def plot_1_model_validation(data):
    """Figure 1: Validation du Modèle Théorique"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    nodes = data['nodes']
    t_exp = data['t_exp'] / 1000
    t_theo = data['t_theo'] / 1000
    stats_df = data['stats']
    
    t_q25 = stats_df['t_total_q25'].values / 1000
    t_q75 = stats_df['t_total_q75'].values / 1000
    
    # Données expérimentales avec intervalles
    ax.errorbar(nodes, t_exp, 
                yerr=[t_exp - t_q25, t_q75 - t_exp],
                fmt='o', label='Données expérimentales',
                color=COLORS['danger'], capsize=5, capthick=2,
                markersize=7, elinewidth=2, alpha=0.9)
    
    # Modèle théorique
    ax.plot(nodes, t_theo, 's--', label='Modèle théorique',
            color=COLORS['primary'], markersize=7, linewidth=2.5)
    
    # Zone de confiance
    ax.fill_between(nodes, t_q25, t_q75, alpha=0.15, 
                     color=COLORS['danger'], label='IQR expérimental')
    
    ax.set_xlabel('Nombre de workers', fontweight='bold')
    ax.set_ylabel('Temps d\'exécution total (s)', fontweight='bold')
    ax.set_title('Validation du Modèle Théorique de Performance', 
                 fontweight='bold', pad=15)
    ax.legend(loc='upper right', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    ax.set_xticks(nodes)
    
    err_mean = data['error'].mean()
    ax.text(0.98, 0.02, f'Erreur moyenne: {err_mean:.2f}%',
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig1_model_validation.png", dpi=300, bbox_inches='tight')
    print(" Figure 1: Validation du modèle")

def plot_2_speedup_efficiency(data):
    """Figure 2: Analyse de Scalabilité"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    
    # Temps total mesuré
    t_total = (stats_df['t_init_med'] + stats_df['t_split_med'] + 
               stats_df['t_calc_med'] + stats_df['t_merge_med']).values / 1000
    
    # Temps de référence T(1)
    t_ref, components = calculate_reference_time(data)
    
    speedup = t_ref / t_total
    efficiency = (speedup / nodes) * 100
    n_sat = data['params_calc']['n_sat']
    
    # === Subplot 1: Speedup ===
    ax1.plot(nodes, nodes, '--', color=COLORS['neutral'], 
             linewidth=2, label='Speedup idéal (linéaire)', alpha=0.6)
    ax1.plot(nodes, speedup, 'o-', color=COLORS['primary'], 
             linewidth=2.5, markersize=8, label='Speedup mesuré')
    ax1.fill_between(nodes, speedup, nodes, color=COLORS['neutral'], alpha=0.1)
    
    ax1.axvline(x=n_sat, color=COLORS['danger'], linestyle=':', 
                linewidth=2, label=f'Saturation NFS (n≈{n_sat:.0f})')
    
    ax1.axvspan(0, n_sat, alpha=0.05, color=COLORS['success'])
    ax1.axvspan(n_sat, nodes[-1], alpha=0.05, color=COLORS['warning'])
    
    ax1.set_xlabel('Nombre de workers', fontweight='bold')
    ax1.set_ylabel('Speedup (×)', fontweight='bold')
    ax1.set_title('(a) Facteur d\'Accélération', fontweight='bold')
    ax1.legend(loc='upper left', frameon=True)
    ax1.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    ax1.set_xticks(nodes)
    ax1.set_ylim([0, max(speedup.max(), nodes[-1]/2) * 1.2])
    
    # === Subplot 2: Efficacité ===
    ax2.plot(nodes, efficiency, 'o-', color=COLORS['success'], 
             linewidth=2.5, markersize=8)
    ax2.axhline(y=100, color=COLORS['neutral'], linestyle='--', 
                linewidth=1.5, alpha=0.6, label='Efficacité idéale')
    ax2.axvline(x=n_sat, color=COLORS['danger'], linestyle=':', 
                linewidth=2, label=f'Saturation (n≈{n_sat:.0f})')
    ax2.fill_between(nodes, 0, efficiency, color=COLORS['success'], alpha=0.2)
    
    ax2.axhspan(80, 100, alpha=0.1, color=COLORS['success'])
    ax2.axhspan(60, 80, alpha=0.1, color=COLORS['warning'])
    
    ax2.set_xlabel('Nombre de workers', fontweight='bold')
    ax2.set_ylabel('Efficacité (%)', fontweight='bold')
    ax2.set_title('(b) Efficacité Parallèle', fontweight='bold')
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    ax2.set_xticks(nodes)
    ax2.set_ylim([0, 110])
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig2_speedup_efficiency.png", dpi=300, bbox_inches='tight')
    print(" Figure 2: Speedup et efficacité")

def plot_3_time_decomposition(data):
    """Figure 3: Décomposition Temporelle par Phase"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    
    t_init = stats_df['t_init_med'].values / 1000
    t_split = stats_df['t_split_med'].values / 1000
    t_calc = stats_df['t_calc_med'].values / 1000
    t_merge = stats_df['t_merge_med'].values / 1000
    t_total = t_init + t_split + t_calc + t_merge
    
    width = 0.65
    x = np.arange(len(nodes))
    
    # Stacked bars
    p1 = ax.bar(x, t_init, width, label='T_init (Initialisation RMI)',
                color='#3498DB', edgecolor='white', linewidth=1.5)
    p2 = ax.bar(x, t_split, width, bottom=t_init,
                label='T_split (Découpage fichier)',
                color='#E74C3C', edgecolor='white', linewidth=1.5)
    p3 = ax.bar(x, t_calc, width, bottom=t_init+t_split,
                label='T_calc (Calcul parallèle)',
                color='#2ECC71', edgecolor='white', linewidth=1.5)
    p4 = ax.bar(x, t_merge, width, bottom=t_init+t_split+t_calc,
                label='T_merge (Agrégation)',
                color='#F39C12', edgecolor='white', linewidth=1.5)
    
    # Annotations pourcentages
    for i, n in enumerate(nodes):
        pct_split = (t_split[i] / t_total[i]) * 100
        if pct_split > 5:
            ax.text(i, t_init[i] + t_split[i]/2, f'{pct_split:.0f}%',
                   ha='center', va='center', fontweight='bold',
                   color='white', fontsize=9)
        
        pct_calc = (t_calc[i] / t_total[i]) * 100
        if pct_calc > 5:
            ax.text(i, t_init[i] + t_split[i] + t_calc[i]/2, f'{pct_calc:.0f}%',
                   ha='center', va='center', fontweight='bold',
                   color='white', fontsize=9)
    
    ax.set_xlabel('Nombre de workers', fontweight='bold')
    ax.set_ylabel('Temps d\'exécution (s)', fontweight='bold')
    ax.set_title('Décomposition Temporelle par Phase d\'Exécution', 
                 fontweight='bold', pad=15)
    ax.legend(loc='upper right', frameon=True, shadow=True, ncol=2)
    ax.grid(True, alpha=0.3, axis='y', linestyle=':', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(nodes)
    
    ax.axhline(y=t_split[0], color='red', linestyle='--', 
               linewidth=1.5, alpha=0.5)
    ax.text(len(nodes)-0.5, t_split[0]+0.5, 'Bottleneck séquentiel',
           fontsize=9, color='red', ha='right')
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig3_time_decomposition.png", dpi=300, bbox_inches='tight')
    print(" Figure 3: Décomposition temporelle")

def plot_4_error_distribution(data):
    """Figure 4: Analyse de l'Erreur du Modèle"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    nodes = data['nodes']
    error = data['error']
    
    # === Subplot 1: Erreur par configuration ===
    bars = ax1.bar(range(len(nodes)), error, color=COLORS['neutral'],
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    
    for i, (bar, err) in enumerate(zip(bars, error)):
        if err < 5:
            bar.set_color(COLORS['success'])
        elif err < 10:
            bar.set_color(COLORS['warning'])
        else:
            bar.set_color(COLORS['danger'])
    
    ax1.axhline(y=5, color=COLORS['success'], linestyle='--', 
                linewidth=2, alpha=0.7)
    ax1.axhline(y=10, color=COLORS['warning'], linestyle='--', 
                linewidth=2, alpha=0.7)
    
    ax1.set_xlabel('Nombre de workers', fontweight='bold')
    ax1.set_ylabel('Erreur relative (%)', fontweight='bold')
    ax1.set_title('(a) Erreur du Modèle par Configuration', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y', linestyle=':', linewidth=0.8)
    ax1.set_xticks(range(len(nodes)))
    ax1.set_xticklabels(nodes)
    
    handles = [mpatches.Patch(color=COLORS['success'], label='Excellent (< 5%)'),
               mpatches.Patch(color=COLORS['warning'], label='Bon (< 10%)'),
               mpatches.Patch(color=COLORS['danger'], label='Acceptable (≥ 10%)')]
    ax1.legend(handles=handles, loc='upper left', frameon=True)
    
    # === Subplot 2: Distribution statistique ===
    ax2.hist(error, bins=8, color=COLORS['primary'], alpha=0.7,
             edgecolor='black', linewidth=1.5, density=False)
    
    mean_err = error.mean()
    median_err = np.median(error)
    std_err = error.std()
    
    ax2.axvline(x=mean_err, color=COLORS['danger'], linestyle='--',
                linewidth=2.5, label=f'Moyenne: {mean_err:.2f}%')
    ax2.axvline(x=median_err, color=COLORS['success'], linestyle='--',
                linewidth=2.5, label=f'Médiane: {median_err:.2f}%')
    
    ax2.set_xlabel('Erreur relative (%)', fontweight='bold')
    ax2.set_ylabel('Fréquence', fontweight='bold')
    ax2.set_title('(b) Distribution des Erreurs', fontweight='bold')
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, alpha=0.3, axis='y', linestyle=':', linewidth=0.8)
    
    textstr = f'μ = {mean_err:.2f}%\nσ = {std_err:.2f}%\nmax = {error.max():.2f}%'
    ax2.text(0.98, 0.97, textstr, transform=ax2.transAxes,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig4_error_analysis.png", dpi=300, bbox_inches='tight')
    print(" Figure 4: Analyse des erreurs")

def plot_5_amdahl_law(data):
    """Figure 5: Illustration de la Loi d'Amdahl"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    
    t_split = stats_df['t_split_med'].values / 1000
    t_total = (stats_df['t_init_med'] + stats_df['t_split_med'] + 
               stats_df['t_calc_med'] + stats_df['t_merge_med']).values / 1000
    
    # Fraction séquentielle
    f_seq = t_split / t_total
    
    # Courbes théoriques d'Amdahl
    n_range = np.linspace(1, 20, 100)
    fractions = [0.1, 0.25, 0.5, 0.75, 0.9]
    colors_amdahl = ['#27AE60', '#3498DB', '#F39C12', '#E74C3C', '#8E44AD']
    
    for f, c in zip(fractions, colors_amdahl):
        speedup_amdahl = 1 / (f + (1-f)/n_range)
        ax.plot(n_range, speedup_amdahl, '--', color=c, linewidth=1.5,
               alpha=0.6, label=f'Amdahl f_seq={f:.0%}')
    
    # Speedup mesuré
    t_ref, _ = calculate_reference_time(data)
    speedup_measured = t_ref / t_total
    
    ax.plot(nodes, speedup_measured, 'o-', color=COLORS['danger'],
           linewidth=3, markersize=9, label='Speedup mesuré', zorder=10)
    
    ax.plot(n_range, n_range, 'k:', linewidth=2, alpha=0.5, 
           label='Speedup idéal')
    
    ax.set_xlabel('Nombre de workers', fontweight='bold')
    ax.set_ylabel('Speedup (×)', fontweight='bold')
    ax.set_title('Loi d\'Amdahl: Impact de la Partie Séquentielle', 
                 fontweight='bold', pad=15)
    ax.legend(loc='upper left', frameon=True, fontsize=9)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    ax.set_xlim([0, 20])
    ax.set_ylim([0, 10])
    
    f_seq_avg = f_seq.mean()
    ax.text(0.98, 0.02, f'Fraction séquentielle moyenne: {f_seq_avg:.1%}',
           transform=ax.transAxes, ha='right', va='bottom',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
           fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig5_amdahl_law.png", dpi=300, bbox_inches='tight')
    print(" Figure 5: Loi d'Amdahl")

def plot_6_nfs_saturation(data):
    """Figure 6: Analyse de la Saturation NFS"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    stats_df = data['stats']
    nodes = stats_df['nodes'].values
    t_calc = stats_df['t_calc_med'].values / 1000
    
    params_calc = data['params_calc']
    n_sat = params_calc['n_sat']
    V_cpu = params_calc['V_cpu']
    BW_nfs = params_calc['BW_nfs']
    file_size = data['params_split']['file_size_mb']
    
    # Courbe théorique
    n_range = np.linspace(1, 20, 200)
    t_calc_theo = file_size / np.minimum(n_range * V_cpu, BW_nfs)
    
    ax.plot(n_range, t_calc_theo, '--', color=COLORS['primary'],
           linewidth=2.5, label='Modèle théorique', alpha=0.8)
    ax.plot(nodes, t_calc, 'o', color=COLORS['danger'],
           markersize=9, label='Données expérimentales', zorder=10)
    
    ax.axvline(x=n_sat, color=COLORS['danger'], linestyle=':',
              linewidth=2.5, label=f'Saturation NFS (n≈{n_sat:.0f})')
    ax.axvspan(0, n_sat, alpha=0.1, color=COLORS['success'], 
              label='Zone scalable')
    ax.axvspan(n_sat, 20, alpha=0.1, color=COLORS['warning'],
              label='Zone saturée')
    
    t_min = file_size / BW_nfs
    ax.axhline(y=t_min, color='gray', linestyle='--',
              linewidth=1.5, alpha=0.6)
    ax.text(19, t_min + 0.3, f'Limite NFS: {t_min:.1f}s',
           ha='right', fontsize=9, color='gray')
    
    ax.set_xlabel('Nombre de workers', fontweight='bold')
    ax.set_ylabel('Temps de calcul T_calc (s)', fontweight='bold')
    ax.set_title('Analyse de la Saturation du Système de Fichiers NFS',
                fontweight='bold', pad=15)
    ax.legend(loc='upper right', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    ax.set_xlim([0, 20])
    ax.set_ylim([0, t_calc.max() * 1.2])
    
    textstr = f'V_cpu = {V_cpu:.1f} MB/s\nBW_NFS = {BW_nfs:.0f} MB/s'
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
           fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{GRAPHS_DIR}/fig6_nfs_saturation.png", dpi=300, bbox_inches='tight')
    print(" Figure 6: Saturation NFS")

def main():
    print("\n" + "="*70)
    print("   GÉNÉRATION DE GRAPHIQUES SCIENTIFIQUES - QUALITÉ PUBLICATION")
    print("="*70 + "\n")
    
    print("Chargement des données de calibration...")
    data = load_data()
    
    # Afficher T(1) calculé
    t_ref, components = calculate_reference_time(data)
    print(f"\n Temps de référence T(1) = {t_ref:.2f}s")
    print(f"  - T_init(1) = {components['t_init_1']:.3f}s")
    print(f"  - T_split   = {components['t_split_1']:.2f}s")
    print(f"  - T_calc(1) = {components['t_calc_1']:.2f}s")
    print(f"  - T_merge   = {components['t_merge_1']:.3f}s")
    
    print("\nGénération des 6 figures scientifiques:\n")
    plot_1_model_validation(data)
    plot_2_speedup_efficiency(data)
    plot_3_time_decomposition(data)
    plot_4_error_distribution(data)
    plot_5_amdahl_law(data)
    plot_6_nfs_saturation(data)
    
    print("\n" + "="*70)
    print(f" Tous les graphiques sauvegardés dans: {GRAPHS_DIR}/")
    print("="*70)
    
    print("\nFigures générées (300 DPI, qualité publication):")
    print("  Fig 1: Validation du modèle théorique")
    print("  Fig 2: Speedup et efficacité parallèle")
    print("  Fig 3: Décomposition temporelle par phase")
    print("  Fig 4: Analyse statistique des erreurs")
    print("  Fig 5: Illustration de la loi d'Amdahl")
    print("  Fig 6: Analyse de la saturation NFS")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
