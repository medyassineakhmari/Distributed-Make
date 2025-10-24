package network.worker;

import java.rmi.Naming;
import java.rmi.registry.LocateRegistry;

public class WorkerNode {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: java network.worker.WorkerNode <hostname>");
            System.exit(1);
        }

        String hostname = args[0];
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   WORKER NODE STARTING                                   ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");
        System.out.println("[WORKER] Node: " + hostname);

        try {
            System.out.println("[WORKER] Creating RMI registry on port 3000...");
            LocateRegistry.createRegistry(3000);

            System.out.println("[WORKER] Creating worker implementation...");
            WorkerImpl worker = new WorkerImpl();

            String url = "rmi://" + hostname + ":3000/WorkerService";
            Naming.rebind(url, worker);

            System.out.println("[WORKER] ✅ Worker ready and waiting for tasks!");
            System.out.println("[WORKER] RMI URL: " + url);
            System.out.println("[WORKER] Press Ctrl+C to stop");

            Thread.sleep(Long.MAX_VALUE);

        } catch (Exception e) {
            System.err.println("[WORKER] ❌ Failed to start: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
