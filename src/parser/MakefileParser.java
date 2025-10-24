package parser;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

public class MakefileParser {
    private BufferedReader reader;
    private String currentLine;
    private HashMap<Task, List<Task>> graph;
    private HashMap<String, Task> taskMap;

    public MakefileParser() {
        this.graph = new HashMap<>();
        this.taskMap = new HashMap<>();
    }

    public HashMap<Task, List<Task>> processFile(String filePath) {
        try {
            reader = new BufferedReader(new FileReader(filePath));
            currentLine = reader.readLine();

            while (currentLine != null) {
                parseRule();
                currentLine = reader.readLine();
            }

            reader.close();
            System.out.println("[PARSER] Successfully parsed Makefile: " + graph.size() + " tasks found");

        } catch (IOException e) {
            System.err.println("[PARSER] Error reading Makefile: " + e.getMessage());
            e.printStackTrace();
        }

        return graph;
    }

    private void parseRule() {
        if (currentLine == null || currentLine.trim().isEmpty() || currentLine.startsWith("#")) {
            return;
        }

        if (currentLine.contains(":") && !currentLine.startsWith("\t")) {
            String[] parts = currentLine.split(":", 2);
            String targetName = parts[0].trim();
            String dependenciesStr = parts.length > 1 ? parts[1].trim() : "";

            Task targetTask = taskMap.getOrDefault(targetName, new Task(targetName));
            taskMap.put(targetName, targetTask);

            List<Task> dependencies = new ArrayList<>();
            if (!dependenciesStr.isEmpty()) {
                String[] depNames = dependenciesStr.split("\\s+");
                for (String depName : depNames) {
                    Task depTask = taskMap.getOrDefault(depName, new Task(depName));
                    taskMap.put(depName, depTask);
                    dependencies.add(depTask);
                }
            }

            try {
                currentLine = reader.readLine();
                while (currentLine != null && currentLine.startsWith("\t")) {
                    String command = currentLine.substring(1);
                    targetTask.addCommand(command);
                    currentLine = reader.readLine();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }

            graph.put(targetTask, dependencies);
        }
    }

    public void printGraph() {
        System.out.println("\n[PARSER] Dependency Graph:");
        System.out.println("========================");
        for (Map.Entry<Task, List<Task>> entry : graph.entrySet()) {
            Task task = entry.getKey();
            List<Task> deps = entry.getValue();
            System.out.print(task.getTaskName() + " depends on: ");
            if (deps.isEmpty()) {
                System.out.println("nothing (can start immediately)");
            } else {
                System.out.println(deps.stream()
                    .map(Task::getTaskName)
                    .reduce((a, b) -> a + ", " + b)
                    .orElse(""));
            }
        }
        System.out.println("========================\n");
    }
}
