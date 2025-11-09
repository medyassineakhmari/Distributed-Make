import java.rmi.registry.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class MasterIO {
    
    private static final int[] SIZES_KB = {1, 2, 5, 10, 20, 50, 100, 200, 500, 1024, 2048, 5120, 10240};
    private static final String TEMP_DIR = "/tmp/pingpong-test/";
    
    public static void main(String[] args) {
        try {
            Files.createDirectories(Paths.get(TEMP_DIR));
            
            List<String> workers = getWorkerHosts();
            System.out.println("Testing " + workers.size() + " workers (WITH I/O)");
            
            List<Metric> results = new ArrayList<>();
            
            for (String host : workers) {
                System.out.println("\n=== Testing: " + host + " (I/O) ===");
                
                Registry registry = LocateRegistry.getRegistry(host, 1099);
                PingPongService service = (PingPongService) registry.lookup("PingPong");
                
                System.out.println(service.hello());
                
                // Warmup
                System.out.println("Warming up...");
                double baselineRTT = 0;
                for (int i = 0; i < 30; i++) {
                    long start = System.nanoTime();
                    service.ping(new byte[]{1});
                    long end = System.nanoTime();
                    baselineRTT += (end - start) / 1_000_000.0;
                }
                baselineRTT /= 30.0;
                System.out.printf("Baseline RTT: %.3f ms\n", baselineRTT);
                
                // Créer fichiers de test sur le worker
                System.out.println("Creating test files on worker...");
                for (int sizeKB : SIZES_KB) {
                    String remotePath = TEMP_DIR + "test_" + sizeKB + "KB.txt";
                    service.createTestFile(remotePath, sizeKB);
                }
                System.out.println();
                
                // Tests avec I/O
                for (int sizeKB : SIZES_KB) {
                    String localPath = TEMP_DIR + "local_" + sizeKB + "KB.txt";
                    String remotePath = TEMP_DIR + "test_" + sizeKB + "KB.txt";
                    
                    // Créer fichier local
                    byte[] data = new byte[sizeKB * 1024];
                    Arrays.fill(data, (byte) 'a');
                    Files.write(Paths.get(localPath), data);
                    
                    // Répéter 5 fois
                    double[] times = new double[9];
                    for (int rep = 0; rep < 9; rep++) {
                        long start = System.nanoTime();
                        
                        // LECTURE locale
                        byte[] fileData = Files.readAllBytes(Paths.get(localPath));
                        
                        // ENVOI RMI
                        service.pingWithIO(remotePath);
                        
                        // ÉCRITURE locale
                        String outPath = TEMP_DIR + "received_" + sizeKB + "KB.txt";
                        Files.write(Paths.get(outPath), fileData);
                        
                        long end = System.nanoTime();
                        times[rep] = (end - start) / 1_000_000.0;
                    }
                    Arrays.sort(times);
                    double rttMs = times[4]; // Médiane
                    
                    double throughputMBps = 0;
                    if (sizeKB > 1) {
                        double transferTimeS = (rttMs - baselineRTT) / 1000.0;
                        if (transferTimeS > 0) {
                            throughputMBps = (sizeKB / 1024.0) / transferTimeS;
                        }
                    }
                    
                    Metric m = new Metric(host, sizeKB, rttMs, throughputMBps, "io");
                    results.add(m);
                    
                    System.out.printf("Size: %5d KB | RTT: %8.3f ms | Throughput: %10.3f MB/s\n",
                            sizeKB, rttMs, throughputMBps);
                }
            }
            
            saveResults(results, "pingpong-io.csv");
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private static List<String> getWorkerHosts() throws Exception {
        String nodeFile = System.getenv("OAR_NODE_FILE");
        if (nodeFile == null) {
            return Arrays.asList("localhost");
        }
        
        String masterHost = java.net.InetAddress.getLocalHost().getHostName();
        Set<String> hosts = new HashSet<>();
        
        BufferedReader reader = new BufferedReader(new FileReader(nodeFile));
        String line;
        while ((line = reader.readLine()) != null) {
            String host = line.trim();
            if (!host.equals(masterHost)) {
                hosts.add(host);
            }
        }
        reader.close();
        
        return new ArrayList<>(hosts);
    }
    
    private static void saveResults(List<Metric> results, String filename) throws Exception {
        PrintWriter writer = new PrintWriter(filename);
        writer.println("host,size_kb,rtt_ms,throughput_mbps,type");
        for (Metric m : results) {
            writer.println(m);
        }
        writer.close();
        System.out.println("\nResults saved: " + filename);
    }
}