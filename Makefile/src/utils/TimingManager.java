package utils;

import java.util.LinkedHashMap;
import java.util.Map;

public class TimingManager {
    private static long startTime;
    private static final Map<String, Long> timestamps = new LinkedHashMap<>();
    
    private TimingManager() {
        throw new UnsupportedOperationException("TimingManager is a utility class");
    }
    
    public static void startTiming() {
        timestamps.clear();
        startTime = System.nanoTime();
        timestamp("START");
    }
    
    public static void timestamp(String phase) {
        timestamps.put(phase, System.nanoTime());
    }
    
    public static void printReport() {
        System.out.println("\n------------------------------------------");
        System.out.println("           TIMING REPORT                ");
        System.out.println("------------------------------------------");
        
        for (Map.Entry<String, Long> entry : timestamps.entrySet()) {
            long durationMs = (entry.getValue() - startTime) / 1_000_000;
            System.out.println(String.format(" %-30s : %4dms ", entry.getKey(), durationMs));
        }
        System.out.println("------------------------------------------\n");
    }
    
    public static long getPhaseDuration(String phase) {
        Long phaseTime = timestamps.get(phase);
        if (phaseTime == null) return -1;
        return (phaseTime - startTime) / 1_000_000;
    }
}