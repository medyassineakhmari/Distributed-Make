import java.io.*;
import java.lang.management.*;
import java.rmi.registry.*;
import java.util.*;

public class Master_Baseline {
    
    // Tailles testées (avec les nouvelles valeurs intermédiaires)
    private static final int[] SIZES_KB = {
        1, 2, 5, 10, 20, 50, 100, 200, 500,
        1024,      // 1 MB
        // 2048,      // 2 MB
        3072,      // 3 MB
        5120,      // 5 MB
        8192 ,      // 8 MB
        10240,     // 10 MB
        20480,     // 20 MB
        30720,     // 30 MB
        40960,     // 40 MB
        51200,     // 50 MB
        61440,     // 60 MB
        71680,     // 70 MB
        81920,    // 80 MB
        92160,    // 90 MB
        102400,    // 100 MB
        307200,    // 300 MB
        512000,    // 500 MB
        1048576   // 1 GB
    };
    
    // Monitoring GC
    private static final List<GarbageCollectorMXBean> gcBeans = 
        ManagementFactory.getGarbageCollectorMXBeans();
    
    private static long getGCTime() {
        long totalTime = 0;
        for (GarbageCollectorMXBean gcBean : gcBeans) {
            totalTime += gcBean.getCollectionTime();
        }
        return totalTime;
    }
    
    private static long getGCCount() {
        long totalCount = 0;
        for (GarbageCollectorMXBean gcBean : gcBeans) {
            totalCount += gcBean.getCollectionCount();
        }
        return totalCount;
    }
    
    public static void main(String[] args) {
        try {
            // BASELINE: No RMI optimizations
            // (removing 4 JVM properties for baseline comparison)
            List<String> workers = getWorkerHosts();
            System.out.println("Testing " + workers.size() + " workers");
            
            List<DetailedMetric> results = new ArrayList<>();
            
            for (String host : workers) {
                System.out.println("\n=== Testing: " + host + " ===");
                Registry registry = LocateRegistry.getRegistry(host, 1099);
                PingPongService service = (PingPongService) registry.lookup("PingPong");
                System.out.println(service.hello());
                
                // Warmup Global
                System.out.println("Global Warming up...");
                for (int i = 0; i < 30; i++) service.ping(new byte[]{1});
                
                // --- TESTS ---
                for (int sizeKB : SIZES_KB) {
                    byte[] data = new byte[sizeKB * 1024];
                    
                    // 1. Stabilisation GC & Warmup Spécifique
                    System.gc();
                    try {
                        Thread.sleep(200);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    
                    for (int w = 0; w < 10; w++) service.ping(data); // Warmup JIT

                    long gcTimeBefore = getGCTime();
                    long gcCountBefore = getGCCount();
                    
                    // 30 mesures
                    double[] latencies = new double[30];
                    double[] throughputs = new double[30];
                    
                    for (int rep = 0; rep < 30; rep++) {
                        long start = System.nanoTime();
                        service.ping(data);
                        long end = System.nanoTime();
                        double rttMs = (end - start) / 1_000_000.0;   // en ms
                        latencies[rep] = rttMs;
                        
                        // Calcul Débit Effectif (Taille / RTT Total)
                        if (rttMs > 0) {
                            throughputs[rep] = (sizeKB / 1024.0) / (rttMs / 1000.0);
                        } else {
                            throughputs[rep] = 0;
                        }
                        
                        if (rep < 3) System.out.println("  [" + (rep+1) + "] latency: " + rttMs + " ms");
                    }
                    System.out.println("... (reps 4-30 omitted for clarity)");
                    
                    long gcTimeAfter = getGCTime();
                    
                    // --- CALCULS STATISTIQUES (IQR / MEDIANE) ---
                    Arrays.sort(latencies);
                    Arrays.sort(throughputs);
                    
                    // Indices pour 30 valeurs : Q1=7, Median=15, Q3=22
                    double p25Latency = latencies[7];
                    double medianLatency = latencies[15];
                    double p75Latency = latencies[22];
                    
                    double p25Throughput = throughputs[7];
                    double medianThroughput = throughputs[15];
                    double p75Throughput = throughputs[22];
                    
                    System.out.printf("  => Median Lat: %.3f ms | Median Thr: %.2f MB/s (IQR: %.2f - %.2f)\n", 
                        medianLatency, medianThroughput, p25Throughput, p75Throughput);
                    
                    results.add(new DetailedMetric(
                        host, sizeKB, 
                        p25Throughput, medianThroughput, p75Throughput,
                        p25Latency, medianLatency, p75Latency,
                        getGCCount() - gcCountBefore, gcTimeAfter - gcTimeBefore
                    ));
                }
            }
            saveResults(results, "pingpong-normal.csv");
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private static class DetailedMetric {
        String host; int sizeKB;
        double p25Thr, medianThr, p75Thr;
        double p25Lat, medianLat, p75Lat;
        long gcCount, gcTimeMs;
        
        public DetailedMetric(String h, int s, double p25T, double medT, double p75T, double p25L, double medL, double p75L, long gcC, long gcTm) {
            this.host = h; this.sizeKB = s;
            this.p25Thr = p25T; this.medianThr = medT; this.p75Thr = p75T;
            this.p25Lat = p25L; this.medianLat = medL; this.p75Lat = p75L;
            this.gcCount = gcC; this.gcTimeMs = gcTm;
        }
    }
    
    private static void saveResults(List<DetailedMetric> results, String filename) throws Exception {
        try (PrintWriter writer = new PrintWriter(filename)) {
            // NOUVEL EN-TÊTE CSV
            writer.println("host,size_kb,p25_throughput_mbps,median_throughput_mbps,p75_throughput_mbps," +
                          "p25_latency_ms,median_latency_ms,p75_latency_ms,gc_count,gc_time_ms");
            
            for (DetailedMetric m : results) {
                writer.printf(Locale.US, "%s,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%d,%d\n",
                    m.host, m.sizeKB, 
                    m.p25Thr, m.medianThr, m.p75Thr,
                    m.p25Lat, m.medianLat, m.p75Lat,
                    m.gcCount, m.gcTimeMs);
            }
            System.out.println("\n[OK] Results saved: " + filename);
        }
    }

    private static List<String> getWorkerHosts() throws Exception {
        String nodeFile = System.getenv("OAR_NODE_FILE");
        if (nodeFile == null) return Arrays.asList("localhost");
        String masterHost = java.net.InetAddress.getLocalHost().getHostName();
        Set<String> hosts = new HashSet<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(nodeFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String host = line.trim();
                if (!host.equals(masterHost)) hosts.add(host);
            }
        }
        return new ArrayList<>(hosts);
    }
}