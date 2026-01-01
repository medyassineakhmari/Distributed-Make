import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "benchmark_results.csv"
OUTPUT_IMAGE = "resultats_huge_nova.png"

def plot_graph():
    try:
        print(f"Lecture de {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE)

        df['Exec_s'] = (df['Total_Time_ms'] - df['Distrib_Exec_Start_ms']) / 1000
        df['Split_s'] = df['Split_Time_ms'] / 1000
        df['Total_s'] = df['Total_Time_ms'] / 1000

        df_mean = df.groupby('Nodes').mean().reset_index().sort_values('Nodes')

        print("\nMOYENNES (Cluster Nova - 1.5 Go) :")
        print(df_mean[['Nodes', 'Total_s', 'Split_s', 'Exec_s']].to_string(index=False))

        plt.figure(figsize=(10, 6))
        
        plt.plot(df_mean['Nodes'], df_mean['Total_s'], 'o-', linewidth=3, color='#2c3e50', label='Temps Total')
        plt.plot(df_mean['Nodes'], df_mean['Split_s'], 's--', linewidth=2, color='#c0392b', label='Temps Split (I/O Sequentiel)')
        plt.plot(df_mean['Nodes'], df_mean['Exec_s'], '^-.', linewidth=2, color='#27ae60', label='Temps Calcul (Distribue)')

        plt.fill_between(df_mean['Nodes'], df_mean['Split_s'], df_mean['Total_s'], color='#2ecc71', alpha=0.1, label='Gain du parallelisme')

        plt.title("Performance WordCount (Fichier 1.5 Go) - Cluster Nova", fontsize=14, fontweight='bold')
        plt.xlabel("Nombre de Workers", fontsize=12)
        plt.ylabel("Temps (secondes)", fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.xticks(df_mean['Nodes'])
        plt.ylim(0, max(df_mean['Total_s']) * 1.1)

        plt.tight_layout()
        plt.savefig(OUTPUT_IMAGE, dpi=300)
        print(f"\nGraphique genere : {OUTPUT_IMAGE}")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    plot_graph()