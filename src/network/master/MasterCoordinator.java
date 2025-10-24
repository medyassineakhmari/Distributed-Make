package network.master;

import network.worker.WorkerInterface;
import parser.Task;
import scheduler.TaskScheduler;

import java.rmi.Naming;

public class MasterCoordinator {

    public static int executeOnWorker(String[] args, String masterHostname, Task task) {
        if (args.length < 2) {
            System.err.println("[MASTER] Invalid arguments");
            return -1;
        }

        String command = args[0];
        String workerHost = args[1];

        try {
            System.out.println("[MASTER] Connecting to worker: " + workerHost);
            String workerUrl = "rmi://" + workerHost + ":3000/WorkerService";
            WorkerInterface worker = (WorkerInterface) Naming.lookup(workerUrl);

            handleDependencies(task, worker, masterHostname, workerHost);

            System.out.println("[MASTER] Executing on " + workerHost + ": " + command);
            int exitCode = worker.executeCommand(command);

            if (exitCode == 0) {
                retrieveResults(task, workerHost, masterHostname);
            }

            return exitCode;

        } catch (Exception e) {
            System.err.println("[MASTER] Error executing on worker: " + e.getMessage());
            e.printStackTrace();
            return -1;
        }
    }

    private static void handleDependencies(Task task, WorkerInterface worker, 
                                          String masterHost, String workerHost) {
        try {
            if (TaskScheduler.graph.get(task) != null) {
                for (Task dependency : TaskScheduler.graph.get(task)) {
                    String filename = dependency.getTaskName();

                    int exists = worker.executeCommand("test -f " + filename + " && echo 'exists' || echo 'missing'");

                    if (exists != 0) {
                        System.out.println("[MASTER] Transferring " + filename + " to " + workerHost);
                        transferFile(masterHost, workerHost, filename);
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("[MASTER] Error handling dependencies: " + e.getMessage());
        }
    }

    private static void retrieveResults(Task task, String workerHost, String masterHost) {
        try {
            String resultFile = task.getTaskName();
            if (resultFile.contains(".")) {
                System.out.println("[MASTER] Retrieving result: " + resultFile);
                transferFile(workerHost, masterHost, resultFile);
            }
        } catch (Exception e) {
            System.err.println("[MASTER] Error retrieving results: " + e.getMessage());
        }
    }

    private static void transferFile(String sourceHost, String destHost, String filename) {
        try {
            String command = "scp " + sourceHost + ":" + filename + " " + destHost + ":~";
            Process process = Runtime.getRuntime().exec(command);
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                System.out.println("[MASTER] ✅ File transferred: " + filename);
            } else {
                System.err.println("[MASTER] ❌ File transfer failed: " + filename);
            }
        } catch (Exception e) {
            System.err.println("[MASTER] Error transferring file: " + e.getMessage());
        }
    }
}
