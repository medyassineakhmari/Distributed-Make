import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "benchmark_results.csv"
OUTPUT_IMAGE = "analysis_speedup.png"

def plot_analysis():
    try:
        print(f"Lecture de {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE)

        df['Exec_s'] = (df['Total_Time_ms'] - df['Distrib_Exec_Start_ms']) / 1000
        
        df['Workers'] = df['Nodes'] - 1

        df_mean = df.groupby('Workers')['Exec_s'].mean().reset_index().sort_values('Workers')

        try:
            t_ref = df_mean[df_mean['Workers'] == 1]['Exec_s'].values[0]
        except IndexError:
            print("Attention : Pas de donnees pour 1 worker (2 noeuds). Le Speedup sera approximatif.")
            t_ref = df_mean['Exec_s'].max()

        df_mean['Speedup'] = t_ref / df_mean['Exec_s']
        
        df_mean['Ideal'] = df_mean['Workers']

        print("\nDONNEES CALCULEES :")
        print(df_mean[['Workers', 'Exec_s', 'Speedup']].to_string(index=False))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        ax1.plot(df_mean['Workers'], df_mean['Exec_s'], 'o-', color='#e74c3c', linewidth=2.5, label='Temps Calcul Reel')
        ax1.set_title("Temps de Calcul vs Nombre de Workers", fontsize=12, fontweight='bold')
        ax1.set_xlabel("Nombre de Workers", fontsize=10)
        ax1.set_ylabel("Temps (secondes)", fontsize=10)
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend()
        
        min_time = df_mean['Exec_s'].min()
        ax1.axhline(y=min_time, color='green', linestyle='--', alpha=0.5)
        ax1.text(df_mean['Workers'].max(), min_time, f" Min: {min_time:.2f}s", va='bottom', ha='right', color='green')

        ax2.plot(df_mean['Workers'], df_mean['Ideal'], '--', color='gray', label='Ideal (Lineaire)')
        ax2.plot(df_mean['Workers'], df_mean['Speedup'], 'o-', color='#2980b9', linewidth=2.5, label='Speedup Reel')
        
        ax2.set_title("Speedup (Acceleration)", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Nombre de Workers", fontsize=10)
        ax2.set_ylabel("Facteur d'acceleration (x)", fontsize=10)
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend()
        
        ax2.fill_between(df_mean['Workers'], df_mean['Speedup'], df_mean['Ideal'], color='gray', alpha=0.1)

        plt.suptitle("Analyse de Performance Distribuee (Hors I/O NFS)", fontsize=16)
        plt.tight_layout()
        plt.savefig(OUTPUT_IMAGE, dpi=300)
        print(f"\nGraphique genere : {OUTPUT_IMAGE}")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    plot_analysis()