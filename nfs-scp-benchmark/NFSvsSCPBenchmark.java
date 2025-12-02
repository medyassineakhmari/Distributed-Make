import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

public class NFSvsSCPBenchmark {
    
    private static final int[] SIZES = {1, 10, 50, 100, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576};
    private static List<Metric> nfsMetrics = new ArrayList<>();
    private static List<Metric> scpMetrics = new ArrayList<>();
    private static Map<String, Double> baselineRTT = new HashMap<>();

    public static void main(String[] args) {
        try {
            System.out.println("=== NFS vs SCP Performance Benchmark ===\n");
            
            // 1. Récupérer les nœuds workers
            List<String> workers = getWorkerHosts();
            System.out.println("Workers trouvés: " + workers);
            System.out.println("Nombre de workers: " + workers.size() + "\n");

            // 2. Créer les fichiers de test pour NFS
            System.out.println("Création des fichiers de test NFS...");
            String nfsDir = System.getProperty("user.dir") + "/nfs_test/";
            new File(nfsDir).mkdirs();
            for (int size : SIZES) {
                createTestFile(nfsDir + "test_" + size + ".txt", size);
            }
            System.out.println("Fichiers NFS créés.\n");

            // 3. Créer les fichiers de test pour SCP
            System.out.println("Création des fichiers de test SCP...");
            String scpDir = "/tmp/scp_test/";
            new File(scpDir).mkdirs();
            for (int size : SIZES) {
                createTestFile(scpDir + "test_" + size + ".txt", size);
            }
            System.out.println("Fichiers SCP créés.\n");

            // 4. Mesurer la latence de base avec chaque worker
            System.out.println("Mesure de la latence de base (baseline RTT)...");
            for (String worker : workers) {
                double rtt = measureBaselineRTT(worker);
                baselineRTT.put(worker, rtt);
                System.out.printf("Worker %s: Baseline RTT = %.2f ms%n", worker, rtt);
            }
            System.out.println();

            // 5. Benchmark NFS
            System.out.println("=== Benchmark NFS ===");
            for (String worker : workers) {
                System.out.println("Testing worker: " + worker);
                for (int size : SIZES) {
                    String filePath = nfsDir + "test_" + size + ".txt";
                    double rtt = benchmarkNFS(worker, filePath);
                    double throughput = (size / 1024.0) / (rtt / 1000.0); // MB/s
                    nfsMetrics.add(new Metric(worker, size, rtt, throughput));
                    System.out.printf("  Size: %d KB, RTT: %.2f ms, Throughput: %.2f MB/s%n", 
                                      size, rtt, throughput);
                }
                System.out.println();
            }

            // 6. Benchmark SCP
            System.out.println("=== Benchmark SCP ===");
            for (String worker : workers) {
                System.out.println("Testing worker: " + worker);
                for (int size : SIZES) {
                    String localPath = scpDir + "test_" + size + ".txt";
                    String remotePath = "/tmp/test_" + size + ".txt";
                    double rtt = benchmarkSCP(worker, localPath, remotePath);
                    double throughput = (size / 1024.0) / (rtt / 1000.0);
                    scpMetrics.add(new Metric(worker, size, rtt, throughput));
                    System.out.printf("  Size: %d KB, RTT: %.2f ms, Throughput: %.2f MB/s%n", 
                                      size, rtt, throughput);
                }
                System.out.println();
            }

            // 7. Écrire les résultats
            writeResults();
            
            // 8. Générer le script Python pour les graphiques
            generatePlotScript();
            
            System.out.println("\n=== Benchmark terminé ===");
            System.out.println("Résultats sauvegardés dans nfs-results.txt et scp-results.txt");
            System.out.println("Pour générer les graphiques, exécutez: python3 plot_results.py");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static List<String> getWorkerHosts() throws IOException, InterruptedException {
        List<String> workers = new ArrayList<>();
        String nodeFile = System.getenv("OAR_NODE_FILE");
        
        if (nodeFile == null || nodeFile.isEmpty()) {
            System.out.println("ATTENTION: OAR_NODE_FILE non défini. Mode test local.");
            return Arrays.asList("localhost");
        }

        String masterHost = executeCommand("hostname").trim();
        
        List<String> allHosts = Files.readAllLines(Paths.get(nodeFile));
        for (String host : allHosts) {
            host = host.trim();
            if (!host.equals(masterHost) && !host.isEmpty()) {
                workers.add(host);
            }
        }
        
        return workers.stream().distinct().collect(Collectors.toList());
    }

    private static void createTestFile(String filePath, int sizeKB) throws IOException {
        byte[] data = new byte[sizeKB * 1024];
        Arrays.fill(data, (byte) 'a');
        Files.write(Paths.get(filePath), data);
    }

    private static double measureBaselineRTT(String worker) {
        try {
            long start = System.nanoTime();
            executeCommand("ssh " + worker + " echo 'test'");
            long end = System.nanoTime();
            return (end - start) / 1_000_000.0;
        } catch (Exception e) {
            System.err.println("Erreur lors de la mesure RTT baseline pour " + worker);
            return 0.0;
        }
    }

    private static double benchmarkNFS(String worker, String filePath) {
        try {
            long start = System.nanoTime();
            String command = String.format("ssh %s cat %s > /dev/null", worker, filePath);
            executeCommand(command);
            long end = System.nanoTime();
            return (end - start) / 1_000_000.0;
        } catch (Exception e) {
            System.err.println("Erreur NFS benchmark: " + e.getMessage());
            return 0.0;
        }
    }

    private static double benchmarkSCP(String worker, String localPath, String remotePath) {
        try {
            long start = System.nanoTime();
            String command = String.format("scp %s %s:%s", localPath, worker, remotePath);
            executeCommand(command);
            executeCommand(String.format("ssh %s cat %s > /dev/null", worker, remotePath));
            long end = System.nanoTime();
            return (end - start) / 1_000_000.0;
        } catch (Exception e) {
            System.err.println("Erreur SCP benchmark: " + e.getMessage());
            return 0.0;
        }
    }

    private static String executeCommand(String command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder("bash", "-c", command);
        pb.redirectErrorStream(true);
        Process process = pb.start();
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
        }
        
        process.waitFor();
        return output.toString();
    }

    private static void writeResults() throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter("nfs-results.txt"))) {
            writer.println("=== NFS Performance Results ===\n");
            for (Metric m : nfsMetrics) {
                writer.println(m);
            }
            
            writer.println("\n=== Average by Size ===");
            Map<Integer, List<Metric>> grouped = nfsMetrics.stream()
                .collect(Collectors.groupingBy(Metric::getDataSize));
            
            for (int size : SIZES) {
                List<Metric> group = grouped.get(size);
                if (group != null && !group.isEmpty()) {
                    double avgRTT = group.stream().mapToDouble(Metric::getRtt).average().orElse(0);
                    double avgThroughput = group.stream().mapToDouble(Metric::getThroughput).average().orElse(0);
                    writer.printf("Size: %d KB, Avg RTT: %.2f ms, Avg Throughput: %.2f MB/s%n",
                                  size, avgRTT, avgThroughput);
                }
            }
        }

        try (PrintWriter writer = new PrintWriter(new FileWriter("scp-results.txt"))) {
            writer.println("=== SCP Performance Results ===\n");
            for (Metric m : scpMetrics) {
                writer.println(m);
            }
            
            writer.println("\n=== Average by Size ===");
            Map<Integer, List<Metric>> grouped = scpMetrics.stream()
                .collect(Collectors.groupingBy(Metric::getDataSize));
            
            for (int size : SIZES) {
                List<Metric> group = grouped.get(size);
                if (group != null && !group.isEmpty()) {
                    double avgRTT = group.stream().mapToDouble(Metric::getRtt).average().orElse(0);
                    double avgThroughput = group.stream().mapToDouble(Metric::getThroughput).average().orElse(0);
                    writer.printf("Size: %d KB, Avg RTT: %.2f ms, Avg Throughput: %.2f MB/s%n",
                                  size, avgRTT, avgThroughput);
                }
            }
        }

        try (PrintWriter writer = new PrintWriter(new FileWriter("results.csv"))) {
            writer.println("Type,Size_KB,RTT_ms,Throughput_MBps");
            for (Metric m : nfsMetrics) {
                writer.printf("NFS,%d,%.2f,%.2f%n", m.getDataSize(), m.getRtt(), m.getThroughput());
            }
            for (Metric m : scpMetrics) {
                writer.printf("SCP,%d,%.2f,%.2f%n", m.getDataSize(), m.getRtt(), m.getThroughput());
            }
        }
    }

    private static void generatePlotScript() throws IOException {
        String script = """
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('results.csv')

nfs_data = df[df['Type'] == 'NFS'].groupby('Size_KB').agg({
    'RTT_ms': 'mean',
    'Throughput_MBps': 'mean'
}).reset_index()

scp_data = df[df['Type'] == 'SCP'].groupby('Size_KB').agg({
    'RTT_ms': 'mean',
    'Throughput_MBps': 'mean'
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

ax1.plot(nfs_data['Size_KB'], nfs_data['RTT_ms'], 'o-', label='NFS', linewidth=2, markersize=8)
ax1.plot(scp_data['Size_KB'], scp_data['RTT_ms'], 's-', label='SCP', linewidth=2, markersize=8)
ax1.set_xscale('log')
ax1.set_xlabel('Taille du fichier (KB)', fontsize=12)
ax1.set_ylabel('RTT (ms)', fontsize=12)
ax1.set_title('Temps de réponse (RTT)', fontsize=14, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

ax2.plot(nfs_data['Size_KB'], nfs_data['Throughput_MBps'], 'o-', label='NFS', linewidth=2, markersize=8)
ax2.plot(scp_data['Size_KB'], scp_data['Throughput_MBps'], 's-', label='SCP', linewidth=2, markersize=8)
ax2.set_xscale('log')
ax2.set_xlabel('Taille du fichier (KB)', fontsize=12)
ax2.set_ylabel('Débit (MB/s)', fontsize=12)
ax2.set_title('Débit de transfert', fontsize=14, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('nfs_vs_scp_comparison.png', dpi=300, bbox_inches='tight')
print("Graphique sauvegardé: nfs_vs_scp_comparison.png")
plt.show()
""";

        Files.writeString(Paths.get("plot_results.py"), script);
    }
}