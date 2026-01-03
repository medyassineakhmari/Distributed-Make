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
    
    public static long getDuration(String startPhase, String endPhase) {
        Long start = timestamps.get(startPhase);
        Long end = timestamps.get(endPhase);
        if (start == null || end == null) {
            return -1;
        }
        return (end - start) / 1_000_000;
    }
    
    public static void printReport() {
        System.out.println("\n╗");
        System.out.println("              TIMING REPORT (DETAILED)                    ");
        System.out.println("╝");
        
        String[] phases = timestamps.keySet().toArray(new String[0]);
        for (int i = 1; i < phases.length; i++) {
            long duration = getDuration(phases[i-1], phases[i]);
            System.out.printf("  %-40s : %6d ms\n", phases[i-1] + " → " + phases[i], duration);
        }
        
        long total = getDuration("START", phases[phases.length - 1]);
        System.out.println("  " + "".repeat(58));
        System.out.printf("  %-40s : %6d ms\n", "TOTAL", total);
        System.out.println("╝\n");
    }
    
    public static void exportMetrics(int numWorkers) {
        try {
            long t_init = getDuration("CLUSTER_INIT_START", "CLUSTER_INITIALIZED");
            long t_split = getDuration("FILE_SPLITTING_START", "FILE_SPLITTED");
            long t_calc = getDuration("DISTRIBUTED_EXECUTION_START", "EXECUTION_COMPLETED");
            long t_merge = 0; // Included in t_calc
            long t_total = getDuration("START", "EXECUTION_COMPLETED");
            
            System.out.println("\n[METRICS_CSV]");
            System.out.printf("%d,%d,%d,%d,%d,%d\n", 
                numWorkers, t_init, t_split, t_calc, t_merge, t_total);
        } catch (Exception e) {
            System.err.println("[TIMING] Error: " + e.getMessage());
        }
    }
}
