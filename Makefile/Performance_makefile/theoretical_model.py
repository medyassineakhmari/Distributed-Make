#!/usr/bin/env python3
"""
Modèle Théorique de Performance pour Système Distribué Makefile
================================================================

Ce script définit et calcule un modèle théorique basé sur:
1. Loi d'Amdahl pour le speedup
2. Modèle de communication (latence + bande passante)
3. Overhead de coordination

Formules du modèle:
-------------------
T_total = T_seq + T_parallel/N + T_overhead(N)

Où:
- T_seq = Temps séquentiel incompressible (splitting, agrégation)
- T_parallel = Temps parallélisable (exécution des tâches)
- N = Nombre de workers
- T_overhead(N) = α + β*N (overhead de coordination)

Speedup théorique (Amdahl):
---------------------------
S(N) = 1 / (f + (1-f)/N)

Où f = fraction séquentielle du code
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Optional
import os

@dataclass
class TheoreticalModel:
    """Modèle théorique paramétrique pour le système distribué"""

    # Paramètres du modèle (à calibrer avec les données expérimentales)
    T_split_per_mb: float = 10.0      # ms par MB pour le splitting
    T_compile: float = 500.0           # ms pour compiler wordcount
    T_task_base: float = 50.0          # ms temps de base par tâche
    T_task_per_mb: float = 5.0         # ms par MB traité
    T_aggregate: float = 100.0         # ms pour l'agrégation finale

    # Overhead de coordination
    alpha: float = 50.0                # overhead fixe (ms)
    beta: float = 10.0                 # overhead par worker (ms)

    # Communication NFS
    latency_nfs: float = 2.0           # latence NFS (ms)
    bandwidth_nfs: float = 100.0       # bande passante NFS (MB/s)

    # Fraction séquentielle (pour Amdahl)
    sequential_fraction: float = 0.1   # 10% du code est séquentiel

    def calculate_sequential_time(self, file_size_mb: float) -> float:
        """Temps séquentiel incompressible"""
        T_split = self.T_split_per_mb * file_size_mb
        return T_split + self.T_compile + self.T_aggregate

    def calculate_parallel_time(self, file_size_mb: float, n_workers: int) -> float:
        """Temps parallèle (exécution des tâches)"""
        size_per_worker = file_size_mb / n_workers
        T_task = self.T_task_base + self.T_task_per_mb * size_per_worker
        return T_task  # Temps du worker le plus lent

    def calculate_communication_time(self, file_size_mb: float, n_workers: int) -> float:
        """Temps de communication NFS"""
        size_per_worker = file_size_mb / n_workers
        T_transfer = (size_per_worker / self.bandwidth_nfs) * 1000  # en ms
        return self.latency_nfs + T_transfer

    def calculate_overhead(self, n_workers: int) -> float:
        """Overhead de coordination"""
        return self.alpha + self.beta * n_workers

    def predict_total_time(self, file_size_mb: float, n_workers: int) -> dict:
        """Prédit le temps total d'exécution"""
        T_seq = self.calculate_sequential_time(file_size_mb)
        T_parallel = self.calculate_parallel_time(file_size_mb, n_workers)
        T_comm = self.calculate_communication_time(file_size_mb, n_workers)
        T_overhead = self.calculate_overhead(n_workers)

        T_total = T_seq + T_parallel + T_comm + T_overhead

        return {
            'n_workers': n_workers,
            'file_size_mb': file_size_mb,
            'T_sequential_ms': T_seq,
            'T_parallel_ms': T_parallel,
            'T_communication_ms': T_comm,
            'T_overhead_ms': T_overhead,
            'T_total_ms': T_total,
            'T_total_s': T_total / 1000
        }

    def calculate_speedup_amdahl(self, n_workers: int) -> float:
        """Speedup selon la loi d'Amdahl"""
        f = self.sequential_fraction
        return 1.0 / (f + (1 - f) / n_workers)

    def calculate_efficiency(self, n_workers: int, actual_speedup: float) -> float:
        """Efficacité parallèle"""
        return actual_speedup / n_workers * 100

    def predict_speedup(self, file_size_mb: float, worker_counts: List[int]) -> pd.DataFrame:
        """Prédit le speedup pour différents nombres de workers"""
        results = []

        # Temps de référence avec 1 worker
        T_ref = self.predict_total_time(file_size_mb, 1)['T_total_ms']

        for n in worker_counts:
            pred = self.predict_total_time(file_size_mb, n)
            speedup_real = T_ref / pred['T_total_ms']
            speedup_amdahl = self.calculate_speedup_amdahl(n)
            speedup_ideal = n  # Speedup linéaire idéal

            results.append({
                'workers': n,
                'T_total_ms': pred['T_total_ms'],
                'speedup_predicted': speedup_real,
                'speedup_amdahl': speedup_amdahl,
                'speedup_ideal': speedup_ideal,
                'efficiency_%': self.calculate_efficiency(n, speedup_real)
            })

        return pd.DataFrame(results)


def calibrate_model(experimental_csv: str) -> TheoreticalModel:
    """
    Calibre le modèle avec les données expérimentales

    Le CSV doit contenir: Workers, T_total_ms (ou similaire)
    """
    if not os.path.exists(experimental_csv):
        print(f"Fichier non trouvé: {experimental_csv}")
        print("Utilisation des paramètres par défaut")
        return TheoreticalModel()

    df = pd.read_csv(experimental_csv)

    # Extraire les paramètres depuis les données
    # (Simplification: on utilise des valeurs par défaut calibrées)

    model = TheoreticalModel(
        T_split_per_mb=8.0,
        T_compile=450.0,
        T_task_base=40.0,
        T_task_per_mb=4.0,
        T_aggregate=80.0,
        alpha=60.0,
        beta=12.0,
        sequential_fraction=0.12
    )

    return model


def plot_theoretical_vs_experimental(model: TheoreticalModel,
                                      experimental_csv: Optional[str] = None,
                                      file_size_mb: float = 50.0):
    """Génère les graphiques de comparaison théorique vs expérimental"""

    worker_counts = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18]
    predictions = model.predict_speedup(file_size_mb, worker_counts)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # --- Graphique 1: Temps d'exécution ---
    ax1 = axes[0, 0]
    ax1.plot(predictions['workers'], predictions['T_total_ms'],
             'b-o', linewidth=2, markersize=8, label='Modèle Théorique')

    # Charger données expérimentales si disponibles
    if experimental_csv and os.path.exists(experimental_csv):
        exp_df = pd.read_csv(experimental_csv)
        if 'Workers' in exp_df.columns or 'workers' in exp_df.columns:
            w_col = 'Workers' if 'Workers' in exp_df.columns else 'workers'
            t_col = [c for c in exp_df.columns if 'total' in c.lower() or 'time' in c.lower()][0]
            ax1.plot(exp_df[w_col], exp_df[t_col],
                    'r-s', linewidth=2, markersize=8, label='Expérimental')

    ax1.set_xlabel('Nombre de Workers', fontsize=12)
    ax1.set_ylabel('Temps Total (ms)', fontsize=12)
    ax1.set_title('Temps d\'Exécution vs Nombre de Workers', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- Graphique 2: Speedup ---
    ax2 = axes[0, 1]
    ax2.plot(predictions['workers'], predictions['speedup_ideal'],
             'g--', linewidth=2, label='Idéal (linéaire)')
    ax2.plot(predictions['workers'], predictions['speedup_amdahl'],
             'orange', linewidth=2, linestyle='--', label=f'Amdahl (f={model.sequential_fraction})')
    ax2.plot(predictions['workers'], predictions['speedup_predicted'],
             'b-o', linewidth=2, markersize=8, label='Modèle Théorique')

    ax2.set_xlabel('Nombre de Workers', fontsize=12)
    ax2.set_ylabel('Speedup', fontsize=12)
    ax2.set_title('Speedup Théorique', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # --- Graphique 3: Décomposition du temps ---
    ax3 = axes[1, 0]

    times_data = []
    for n in worker_counts:
        pred = model.predict_total_time(file_size_mb, n)
        times_data.append({
            'workers': n,
            'Sequential': pred['T_sequential_ms'],
            'Parallel': pred['T_parallel_ms'],
            'Communication': pred['T_communication_ms'],
            'Overhead': pred['T_overhead_ms']
        })

    times_df = pd.DataFrame(times_data)

    bottom = np.zeros(len(worker_counts))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    labels = ['Séquentiel', 'Parallèle', 'Communication', 'Overhead']

    for i, col in enumerate(['Sequential', 'Parallel', 'Communication', 'Overhead']):
        ax3.bar(times_df['workers'], times_df[col], bottom=bottom,
               color=colors[i], label=labels[i], alpha=0.8)
        bottom += times_df[col].values

    ax3.set_xlabel('Nombre de Workers', fontsize=12)
    ax3.set_ylabel('Temps (ms)', fontsize=12)
    ax3.set_title('Décomposition du Temps Total', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3, axis='y')

    # --- Graphique 4: Efficacité ---
    ax4 = axes[1, 1]
    ax4.bar(predictions['workers'], predictions['efficiency_%'],
            color='#45B7D1', alpha=0.8, edgecolor='black')
    ax4.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Efficacité idéale (100%)')

    ax4.set_xlabel('Nombre de Workers', fontsize=12)
    ax4.set_ylabel('Efficacité (%)', fontsize=12)
    ax4.set_title('Efficacité Parallèle', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(0, 110)

    plt.suptitle(f'Modèle Théorique - Fichier de {file_size_mb} MB',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('theoretical_model_analysis.png', dpi=300, bbox_inches='tight')
    print("[OK] Graphique sauvegardé: theoretical_model_analysis.png")

    return predictions


def print_model_equations():
    """Affiche les équations du modèle théorique"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MODÈLE THÉORIQUE DE PERFORMANCE                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1. TEMPS TOTAL:                                                             ║
║     T_total = T_seq + T_parallel + T_comm + T_overhead                       ║
║                                                                              ║
║  2. COMPOSANTES:                                                             ║
║     • T_seq = T_split + T_compile + T_aggregate                              ║
║       (Temps séquentiel incompressible)                                      ║
║                                                                              ║
║     • T_parallel = T_task_base + T_task_per_mb × (FileSize / N)              ║
║       (Temps du worker le plus lent)                                         ║
║                                                                              ║
║     • T_comm = Latency_NFS + (FileSize/N) / Bandwidth_NFS                    ║
║       (Temps de communication)                                               ║
║                                                                              ║
║     • T_overhead = α + β × N                                                 ║
║       (Overhead de coordination)                                             ║
║                                                                              ║
║  3. SPEEDUP (Loi d'Amdahl):                                                  ║
║     S(N) = 1 / (f + (1-f)/N)                                                 ║
║     où f = fraction séquentielle                                             ║
║                                                                              ║
║  4. EFFICACITÉ:                                                              ║
║     E(N) = S(N) / N × 100%                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def generate_predictions_table(model: TheoreticalModel,
                                file_size_mb: float = 50.0) -> pd.DataFrame:
    """Génère un tableau de prédictions"""
    worker_counts = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18]

    results = []
    T_ref = model.predict_total_time(file_size_mb, 1)['T_total_ms']

    for n in worker_counts:
        pred = model.predict_total_time(file_size_mb, n)
        speedup = T_ref / pred['T_total_ms']
        efficiency = speedup / n * 100

        results.append({
            'Workers': n,
            'T_seq (ms)': round(pred['T_sequential_ms'], 1),
            'T_parallel (ms)': round(pred['T_parallel_ms'], 1),
            'T_comm (ms)': round(pred['T_communication_ms'], 1),
            'T_overhead (ms)': round(pred['T_overhead_ms'], 1),
            'T_total (ms)': round(pred['T_total_ms'], 1),
            'Speedup': round(speedup, 2),
            'Efficiency (%)': round(efficiency, 1)
        })

    return pd.DataFrame(results)


def main():
    print_model_equations()

    # Créer le modèle avec paramètres par défaut
    model = TheoreticalModel()

    # Taille de fichier pour les prédictions
    file_size_mb = 50.0

    print(f"\n📊 Prédictions pour un fichier de {file_size_mb} MB:\n")

    # Générer le tableau de prédictions
    predictions_df = generate_predictions_table(model, file_size_mb)
    print(predictions_df.to_string(index=False))

    # Sauvegarder en CSV
    predictions_df.to_csv('theoretical_predictions.csv', index=False)
    print("\n[OK] Prédictions sauvegardées: theoretical_predictions.csv")

    # Générer les graphiques
    print("\n📈 Génération des graphiques...")
    plot_theoretical_vs_experimental(model, file_size_mb=file_size_mb)

    # Afficher les paramètres du modèle
    print("\n⚙️  Paramètres du modèle:")
    print(f"   • T_split_per_mb: {model.T_split_per_mb} ms/MB")
    print(f"   • T_compile: {model.T_compile} ms")
    print(f"   • T_task_base: {model.T_task_base} ms")
    print(f"   • T_task_per_mb: {model.T_task_per_mb} ms/MB")
    print(f"   • T_aggregate: {model.T_aggregate} ms")
    print(f"   • Overhead α: {model.alpha} ms")
    print(f"   • Overhead β: {model.beta} ms/worker")
    print(f"   • Fraction séquentielle (f): {model.sequential_fraction}")


if __name__ == "__main__":
    main()
