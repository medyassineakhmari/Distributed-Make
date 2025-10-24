package parser;

import cluster.ComputeNode;
import network.master.MasterCoordinator;
import cluster.ClusterManager;
import cluster.NodeStatus;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Task {
    private String taskName;
    private List<String> commands;
    public TaskStatus status;
    public static ComputeNode master;
    private Random random = new Random();

    public Task() {
        this.commands = new ArrayList<>();
        this.status = TaskStatus.NOT_STARTED;
    }

    public Task(String name) {
        this.taskName = name;
        this.commands = new ArrayList<>();
        this.status = TaskStatus.NOT_STARTED;
    }

    public String getTaskName() {
        return taskName;
    }

    public void setTaskName(String name) {
        this.taskName = name;
    }

    public List<String> getCommands() {
        return commands;
    }

    public void addCommand(String command) {
        this.commands.add(command);
    }

    public void execute() {
        try {
            for (String command : commands) {
                System.out.println("[TASK " + taskName + "] Searching for available worker...");

                ComputeNode availableWorker = null;
                while (availableWorker == null) {
                    synchronized (ClusterManager.nodes) {
                        for (ComputeNode node : ClusterManager.nodes) {
                            if (node.status == NodeStatus.FREE) {
                                availableWorker = node;
                                availableWorker.status = NodeStatus.OCCUPIED;
                                break;
                            }
                        }
                    }

                    if (availableWorker == null) {
                        System.out.println("[TASK " + taskName + "] All workers busy, waiting...");
                        Thread.sleep(100 + random.nextInt(100));
                    }
                }

                System.out.println("[TASK " + taskName + "] Assigned to worker: " + availableWorker.hostname);

                String[] arguments = new String[]{command, availableWorker.hostname};
                int exitCode = MasterCoordinator.executeOnWorker(arguments, master.hostname, this);

                if (exitCode == 0) {
                    availableWorker.status = NodeStatus.FREE;
                    System.out.println("[TASK " + taskName + "] Completed successfully on " + availableWorker.hostname);
                } else {
                    availableWorker.status = NodeStatus.FREE;
                    System.err.println("[TASK " + taskName + "] Failed with exit code: " + exitCode);
                    this.status = TaskStatus.FAILED;
                    return;
                }
            }

            this.status = TaskStatus.FINISHED;

        } catch (Exception e) {
            System.err.println("[TASK " + taskName + "] Exception: " + e.getMessage());
            e.printStackTrace();
            this.status = TaskStatus.FAILED;
        }
    }

    @Override
    public String toString() {
        return "Task{name='" + taskName + "', status=" + status + ", commands=" + commands.size() + '}';
    }
}
