public class Metric {
    private String worker;
    private int dataSize;
    private double rtt;
    private double throughput;

    public Metric(String worker, int dataSize, double rtt, double throughput) {
        this.worker = worker;
        this.dataSize = dataSize;
        this.rtt = rtt;
        this.throughput = throughput;
    }

    public String getWorker() {
        return worker;
    }

    public int getDataSize() {
        return dataSize;
    }

    public double getRtt() {
        return rtt;
    }

    public double getThroughput() {
        return throughput;
    }

    @Override
    public String toString() {
        return String.format("Worker: %s, Size: %d KB, RTT: %.2f ms, Throughput: %.2f MB/s",
                worker, dataSize, rtt, throughput);
    }
}