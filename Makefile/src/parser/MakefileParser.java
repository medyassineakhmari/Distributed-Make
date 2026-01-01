package parser;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

public class MakefileParser {
    private BufferedReader reader;
    private String currentLine;
    private HashMap<TaskNFS, List<TaskNFS>> graphNFS;
    private HashMap<String, TaskNFS> taskMapNFS;

    public MakefileParser() {
        this.graphNFS = new HashMap<>();
        this.taskMapNFS = new HashMap<>();
    }

    public HashMap<TaskNFS, List<TaskNFS>> processFileNFS(String filePath) throws IOException {
        if (filePath == null || filePath.trim().isEmpty()) {
            throw new IllegalArgumentException("File path cannot be null or empty");
        }

        this.graphNFS = new HashMap<>();
        this.taskMapNFS = new HashMap<>();

        System.out.println("[PARSER-NFS] Reading Makefile from: " + filePath);

        try {
            reader = new BufferedReader(new FileReader(filePath));
            currentLine = reader.readLine();

            while (currentLine != null) {
                parseRuleNFS();
                currentLine = reader.readLine();
            }

            reader.close();
            System.out.println("[PARSER-NFS] Successfully parsed Makefile: " + graphNFS.size() + " tasks found");

            if (graphNFS.isEmpty()) {
                System.err.println("[PARSER-NFS] Warning: No tasks found in Makefile");
            }

        } catch (IOException e) {
            System.err.println("[PARSER-NFS] Error reading Makefile: " + e.getMessage());
            throw e;
        }

        return graphNFS;
    }

    private void parseRuleNFS() {
        if (currentLine == null || currentLine.trim().isEmpty() || currentLine.startsWith("#")) {
            return;
        }

        if (currentLine.contains(":") && !currentLine.startsWith("\t")) {
            String[] parts = currentLine.split(":", 2);
            String targetName = parts[0].trim();
            String dependenciesStr = parts.length > 1 ? parts[1].trim() : "";

            TaskNFS targetTask = taskMapNFS.getOrDefault(targetName, new TaskNFS(targetName));
            taskMapNFS.put(targetName, targetTask);

            List<TaskNFS> dependencies = new ArrayList<>();
            if (!dependenciesStr.isEmpty()) {
                String[] depNames = dependenciesStr.split("\\s+");
                for (String depName : depNames) {
                    if (!depName.trim().isEmpty()) {
                        TaskNFS depTask = taskMapNFS.getOrDefault(depName, new TaskNFS(depName));
                        taskMapNFS.put(depName, depTask);
                        dependencies.add(depTask);
                    }
                }
            }

            try {
                currentLine = reader.readLine();
                while (currentLine != null && currentLine.startsWith("\t")) {
                    String command = currentLine.substring(1);
                    if (!command.trim().isEmpty()) {
                        targetTask.addCommand(command);
                    }
                    currentLine = reader.readLine();
                }
            } catch (IOException e) {
                System.err.println("[PARSER-NFS] Error reading commands for task " + targetName);
                e.printStackTrace();
            }

            graphNFS.put(targetTask, dependencies);
        }
    }

    public void printGraphNFS() {
        System.out.println("\n[PARSER-NFS] Dependency Graph:");
        System.out.println("========================");
        for (Map.Entry<TaskNFS, List<TaskNFS>> entry : graphNFS.entrySet()) {
            TaskNFS task = entry.getKey();
            List<TaskNFS> deps = entry.getValue();
            System.out.print(task.getTaskName() + " depends on: ");
            if (deps.isEmpty()) {
                System.out.println("nothing (can start immediately)");
            } else {
                System.out.println(deps.stream()
                    .map(TaskNFS::getTaskName)
                    .reduce((a, b) -> a + ", " + b)
                    .orElse(""));
            }
            System.out.println("  Commands: " + task.getCommands().size());
        }
        System.out.println("========================\n");
    }
}
