package cluster;

import parser.Task;

import java.util.ArrayList;
import java.util.List;

public class ClusterManager {
    public static List<ComputeNode> nodes = new ArrayList<>();

    public static void initializeCluster(String nodesList) {
        String cleaned = nodesList.replaceAll("[\\[\\]'\"]", "").trim();
        String[] hostnames = cleaned.split(",");

        System.out.println("[CLUSTER] Initializing cluster with " + hostnames.length + " nodes:");

        for (String hostname : hostnames) {
            hostname = hostname.trim();
            if (!hostname.isEmpty()) {
                ComputeNode node = new ComputeNode(hostname);
                nodes.add(node);
                System.out.println("[CLUSTER]   - " + hostname);
            }
        }

        if (!nodes.isEmpty()) {
            Task.master = nodes.get(0);
            System.out.println("[CLUSTER] Master node: " + Task.master.hostname);
        }

        System.out.println("[CLUSTER] ✅ Cluster initialized with " + nodes.size() + " worker(s)\n");
    }

    public static void printClusterStatus() {
        System.out.println("\n[CLUSTER] Current Status:");
        System.out.println("========================");
        for (ComputeNode node : nodes) {
            String statusSymbol = node.status == NodeStatus.FREE ? "✅" : "⏳";
            System.out.println(statusSymbol + " " + node.hostname + " - " + node.status);
        }
        System.out.println("========================\n");
    }
}
