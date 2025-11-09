import java.rmi.registry.*;
import java.io.*;
import java.util.*;

public class SitesComparaison {
    
    public static void main(String[] args) {
        try {
            List<String> workers = getWorkerHosts();
            System.out.println("Testing " + workers.size() + " workers for sites comparison");
            
            PrintWriter writer = new PrintWriter("sites-comparison.csv");
            writer.println("site,latency_ms,throughput_mbps");
            
            for (String host : workers) {
                System.out.println("\n=== Testing: " + host + " ===");
                
                Registry registry = LocateRegistry.getRegistry(host, 1099);
                PingPongService service = (PingPongService) registry.lookup("PingPong");
                
                // Mesurer latence (N=1)
                double latency = 0;
                for (int i = 0; i < 50; i++) {
                    long start = System.nanoTime();
                    service.ping(new byte[]{1});
                    long end = System.nanoTime();
                    latency += (end - start) / 1_000_000.0;
                }
                latency = (latency / 50.0) / 2.0; // RTT/2 = latence
                
                // Mesurer débit (N=10MB)
                byte[] bigData = new byte[10 * 1024 * 1024];
                double[] times = new double[10];
                for (int i = 0; i < 10; i++) {
                    long start = System.nanoTime();
                    service.ping(bigData);
                    long end = System.nanoTime();
                    times[i] = (end - start) / 1_000_000.0;
                }
                Arrays.sort(times);
                double rttMs = times[5]; // Médiane
                double throughput = 10.0 / ((rttMs - latency * 2) / 1000.0);
                
                String siteName = host.split("\\.")[0];
                writer.printf("%s,%.6f,%.6f\n", siteName, latency, throughput);
                System.out.printf("Site: %s | Latency: %.3f ms | Throughput: %.3f MB/s\n",
                        siteName, latency, throughput);
            }
            
            writer.close();
            System.out.println("\nSites comparison saved: sites-comparison.csv");
            
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
}