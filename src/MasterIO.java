import java.rmi.registry.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.lang.management.*;

public class MasterIO {
    
    // Mêmes tailles que Master.java
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
    
    private static final String TEMP_DIR = "/tmp/pingpong-test/";
    
    private static final List<GarbageCollectorMXBean> gcBeans = ManagementFactory.getGarbageCollectorMXBeans();
    private static long getGCTime() {
        long total = 0; for(GarbageCollectorMXBean b : gcBeans) total += b.getCollectionTime(); return total;
    }
    private static long getGCCount() {
        long total = 0; for(GarbageCollectorMXBean b : gcBeans) total += b.getCollectionCount(); return total;
    }
    
    public static void main(String[] args) {
        try {
            Files.createDirectories(Paths.get(TEMP_DIR));
            List<String> workers = getWorkerHosts();
            System.out.println("Testing " + workers.size() + " workers (WITH I/O)");
            
            List<DetailedMetric> results = new ArrayList<>();
            
            for (String host : workers) {
                System.out.println("\n=== Testing: " + host + " (I/O) ===");
                Registry registry = LocateRegistry.getRegistry(host, 1099);
                PingPongService service = (PingPongService) registry.lookup("PingPong");
                System.out.println(service.hello());
                
                // Warmup
                System.out.println("Global Warming up...");
                for (int i = 0; i < 5; i++) service.ping(new byte[]{1});

                // Préparation fichiers distants
                System.out.println("Creating test files...");
                for (int sizeKB : SIZES_KB) {
                    service.createTestFile(TEMP_DIR + "test_" + sizeKB + "KB.txt", sizeKB);
                }

                // --- TESTS ---
                for (int sizeKB : SIZES_KB) {
                    System.out.printf("\n--- Testing size: %d KB (%.2f MB) with I/O ---\n", sizeKB, sizeKB/1024.0);
                    
                    String localPath = TEMP_DIR + "local_" + sizeKB + "KB.txt";
                    String remotePath = TEMP_DIR + "test_" + sizeKB + "KB.txt";
                    
                    byte[] data = new byte[sizeKB * 1024];
                    Arrays.fill(data, (byte) 'a');
                    Files.write(Paths.get(localPath), data);
                    
                    long gcTimeBefore = getGCTime();
                    long gcCountBefore = getGCCount();
                    
                    double[] latencies = new double[30];
                    double[] throughputs = new double[30];
                    
                    for (int rep = 0; rep < 30; rep++) {
                        long start = System.nanoTime();
                        
                        byte[] fileData = Files.readAllBytes(Paths.get(localPath));
                        service.pingWithIO(remotePath);
                        Files.write(Paths.get(TEMP_DIR + "received_" + sizeKB + "KB.txt"), fileData);
                        
                        long end = System.nanoTime();
                        double rttMs = (end - start) / 1_000_000.0;
                        latencies[rep] = rttMs;
                        
                        if (rttMs > 0) throughputs[rep] = (sizeKB / 1024.0) / (rttMs / 1000.0);
                        else throughputs[rep] = 0;
                        
                        System.out.printf("  [%2d] Lat: %8.3f ms | Thr: %10.4f MB/s\n", rep+1, rttMs, throughputs[rep]);
                    }
                    
                    long gcTimeAfter = getGCTime();
                    
                    // STATS
                    Arrays.sort(latencies);
                    Arrays.sort(throughputs);
                    
                    results.add(new DetailedMetric(
                        host, sizeKB, 
                        throughputs[7], throughputs[15], throughputs[22], // Q1, Med, Q3
                        latencies[7], latencies[15], latencies[22],       // Q1, Med, Q3
                        getGCCount() - gcCountBefore, gcTimeAfter - gcTimeBefore
                    ));
                }
            }
            saveResults(results, "pingpong-io.csv");
            
        } catch (Exception e) { e.printStackTrace(); }
    }
    
    // Mêmes classes internes DetailedMetric et saveResults que Master.java ...
    private static class DetailedMetric {
        String host; int sizeKB;
        double p25Thr, medianThr, p75Thr, p25Lat, medianLat, p75Lat;
        long gcCount, gcTimeMs;
        public DetailedMetric(String h, int s, double p25T, double medT, double p75T, double p25L, double medL, double p75L, long gcC, long gcTm) {
            this.host = h; this.sizeKB = s;
            this.p25Thr = p25T; this.medianThr = medT; this.p75Thr = p75T;
            this.p25Lat = p25L; this.medianLat = medL; this.p75Lat = p75L;
            this.gcCount = gcC; this.gcTimeMs = gcTm;
        }
    }
    
    private static void saveResults(List<DetailedMetric> results, String filename) throws Exception {
        PrintWriter writer = new PrintWriter(filename);
        writer.println("host,size_kb,p25_throughput_mbps,median_throughput_mbps,p75_throughput_mbps," +
                      "p25_latency_ms,median_latency_ms,p75_latency_ms,gc_count,gc_time_ms");
        for (DetailedMetric m : results) {
            writer.printf(Locale.US, "%s,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%d,%d\n",
                m.host, m.sizeKB, m.p25Thr, m.medianThr, m.p75Thr, m.p25Lat, m.medianLat, m.p75Lat, m.gcCount, m.gcTimeMs);
        }
        writer.close();
        System.out.println("\n✓ Results saved: " + filename);
    }

    private static List<String> getWorkerHosts() throws Exception {
        String nodeFile = System.getenv("OAR_NODE_FILE");
        if (nodeFile == null) return Arrays.asList("localhost");
        String masterHost = java.net.InetAddress.getLocalHost().getHostName();
        Set<String> hosts = new HashSet<>();
        BufferedReader reader = new BufferedReader(new FileReader(nodeFile));
        String line;
        while ((line = reader.readLine()) != null) {
            String host = line.trim();
            if (!host.equals(masterHost)) hosts.add(host);
        }
        reader.close();
        return new ArrayList<>(hosts);
    }
}