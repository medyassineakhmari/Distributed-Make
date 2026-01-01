package cluster;

import config.Configuration;

public class ComputeNode {
    public final String hostname;
    public final int port;
    private volatile NodeStatus status;

    public ComputeNode(String hostname) {
        this(hostname, Configuration.RMI_REGISTRY_PORT);
    }

    public ComputeNode(String hostname, int port) {
        if (hostname == null || hostname.trim().isEmpty()) {
            throw new IllegalArgumentException("Hostname cannot be null or empty");
        }
        if (port < 1024 || port > 65535) {
            throw new IllegalArgumentException("Port must be between 1024 and 65535");
        }
        this.hostname = hostname;
        this.port = port;
        this.status = NodeStatus.FREE;
    }

    public NodeStatus getStatus() {
        return status;
    }

    public void setStatus(NodeStatus status) {
        if (status == null) {
            throw new IllegalArgumentException("Status cannot be null");
        }
        this.status = status;
    }

    @Override
    public String toString() {
        return "ComputeNode{" + hostname + ":" + port + ", " + status + "}";
    }
}