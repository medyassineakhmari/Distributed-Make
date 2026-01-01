package network.master;

import config.Configuration;
import network.worker.WorkerInterface;
import java.rmi.Naming;

public class MasterCoordinatorNFS {

    public static int executeOnWorker(String command, String workerHost, int workerPort) {
        if (command == null || command.trim().isEmpty()) {
            System.err.println("[MASTER-NFS] Invalid command");
            return -1;
        }

        if (workerHost == null || workerHost.trim().isEmpty()) {
            System.err.println("[MASTER-NFS] Invalid worker host");
            return -1;
        }

        try {
            System.out.println("[MASTER-NFS] Connecting to worker: " + workerHost + ":" + workerPort);
            String workerUrl = Configuration.buildRmiUrl(workerHost, workerPort);
            WorkerInterface worker = (WorkerInterface) Naming.lookup(workerUrl);

            System.out.println("[MASTER-NFS] Executing on " + workerHost + ":" + workerPort);
            System.out.println("[MASTER-NFS]   Command: " + command);
            int exitCode = worker.executeCommand(command);

            if (exitCode == 0) {
                System.out.println("[MASTER-NFS] Execution successful (results accessible via NFS)");
            } else {
                System.err.println("[MASTER-NFS] Execution failed with exit code: " + exitCode);
            }

            return exitCode;

        } catch (java.rmi.NotBoundException e) {
            System.err.println("[MASTER-NFS] Worker not found at " + workerHost + ":" + workerPort);
            System.err.println("[MASTER-NFS]    Make sure the worker is running and bound to 'WorkerService'");
            return -1;
        } catch (java.rmi.ConnectException e) {
            System.err.println("[MASTER-NFS] Cannot connect to worker " + workerHost + ":" + workerPort);
            System.err.println("[MASTER-NFS]    Check network connectivity and firewall settings");
            return -1;
        } catch (Exception e) {
            System.err.println("[MASTER-NFS] Error executing on worker " + workerHost + ": " + e.getMessage());
            e.printStackTrace();
            return -1;
        }
    }

    public static boolean isLocalhost(String hostname) {
        if (hostname == null) return false;
        String normalized = hostname.trim().toLowerCase();
        return normalized.equals("localhost") ||
               normalized.equals("127.0.0.1") ||
               normalized.equals("::1") ||
               normalized.equals("0.0.0.0");
    }
}