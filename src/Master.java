import java.rmi.registry.*;
import java.io.*;
import java.util.*;

public class Master {
    
    private static final int[] SIZES_KB = {1, 2, 5, 10, 20, 50, 100, 200, 500, 1024, 2048, 5120, 10240};
    
    public static void main(String[] args) {
        try {
            List<String> workers = getWorkerHosts();
            System.out.println("Testing " + workers.size() + " workers");
            
            List<Metric> results = new ArrayList<>();
            
            for (String host : workers) {
                System.out.println("\n=== Testing: " + host + " ===");
                
                Registry registry = LocateRegistry.getRegistry(host, 1099);
                PingPongService service = (PingPongService) registry.lookup("PingPong");
                
                System.out.println(service.hello());
                
                // Warmup
                System.out.println("Warming up...");
                double baselineRTT = Double.MAX_VALUE;
                for (int i = 0; i < 30; i++) {
                    long start = System.nanoTime();
                    service.ping(new byte[]{1});
                    long end = System.nanoTime();
                    double rtt = (end - start) / 1_000_000.0;
                    
                    // Garder le minimum
                    if (rtt < baselineRTT) {
                        baselineRTT = rtt;
                    }
                }
                System.out.printf("Baseline RTT: %.3f ms\n\n", baselineRTT);
                
                // Tests
                for (int sizeKB : SIZES_KB) {
                    byte[] data = new byte[sizeKB * 1024];
                    
                    // Répéter 5 fois et prendre la médiane
                    double[] times = new double[9];
                    for (int rep = 0; rep < 9; rep++) {
                        long start = System.nanoTime();
                        service.ping(data);
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
                    
                    Metric m = new Metric(host, sizeKB, rttMs, throughputMBps, "normal");
                    results.add(m);
                    
                    System.out.printf("Size: %5d KB | RTT: %8.3f ms | Throughput: %10.4f MB/s\n",
                            sizeKB, rttMs, throughputMBps);
                }
            }
            
            saveResults(results, "pingpong-normal.csv");
            
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