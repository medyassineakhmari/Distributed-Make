#!/usr/bin/env python3
"""
Visualization: RDMA vs TCP/IP vs gRPC performance comparison
"""

import sys

# Data: [RMI_Opt, gRPC, MPI, RDMA]
sizes_kb = [1, 10, 100, 1024, 10240]
rtt_ms = {
    1: [0.35, 0.15, 0.05, 0.001],
    10: [0.36, 0.20, 0.08, 0.002],
    100: [0.42, 0.35, 0.15, 0.005],
    1024: [1.20, 0.80, 0.40, 0.020],
    10240: [14.5, 8.0, 4.0, 0.100],
}

throughput_mbps = {
    1: [100, 300, 800, 8000],
    10: [150, 500, 1500, 8500],
    100: [400, 1000, 2500, 9000],
    1024: [750, 1500, 3000, 10000],
    10240: [900, 1600, 4000, 11000],
}

solutions = ["RMI-Opt", "gRPC", "MPI", "RDMA"]
colors = ["📉", "📊", "📈", "🚀"]

print("=" * 100)
print("RDMA vs AUTRES SOLUTIONS - COMPARAISON COMPLÈTE")
print("=" * 100)

print("\n📊 LATENCE (RTT en millisecondes)\n")
print(f"{'Message Size':<15}", end="")
for sol in solutions:
    print(f"{sol:<15}", end="")
print()
print("-" * 100)

for size in sizes_kb:
    print(f"{size:>6} KB       ", end="")
    for i, sol in enumerate(solutions):
        rtt = rtt_ms[size][i]
        if rtt < 0.01:
            print(f"{rtt*1000:>6.2f} µs     ", end="")
        else:
            print(f"{rtt:>6.3f} ms     ", end="")
    print()

print("\n" + "=" * 100)
print("📈 DÉBIT (Throughput en MB/s)\n")
print(f"{'Message Size':<15}", end="")
for sol in solutions:
    print(f"{sol:<15}", end="")
print()
print("-" * 100)

for size in sizes_kb:
    print(f"{size:>6} KB       ", end="")
    for i, sol in enumerate(solutions):
        thr = throughput_mbps[size][i]
        if thr > 1000:
            print(f"{thr/1000:>5.1f} GB/s   ", end="")
        else:
            print(f"{thr:>6.0f} MB/s   ", end="")
    print()

print("\n" + "=" * 100)
print("🎯 SPEEDUP vs BASELINE (RMI Optimisé = 1x)\n")

print(f"{'Message Size':<15}", end="")
for sol in solutions[1:]:
    print(f"{sol:<15}", end="")
print()
print("-" * 100)

for size in sizes_kb:
    baseline_thr = throughput_mbps[size][0]
    print(f"{size:>6} KB       ", end="")
    for i in range(1, len(solutions)):
        speedup = throughput_mbps[size][i] / baseline_thr
        print(f"{speedup:>6.1f}x       ", end="")
    print()

print("\n" + "=" * 100)
print("💾 IMPACT: Temps de transfert de fichiers\n")

file_sizes = [10, 100, 1000]  # MB
solutions_names = ["RMI-Opt", "gRPC", "MPI", "RDMA"]
baseline_thr = 900  # MB/s for RMI optimized

print(f"{'File Size':<15}", end="")
for sol in solutions_names:
    print(f"{sol:<15}", end="")
print()
print("-" * 100)

for file_size in file_sizes:
    print(f"{file_size:>6} MB       ", end="")
    
    # RMI Optimized
    time_sec = file_size / baseline_thr
    print(f"{time_sec:>6.2f} sec    ", end="")
    
    # gRPC (1.6x speedup)
    time_sec = file_size / (baseline_thr * 1.6)
    print(f"{time_sec:>6.2f} sec    ", end="")
    
    # MPI (4x speedup)
    time_sec = file_size / (baseline_thr * 4)
    print(f"{time_sec:>6.2f} sec    ", end="")
    
    # RDMA (12x speedup)
    time_sec = file_size / (baseline_thr * 12)
    print(f"{time_sec:>6.2f} sec    ", end="")
    
    print()

print("\n" + "=" * 100)
print("🔬 ANALYSE DÉTAILLÉE : 10 MB Transfer\n")

transfer_size = 10  # MB
scenarios = [
    ("RMI Optimized", 900, 0.01, "Java RMI + TCP/IP"),
    ("gRPC", 1600, 0.002, "Protocol Buffers + HTTP/2"),
    ("MPI", 4000, 0.001, "Direct Network + OpenMPI"),
    ("RDMA Direct", 11000, 0.0001, "Zero-copy + HW offload"),
]

print(f"{'Solution':<20} {'Débit':<15} {'Temps 10MB':<15} {'Technologie':<30}")
print("-" * 100)

for name, thr, overhead, tech in scenarios:
    time_ms = (transfer_size / thr) * 1000 + (overhead * 1000)
    print(f"{name:<20} {thr:>6} MB/s    {time_ms:>6.2f} ms        {tech:<30}")

print("\n" + "=" * 100)
print("✅ VERDICT\n")

print("""
┌──────────────────────────────────────────────────────────────────┐
│ RÉSULTATS ESTIMÉS AVEC RDMA DIRECT                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ✅ Débit maximal:        11000 MB/s (11 GB/s)                   │
│    vs RMI-Opt:          900 MB/s                                │
│    GAIN:                12x plus rapide 🚀                       │
│                                                                  │
│ ✅ Latence minimale:     0.001 ms (1 microseconde)             │
│    vs RMI-Opt:          0.35 ms (350 microsecondes)            │
│    GAIN:                350x plus rapide 🚀                      │
│                                                                  │
│ ✅ Utilisation du réseau: 88% du potentiel 12.5 GB/s           │
│    vs RMI-Opt:          7.2% du potentiel                       │
│    GAIN:                12x meilleure utilisation                │
│                                                                  │
│ ✅ Copie de données:     0 copies (zero-copy)                  │
│    vs RMI-Opt:          5 copies (heap, kernel, NIC)           │
│    GAIN:                Zéro overhead 🎉                         │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ COÛT D'IMPLÉMENTATION:   4-6 heures + Complexité élevée         │
│ LANGAGE REQUIS:         Java (JNI) + C/C++ + RDMA verbs        │
│ DRIVERS REQUIS:         OFED + InfiniBand/Omni-Path             │
└──────────────────────────────────────────────────────────────────┘
""")

print("=" * 100)
print("RECOMMANDATION FINALE\n")
print("""
Si tu veux la MEILLEURE performance possible:
→ RDMA Direct est le choix optimal (10-12x speedup)

Si tu veux un compromis temps/complexité:
→ gRPC (3-4 heures, +2x speedup)

Si tu veux juste amélioration rapide:
→ RMI Optimisé (30 min, +0.2x speedup)
""")

print("=" * 100)
