package scheduler;

import parser.MakefileParser;
import parser.Task;
import cluster.ClusterManager;

import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   DISTRIBUTED WORD COUNT - Mono-Site Architecture       ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝\n");

        if (args.length < 1) {
            System.err.println("Usage: java scheduler.Main \"[worker1,worker2,...]\"");
            System.err.println("Example: java scheduler.Main \"[nancy-2.grid5000.fr,nancy-3.grid5000.fr]\"");
            System.exit(1);
        }

        try {
            System.out.println("[MAIN] Initializing cluster...");
            ClusterManager.initializeCluster(args[0]);

            System.out.println("[MAIN] Parsing Makefile...");
            MakefileParser parser = new MakefileParser();
            Map<Task, List<Task>> graph = parser.processFile("./scheduler/Makefile");
            parser.printGraph();

            System.out.println("[MAIN] Creating task scheduler...");
            TaskScheduler scheduler = new TaskScheduler();

            for (Map.Entry<Task, List<Task>> entry : graph.entrySet()) {
                scheduler.addTask(entry.getKey(), entry.getValue());
            }

            System.out.println("[MAIN] Starting distributed execution...\n");
            scheduler.executeTasks();

            System.out.println("\n[MAIN] ✅ Distributed execution completed successfully!");

        } catch (Exception e) {
            System.err.println("\n[MAIN] ❌ Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
