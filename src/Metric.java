import java.io.Serializable;

public class Metric implements Serializable {
    String host;
    int sizeKB;
    double rttMs;
    double throughputMBps;
    String type; // "normal" ou "io"
    
    public Metric(String host, int sizeKB, double rttMs, double throughputMBps, String type) {
        this.host = host;
        this.sizeKB = sizeKB;
        this.rttMs = rttMs;
        this.throughputMBps = throughputMBps;
        this.type = type;
    }
    
    @Override
    public String toString() {
        return String.format("%s,%d,%.6f,%.6f,%s", host, sizeKB, rttMs, throughputMBps, type);
    }
}