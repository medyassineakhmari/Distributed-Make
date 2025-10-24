package cluster;

public class ComputeNode {
    public String hostname;
    public NodeStatus status;

    public ComputeNode(String hostname) {
        this.hostname = hostname;
        this.status = NodeStatus.FREE;
    }

    @Override
    public String toString() {
        return "ComputeNode{" + hostname + ", " + status + "}";
    }
}
