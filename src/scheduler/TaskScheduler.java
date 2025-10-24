package scheduler;

import parser.Task;
import parser.TaskStatus;

import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class TaskScheduler {
    public static Map<Task, List<Task>> graph = new HashMap<>();

    public void addTask(Task task, List<Task> dependencies) {
        graph.put(task, dependencies);
    }

    public void executeTasks() throws InterruptedException {
        System.out.println("\n[SCHEDULER] Starting task execution...");
        ExecutorService executor = Executors.newCachedThreadPool();

        int iteration = 0;
        while (!allTasksCompleted()) {
            iteration++;
            System.out.println("\n[SCHEDULER] Iteration " + iteration + " - Checking for ready tasks...");

            for (Map.Entry<Task, List<Task>> entry : graph.entrySet()) {
                Task task = entry.getKey();

                if (canBeExecuted(task)) {
                    task.status = TaskStatus.IN_PROGRESS;
                    System.out.println("[SCHEDULER] Launching task: " + task.getTaskName());
                    executor.submit(task::execute);
                }
            }

            Thread.sleep(500);
        }

        System.out.println("\n[SCHEDULER] All tasks submitted, waiting for completion...");
        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.HOURS);

        System.out.println("\n[SCHEDULER] ✅ All tasks completed!");
        printFinalStatus();
    }

    private boolean canBeExecuted(Task task) {
        if (task.status != TaskStatus.NOT_STARTED) {
            return false;
        }

        List<Task> dependencies = graph.get(task);
        if (dependencies == null || dependencies.isEmpty()) {
            return true;
        }

        return dependencies.stream()
                .allMatch(dep -> dep.status == TaskStatus.FINISHED);
    }

    private boolean allTasksCompleted() {
        return graph.keySet().stream()
                .allMatch(task -> task.status == TaskStatus.FINISHED || task.status == TaskStatus.FAILED);
    }

    private void printFinalStatus() {
        System.out.println("\n[SCHEDULER] Final Status:");
        System.out.println("========================");
        for (Task task : graph.keySet()) {
            String statusSymbol = task.status == TaskStatus.FINISHED ? "✅" : "❌";
            System.out.println(statusSymbol + " " + task.getTaskName() + " - " + task.status);
        }
        System.out.println("========================\n");
    }
}
