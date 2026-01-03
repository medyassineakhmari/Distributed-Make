#!/usr/bin/env python3
"""
Calibration du modèle théorique à partir des mesures expérimentales
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import sys
import os

# Chemins
PERF_DIR = os.path.expanduser("~/Distributed-Make/Makefile/performances")
DATA_FILE = f"{PERF_DIR}/data/raw_measurements.csv"
RESULTS_DIR = f"{PERF_DIR}/results"
CALIB_FILE = f"{RESULTS_DIR}/calibration_report.txt"

# Créer dossier résultats
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data():
    """Charge et agrège les données"""
    if not os.path.exists(DATA_FILE):
        print(f" ERREUR: Fichier de données introuvable - {DATA_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    
    print(f" Données chargées: {len(df)} mesures")
    print(f"  Configurations: {df['nodes'].unique()}")
    print(f"  Itérations par config: {df.groupby('nodes').size().min()}-{df.groupby('nodes').size().max()}")
    
    return df

def compute_statistics(df):
    """Calcule médiane et IQR pour chaque configuration"""
    stats = df.groupby('nodes').agg({
        't_init_ms': ['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)],
        't_split_ms': ['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)],
        't_calc_ms': ['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)],
        't_merge_ms': ['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)],
        't_total_ms': ['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)]
    }).reset_index()
    
    # Renommer colonnes
    stats.columns = ['nodes', 
                     't_init_med', 't_init_q25', 't_init_q75',
                     't_split_med', 't_split_q25', 't_split_q75',
                     't_calc_med', 't_calc_q25', 't_calc_q75',
                     't_merge_med', 't_merge_q25', 't_merge_q75',
                     't_total_med', 't_total_q25', 't_total_q75']
    
    return stats

def calibrate_init(stats):
    """Calibre T_init(n) = α × n + β"""
    def model(n, alpha, beta):
        return alpha * n + beta
    
    nodes = stats['nodes'].values
    t_init = stats['t_init_med'].values
    
    params, cov = curve_fit(model, nodes, t_init)
    alpha, beta = params
    
    # Erreur standard
    perr = np.sqrt(np.diag(cov))
    
    # R²
    residuals = t_init - model(nodes, *params)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((t_init - np.mean(t_init))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return {
        'alpha': alpha,
        'beta': beta,
        'alpha_err': perr[0],
        'beta_err': perr[1],
        'r_squared': r_squared
    }

def calibrate_split(stats):
    """Calibre T_split = S / BW_write (constant)"""
    t_split_med = stats['t_split_med'].median()
    t_split_std = stats['t_split_med'].std()
    
    # Taille fichier (à ajuster selon votre fichier)
    file_size_mb = 1700  # 1.5 GB
    
    BW_write = file_size_mb / (t_split_med / 1000)  # MB/s
    
    return {
        't_split_med': t_split_med,
        't_split_std': t_split_std,
        'BW_write': BW_write,
        'file_size_mb': file_size_mb
    }

def calibrate_calc(stats, file_size_mb):
    """Calibre T_calc(n) = S / min(n × V_cpu, BW_nfs)"""
    def model(n, V_cpu, BW_nfs):
        return file_size_mb / np.minimum(n * V_cpu, BW_nfs) * 1000
    
    nodes = stats['nodes'].values
    t_calc = stats['t_calc_med'].values
    
    # Bounds: V_cpu ∈ [1, 100], BW_nfs ∈ [50, 1000]
    params, cov = curve_fit(model, nodes, t_calc, 
                           bounds=([1, 50], [100, 1000]),
                           maxfev=10000)
    V_cpu, BW_nfs = params
    
    perr = np.sqrt(np.diag(cov))
    n_sat = BW_nfs / V_cpu
    
    # R²
    residuals = t_calc - model(nodes, *params)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((t_calc - np.mean(t_calc))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return {
        'V_cpu': V_cpu,
        'BW_nfs': BW_nfs,
        'V_cpu_err': perr[0],
        'BW_nfs_err': perr[1],
        'n_sat': n_sat,
        'r_squared': r_squared
    }

def compute_theoretical_model(stats, params_init, params_split, params_calc):
    """Calcule T_théorique pour chaque configuration"""
    nodes = stats['nodes'].values
    
    t_init_theo = params_init['alpha'] * nodes + params_init['beta']
    t_split_theo = np.full_like(nodes, params_split['t_split_med'], dtype=float)
    t_calc_theo = params_split['file_size_mb'] / np.minimum(
        nodes * params_calc['V_cpu'], 
        params_calc['BW_nfs']
    ) * 1000
    t_merge_theo = stats['t_merge_med'].median()
    
    t_total_theo = t_init_theo + t_split_theo + t_calc_theo + t_merge_theo
    
    return t_init_theo, t_split_theo, t_calc_theo, t_total_theo

def generate_report(stats, params_init, params_split, params_calc):
    """Génère rapport de calibration"""
    
    # Calcul modèle théorique
    t_init_theo, t_split_theo, t_calc_theo, t_total_theo = compute_theoretical_model(
        stats, params_init, params_split, params_calc
    )
    
    # Erreur relative
    error = np.abs(t_total_theo - stats['t_total_med'].values) / stats['t_total_med'].values * 100
    
    report = []
    report.append("╗")
    report.append("            RAPPORT DE CALIBRATION DU MODÈLE                      ")
    report.append("╝")
    report.append("")
    
    report.append(" 1. PARAMÈTRES CALIBRÉS ")
    report.append("")
    report.append("T_init(n) = α × n + β")
    report.append(f"  α = {params_init['alpha']:.2f} ± {params_init['alpha_err']:.2f} ms/worker")
    report.append(f"  β = {params_init['beta']:.2f} ± {params_init['beta_err']:.2f} ms")
    report.append(f"  R² = {params_init['r_squared']:.4f}")
    report.append("")
    
    report.append("T_split(S) = S / BW_write")
    report.append(f"  S = {params_split['file_size_mb']:.0f} MB")
    report.append(f"  BW_write = {params_split['BW_write']:.2f} MB/s")
    report.append(f"  T_split = {params_split['t_split_med']:.2f} ± {params_split['t_split_std']:.2f} ms")
    report.append("")
    
    report.append("T_calc(n, S) = S / min(n × V_cpu, BW_nfs)")
    report.append(f"  V_cpu = {params_calc['V_cpu']:.2f} ± {params_calc['V_cpu_err']:.2f} MB/s")
    report.append(f"  BW_nfs = {params_calc['BW_nfs']:.2f} ± {params_calc['BW_nfs_err']:.2f} MB/s")
    report.append(f"  n_sat = {params_calc['n_sat']:.2f} workers")
    report.append(f"  R² = {params_calc['r_squared']:.4f}")
    report.append("")
    
    report.append(" 2. VALIDATION MODÈLE ")
    report.append("")
    report.append(f"{'n':<6} {'T_exp(s)':<12} {'T_theo(s)':<12} {'Erreur(%)':<12}")
    report.append("" * 50)
    
    for i, n in enumerate(stats['nodes'].values):
        t_exp = stats['t_total_med'].values[i] / 1000
        t_theo = t_total_theo[i] / 1000
        err = error[i]
        report.append(f"{n:<6} {t_exp:<12.2f} {t_theo:<12.2f} {err:<12.2f}")
    
    report.append("" * 50)
    report.append(f"Erreur moyenne: {error.mean():.2f}%")
    report.append(f"Erreur max: {error.max():.2f}%")
    report.append("")
    
    report.append(" 3. INTERPRÉTATION ")
    report.append("")
    if error.mean() < 5:
        report.append(" EXCELLENT: Modèle très précis (erreur < 5%)")
    elif error.mean() < 10:
        report.append(" BON: Modèle validé (erreur < 10%)")
    else:
        report.append("⚠ À INVESTIGUER: Erreur > 10% - Paramètres manquants?")
    
    report.append("")
    report.append("Point de saturation NFS:")
    report.append(f"  - Au-delà de {params_calc['n_sat']:.0f} workers, T_calc ne diminue plus")
    report.append(f"  - Bande passante NFS devient le goulot d'étranglement")
    report.append("")
    
    # Sauvegarder
    with open(CALIB_FILE, 'w') as f:
        f.write('\n'.join(report))
    
    # Afficher
    for line in report:
        print(line)
    
    print(f"\n Rapport sauvegardé: {CALIB_FILE}")
    
    return {
        'nodes': stats['nodes'].values,
        't_exp': stats['t_total_med'].values,
        't_theo': t_total_theo,
        'error': error,
        'params_init': params_init,
        'params_split': params_split,
        'params_calc': params_calc
    }

def main():
    print("╗")
    print("         CALIBRATION DU MODÈLE THÉORIQUE                  ")
    print("╝\n")
    
    # 1. Charger données
    df = load_data()
    
    # 2. Calculer statistiques
    print("\n Calcul des statistiques (médiane + IQR)...")
    stats = compute_statistics(df)
    
    # 3. Calibrer chaque composante
    print("\n Calibration de T_init(n)...")
    params_init = calibrate_init(stats)
    
    print(" Calibration de T_split(S)...")
    params_split = calibrate_split(stats)
    
    print(" Calibration de T_calc(n, S)...")
    params_calc = calibrate_calc(stats, params_split['file_size_mb'])
    
    # 4. Générer rapport
    print("\n Génération du rapport...\n")
    results = generate_report(stats, params_init, params_split, params_calc)
    
    # 5. Sauvegarder résultats pour plotting
    results_file = f"{RESULTS_DIR}/calibration_data.npz"
    np.savez(results_file,
             nodes=results['nodes'],
             t_exp=results['t_exp'],
             t_theo=results['t_theo'],
             error=results['error'],
             stats=stats.to_dict('list'),
             params_init=params_init,
             params_split=params_split,
             params_calc=params_calc)
    
    print(f" Données de calibration sauvegardées: {results_file}")

if __name__ == "__main__":
    main()
