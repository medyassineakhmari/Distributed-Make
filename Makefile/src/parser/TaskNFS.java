package parser;

import cluster.ClusterManager;
import cluster.ComputeNode;
import config.Configuration;
import network.master.MasterCoordinatorNFS;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class TaskNFS {
    private final String taskName;
    private final List<String> commands;
    private volatile TaskStatus status;
    private ClusterManager clusterManager;
    private String nfsPath;
    private final Random random;

    public TaskNFS() {
        this("", null);
    }

    public TaskNFS(String name) {
        this(name, null);
    }

    public TaskNFS(String name, ClusterManager clusterManager) {
        if (name == null) {
            throw new IllegalArgumentException("Task name cannot be null");
        }
        this.taskName = name;
        this.commands = new ArrayList<>();
        this.status = TaskStatus.NOT_STARTED;
        this.clusterManager = clusterManager;
        this.nfsPath = "/tmp/nfs_shared";
        this.random = new Random();
    }

    public String getTaskName() {
        return taskName;
    }

    public List<String> getCommands() {
        return new ArrayList<>(commands);
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus status) {
        if (status == null) {
            throw new IllegalArgumentException("Status cannot be null");
        }
        this.status = status;
    }

    public void setNfsPath(String nfsPath) {
        if (nfsPath == null || nfsPath.trim().isEmpty()) {
            throw new IllegalArgumentException("NFS path cannot be null or empty");
        }
        this.nfsPath = nfsPath;
    }

    public String getNfsPath() {
        return nfsPath;
    }

    public void addCommand(String command) {
        if (command == null || command.trim().isEmpty()) {
            throw new IllegalArgumentException("Command cannot be null or empty");
        }
        this.commands.add(command);
    }

    public void setClusterManager(ClusterManager manager) {
        if (manager == null) {
            throw new IllegalArgumentException("ClusterManager cannot be null");
        }
        this.clusterManager = manager;
    }

    private boolean isAggregationTask() {
        return taskName.contains("total.txt") ||
               (commands.stream().anyMatch(cmd ->
                   cmd.contains("cat") && cmd.contains("count") && cmd.contains("awk")));
    }

    public void execute() {
        if (clusterManager == null) {
            System.err.println("[TASK-NFS " + taskName + "] No cluster manager configured");
            this.status = TaskStatus.FAILED;
            return;
        }

        if (commands.isEmpty()) {
            System.out.println("[TASK-NFS " + taskName + "] No commands to execute, marking as finished");
            this.status = TaskStatus.FINISHED;
            return;
        }

        try {
            if (isAggregationTask()) {
                System.out.println("[TASK-NFS " + taskName + "] Running aggregation locally (accessing NFS)");
                for (String command : commands) {
                    if (!executeLocalCommand(command)) {
                        return;
                    }
                }
            } else {
                for (String command : commands) {
                    if (!executeCommand(command)) {
                        return;
                    }
                }
            }

            this.status = TaskStatus.FINISHED;

        } catch (Exception e) {
            System.err.println("[TASK-NFS " + taskName + "] Exception: " + e.getMessage());
            e.printStackTrace();
            this.status = TaskStatus.FAILED;
        }
    }

    private boolean executeLocalCommand(String command) {
        System.out.println("[TASK-NFS " + taskName + "] Executing locally: " + command);

        try {
            String cdCommand = "cd " + nfsPath + " && " + command;
            String[] execCommand = {"/bin/bash", "-c", cdCommand};
            Process process = Runtime.getRuntime().exec(execCommand);
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                System.out.println("[TASK-NFS " + taskName + "] Local execution successful");
                return true;
            } else {
                java.io.BufferedReader errorReader = new java.io.BufferedReader(
                    new java.io.InputStreamReader(process.getErrorStream()));
                String line;
                System.err.println("[TASK-NFS " + taskName + "] Local execution failed with exit code: " + exitCode);
                while ((line = errorReader.readLine()) != null) {
                    System.err.println("[ERROR] " + line);
                }
                this.status = TaskStatus.FAILED;
                return false;
            }
        } catch (Exception e) {
            System.err.println("[TASK-NFS " + taskName + "] Exception during local execution: " + e.getMessage());
            e.printStackTrace();
            this.status = TaskStatus.FAILED;
            return false;
        }
    }

    private boolean executeCommand(String command) {
        System.out.println("[TASK-NFS " + taskName + "] Searching for available worker...");

        ComputeNode availableWorker = null;
        int retryCount = 0;
        final int MAX_RETRIES = 100;

        while (availableWorker == null && retryCount < MAX_RETRIES) {
            availableWorker = clusterManager.acquireAvailableNode();

            if (availableWorker == null) {
                retryCount++;
                if (retryCount % 10 == 0) {
                    System.out.println("[TASK-NFS " + taskName + "] All workers busy, waiting... (retry " + retryCount + ")");
                }
                try {
                    Thread.sleep(Configuration.TASK_RETRY_BASE_WAIT_MS +
                                random.nextInt(Configuration.TASK_RETRY_RANDOM_RANGE_MS));
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    System.err.println("[TASK-NFS " + taskName + "] Interrupted while waiting for worker");
                    this.status = TaskStatus.FAILED;
                    return false;
                }
            }
        }

        if (availableWorker == null) {
            System.err.println("[TASK-NFS " + taskName + "] Failed to acquire worker after " + MAX_RETRIES + " retries");
            this.status = TaskStatus.FAILED;
            return false;
        }

        try {
            System.out.println("[TASK-NFS " + taskName + "] Assigned to worker: " + availableWorker.hostname + ":" + availableWorker.port);

            String cdCommand = "cd " + nfsPath + " && " + command;
            int exitCode = MasterCoordinatorNFS.executeOnWorker(
                cdCommand,
                availableWorker.hostname,
                availableWorker.port
            );

            if (exitCode == 0) {
                System.out.println("[TASK-NFS " + taskName + "] Completed successfully on " + availableWorker.hostname + ":" + availableWorker.port);
                return true;
            } else {
                System.err.println("[TASK-NFS " + taskName + "] Failed with exit code: " + exitCode);
                this.status = TaskStatus.FAILED;
                return false;
            }

        } finally {
            clusterManager.releaseNode(availableWorker);
        }
    }

    @Override
    public String toString() {
        return "TaskNFS{name='" + taskName + "', status=" + status + ", commands=" + commands.size() + ", nfsPath='" + nfsPath + "'}";
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TaskNFS taskNFS = (TaskNFS) o;
        return taskName.equals(taskNFS.taskName);
    }

    @Override
    public int hashCode() {
        return taskName.hashCode();
    }
}
