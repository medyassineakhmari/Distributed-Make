package scheduler;

import config.Configuration;
import parser.TaskNFS;
import parser.TaskStatus;

import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class TaskScheduler {
    private final Map<TaskNFS, List<TaskNFS>> dependencyGraph;

    public TaskScheduler() {
        this.dependencyGraph = new HashMap<>();
    }

    public void addTaskNFS(TaskNFS task, List<TaskNFS> dependencies) {
        if (task == null) {
            throw new IllegalArgumentException("Task cannot be null");
        }
        if (dependencies == null) {
            dependencies = new ArrayList<>();
        }
        dependencyGraph.put(task, dependencies);
    }

    public void executeTasks() throws InterruptedException {
        if (dependencyGraph.isEmpty()) {
            throw new IllegalStateException("No tasks scheduled for execution");
        }

        System.out.println("\n[SCHEDULER-NFS] Starting task execution (NFS mode)...");
        ExecutorService executor = Executors.newCachedThreadPool();

        while (!allTasksCompleted()) {
            System.out.println("\n[SCHEDULER-NFS] Checking for ready tasks...");

            for (Map.Entry<TaskNFS, List<TaskNFS>> entry : dependencyGraph.entrySet()) {
                TaskNFS task = entry.getKey();

                if (canBeExecuted(task)) {
                    task.setStatus(TaskStatus.IN_PROGRESS);
                    System.out.println("[SCHEDULER-NFS] Launching task: " + task.getTaskName());
                    executor.submit(task::execute);
                }
            }

            Thread.sleep(Configuration.SCHEDULER_POLL_INTERVAL_MS);
        }

        System.out.println("\n[SCHEDULER-NFS] All tasks submitted, waiting for completion...");
        executor.shutdown();
        if (!executor.awaitTermination(Configuration.SCHEDULER_TIMEOUT_HOURS, TimeUnit.HOURS)) {
            System.err.println("[SCHEDULER-NFS] Timeout waiting for tasks to complete");
            executor.shutdownNow();
        }

        System.out.println("\n[SCHEDULER-NFS] All tasks completed!");
        printFinalStatus();
    }

    private boolean canBeExecuted(TaskNFS task) {
        if (task.getStatus() != TaskStatus.NOT_STARTED) {
            return false;
        }

        List<TaskNFS> dependencies = dependencyGraph.get(task);
        if (dependencies == null || dependencies.isEmpty()) {
            return true;
        }

        return dependencies.stream()
                .allMatch(dep -> dep.getStatus() == TaskStatus.FINISHED);
    }

    private boolean allTasksCompleted() {
        return dependencyGraph.keySet().stream()
                .allMatch(task -> task.getStatus() == TaskStatus.FINISHED ||
                                  task.getStatus() == TaskStatus.FAILED);
    }

    private void printFinalStatus() {
        System.out.println("\n[SCHEDULER-NFS] Final Status:");
        System.out.println("========================");
        for (TaskNFS task : dependencyGraph.keySet()) {
            String statusSymbol = task.getStatus() == TaskStatus.FINISHED ? "OK" : "KO";
            System.out.println(statusSymbol + " " + task.getTaskName() + " - " + task.getStatus());
        }
        System.out.println("========================\n");
    }

    public int getTaskCount() {
        return dependencyGraph.size();
    }
}
