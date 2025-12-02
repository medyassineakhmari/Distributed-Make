import java.rmi.registry.*;
import java.io.*;
import java.util.*;
import java.net.InetAddress;

/**
 * MasterOPA.java - Test Omni-Path/InfiniBand network (172.18.x.x IPs)
 * 
 * This variant forces the use of Omni-Path IPs (172.18.x.x) instead of
 * Ethernet IPs (172.16.x.x). It reads the OAR_NODE_FILE and resolves
 * each hostname to its IB0 IP address.
 * 
 * Usage: java MasterOPA
 * Environment: OAR_NODE_FILE must be set (automatic in OAR jobs)
 */
public class MasterOPA {
    
    private static final int[] SIZES_KB = {1, 2, 5, 10, 20, 50, 100, 200, 500, 1024, 2048, 5120, 10240};
    
    public static void main(String[] args) {
        try {
            // 🚀 Optimisations RMI pour meilleur débit
            System.setProperty("sun.rmi.transport.tcp.directByteBufferPool", "true");
            System.setProperty("sun.rmi.serialization.useProxyClass", "false");
            System.setProperty("sun.rmi.transport.tcp.responseTimeout", "10000");
            System.setProperty("sun.rmi.transport.tcp.readTimeout", "10000");
            
            System.out.println("========================================");
            System.out.println("  PingPong - OMNI-PATH (100G) Test");
            System.out.println("========================================\n");
            
            List<String> workers = getWorkerHostsOPA();
            System.out.println("Testing " + workers.size() + " workers on Omni-Path network");
            
            List<Metric> results = new ArrayList<>();
            
            for (String host : workers) {
                System.out.println("\n=== Testing OPA: " + host + " ===");
                
                try {
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
                        
                        if (rtt < baselineRTT) {
                            baselineRTT = rtt;
                        }
                    }
                    System.out.printf("Baseline RTT: %.3f ms\n\n", baselineRTT);
                    
                    // Tests
                    for (int sizeKB : SIZES_KB) {
                        byte[] data = new byte[sizeKB * 1024];
                        
                        double[] times = new double[9];
                        for (int rep = 0; rep < 9; rep++) {
                            long start = System.nanoTime();
                            service.ping(data);
                            long end = System.nanoTime();
                            times[rep] = (end - start) / 1_000_000.0;
                        }
                        Arrays.sort(times);
                        double rttMs = times[4];
                        
                        double throughputMBps = 0;
                        if (sizeKB > 1) {
                            double transferTimeS = (rttMs - baselineRTT) / 1000.0;
                            if (transferTimeS > 0) {
                                throughputMBps = (sizeKB / 1024.0) / transferTimeS;
                            }
                        }
                        
                        Metric m = new Metric(host, sizeKB, rttMs, throughputMBps, "opa");
                        results.add(m);
                        
                        System.out.printf("Size: %5d KB | RTT: %8.3f ms | Throughput: %10.4f MB/s\n",
                                sizeKB, rttMs, throughputMBps);
                    }
                } catch (Exception e) {
                    System.err.println("Error testing worker " + host + ": " + e.getMessage());
                }
            }
            
            saveResults(results, "pingpong-opa.csv");
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    /**
     * Récupère les hostnames depuis OAR_NODE_FILE, puis résout chaque
     * hostname en IP Omni-Path (172.18.x.x).
     */
    private static List<String> getWorkerHostsOPA() throws Exception {
        String nodeFile = System.getenv("OAR_NODE_FILE");
        if (nodeFile == null) {
            System.out.println("Warning: OAR_NODE_FILE not set, using localhost");
            return Arrays.asList("localhost");
        }
        
        String masterHost = java.net.InetAddress.getLocalHost().getHostName();
        Map<String, String> hostsToIPs = new LinkedHashMap<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(nodeFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String hostname = line.trim();
                if (!hostname.isEmpty() && !hostname.equals(masterHost)) {
                    String opaIP = resolveToOPAIP(hostname);
                    hostsToIPs.put(hostname, opaIP);
                    System.out.println("  " + hostname + " → " + opaIP);
                }
            }
        }
        
        return new ArrayList<>(hostsToIPs.values());
    }
    
    /**
     * Résout un hostname en IP Omni-Path (172.18.x.x)
     * 
     * Stratégie :
     * 1. Essaie d'abord de résoudre vers 172.18.x.x directement
     * 2. Si échoue, essaie de construire l'IP OPA depuis l'IP Ethernet (172.16.x.x → 172.18.x.x)
     * 3. Si toujours échoue, fallback sur Ethernet
     */
    private static String resolveToOPAIP(String hostname) {
        // Stratégie 1 : Essaie de résoudre et cherche une IP 172.18.x.x
        try {
            InetAddress[] addrs = InetAddress.getAllByName(hostname);
            for (InetAddress addr : addrs) {
                String ip = addr.getHostAddress();
                if (isOPANetwork(ip)) {
                    System.out.println("    ✓ Found OPA IP directly: " + ip);
                    return ip;
                }
            }
        } catch (Exception e) {
            // Silencieux
        }
        
        // Stratégie 2 : Résoudre en IP Ethernet et la convertir en IP OPA
        try {
            InetAddress addr = InetAddress.getByName(hostname);
            String ethernetIP = addr.getHostAddress();
            
            // Construire l'IP OPA en remplaçant 172.16.x.x par 172.18.x.x
            if (ethernetIP.startsWith("172.16.")) {
                String opaIP = ethernetIP.replace("172.16.", "172.18.");
                System.out.println("    ✓ Converted Ethernet to OPA: " + ethernetIP + " → " + opaIP);
                return opaIP;
            }
        } catch (Exception e) {
            // Silencieux
        }
        
        // Fallback: utilise la première IP resolue (Ethernet)
        try {
            InetAddress addr = InetAddress.getByName(hostname);
            String ip = addr.getHostAddress();
            System.out.println("    ⚠ Using non-OPA IP (fallback): " + ip);
            return ip;
        } catch (Exception e) {
            System.err.println("    ✗ Cannot resolve " + hostname);
            return "localhost";
        }
    }
    
    /**
     * Vérifie si une adresse IP appartient au réseau Omni-Path (172.18.x.x)
     */
    private static boolean isOPANetwork(String ip) {
        return ip.startsWith("172.18.");
    }
    
    private static void saveResults(List<Metric> results, String filename) throws Exception {
        try (PrintWriter writer = new PrintWriter(filename)) {
            writer.println("host,size_kb,rtt_ms,throughput_mbps,type");
            for (Metric m : results) {
                writer.println(m);
            }
        }
        System.out.println("\n✓ Results saved: " + filename);
    }
}
