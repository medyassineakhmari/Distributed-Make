package cluster;

import config.Configuration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ClusterManager {
    private final List<ComputeNode> nodes;
    private final ComputeNode masterNode;

    public ClusterManager(String nodesList) {
        if (nodesList == null || nodesList.trim().isEmpty()) {
            throw new IllegalArgumentException("Nodes list cannot be null or empty");
        }

        String cleaned = nodesList.replaceAll("[\\[\\]'\"]", "").trim();
        String[] hostnames = cleaned.split(",");

        List<ComputeNode> tempNodes = new ArrayList<>();
        System.out.println("[CLUSTER] Initializing cluster with " + hostnames.length + " nodes:");

        for (String nodeSpec : hostnames) {
            nodeSpec = nodeSpec.trim();
            if (!nodeSpec.isEmpty()) {
                ComputeNode node = parseNodeSpec(nodeSpec);
                tempNodes.add(node);
                System.out.println("[CLUSTER]   - " + node.hostname + ":" + node.port);
            }
        }

        if (tempNodes.isEmpty()) {
            throw new IllegalArgumentException("No valid nodes found in the list");
        }

        if (tempNodes.size() < Configuration.MIN_WORKER_NODES) {
            throw new IllegalArgumentException(
                String.format("At least %d total nodes required (1 master + %d worker(s))",
                    Configuration.MIN_WORKER_NODES, Configuration.MIN_WORKER_NODES - 1)
            );
        }

        if (tempNodes.size() > Configuration.MAX_WORKER_NODES) {
            throw new IllegalArgumentException(
                String.format("Maximum %d worker nodes allowed", Configuration.MAX_WORKER_NODES)
            );
        }

        this.masterNode = tempNodes.get(0);

        List<ComputeNode> workerNodes = new ArrayList<>(tempNodes.subList(1, tempNodes.size()));
        this.nodes = Collections.synchronizedList(workerNodes);

        System.out.println("[CLUSTER] Master node: " + masterNode.hostname + " (coordination only)");
        System.out.println("[CLUSTER] Worker nodes: " + workerNodes.size());
        for (ComputeNode worker : workerNodes) {
            System.out.println("[CLUSTER]   - " + worker.hostname + ":" + worker.port);
        }
        System.out.println("[CLUSTER] Cluster initialized: 1 master + " + workerNodes.size() + " worker(s)\n");
    }

    public List<ComputeNode> getNodes() {
        return nodes;
    }

    public ComputeNode getMasterNode() {
        return masterNode;
    }

    public synchronized ComputeNode acquireAvailableNode() {
        for (ComputeNode node : nodes) {
            if (node.getStatus() == NodeStatus.FREE) {
                node.setStatus(NodeStatus.OCCUPIED);
                return node;
            }
        }
        return null;
    }

    public synchronized void releaseNode(ComputeNode node) {
        if (node != null) {
            node.setStatus(NodeStatus.FREE);
        }
    }

    public void printClusterStatus() {
        System.out.println("\n[CLUSTER] Current Status:");
        System.out.println("========================");
        for (ComputeNode node : nodes) {
            String statusSymbol = node.getStatus() == NodeStatus.FREE ? "[FREE]" : "[BUSY]";
            System.out.println(statusSymbol + " " + node.hostname + " - " + node.getStatus());
        }
        System.out.println("========================\n");
    }

    private ComputeNode parseNodeSpec(String nodeSpec) {
        if (nodeSpec == null || nodeSpec.isEmpty()) {
            throw new IllegalArgumentException("Node specification cannot be null or empty");
        }

        String[] parts = nodeSpec.split(":");
        String hostname = parts[0].trim();

        validateHostname(hostname);

        if (parts.length == 1) {
            return new ComputeNode(hostname);
        } else if (parts.length == 2) {
            try {
                int port = Integer.parseInt(parts[1].trim());
                return new ComputeNode(hostname, port);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Invalid port number in: " + nodeSpec);
            }
        } else {
            throw new IllegalArgumentException("Invalid node specification format: " + nodeSpec);
        }
    }

    private void validateHostname(String hostname) {
        if (hostname == null || hostname.isEmpty()) {
            throw new IllegalArgumentException("Hostname cannot be null or empty");
        }
        if (hostname.length() > 255) {
            throw new IllegalArgumentException("Hostname too long: " + hostname);
        }
    }
}