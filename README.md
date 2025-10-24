# 🚀 Distributed Word Count System

A distributed word counting system using **Java RMI** on **Grid5000** infrastructure (mono-site architecture).

## 📋 Features

- ✅ Makefile parser with dependency resolution
- ✅ Intelligent task scheduler
- ✅ RMI-based distributed execution
- ✅ Automatic load balancing
- ✅ Grid5000 deployment scripts

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                   Grid5000 Site                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐                                      │
│  │ Master Node  │  ← Coordinates all tasks             │
│  └──────┬───────┘                                      │
│         │ RMI                                           │
│         ↓                                               │
│  ┌──────────────┬──────────────┬──────────────┐       │
│  │ Worker 1     │ Worker 2     │ Worker 3     │       │
│  │ Executes     │ Executes     │ Executes     │       │
│  └──────────────┴──────────────┴──────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure
```
wordcount-distributed/
├── src/
│   ├── parser/              # Makefile parsing
│   │   ├── MakefileParser.java
│   │   ├── Task.java
│   │   ├── TaskStatus.java
│   │   ├── Token.java
│   │   └── TokenCode.java
│   ├── scheduler/           # Task scheduling
│   │   ├── Main.java
│   │   ├── TaskScheduler.java
│   │   └── Makefile
│   ├── network/             # RMI communication
│   │   ├── master/
│   │   │   └── MasterCoordinator.java
│   │   └── worker/
│   │       ├── WorkerNode.java
│   │       ├── WorkerInterface.java
│   │       └── WorkerImpl.java
│   └── cluster/             # Cluster management
│       ├── ComputeNode.java
│       ├── NodeStatus.java
│       └── ClusterManager.java
├── deploy/                  # Deployment scripts
│   ├── setup.sh
│   └── run_distributed.sh
├── test/                    # Test files
│   ├── wordcount.c
│   └── generate_data.sh
└── docs/                    # Documentation
    └── ARCHITECTURE.md
```

## 🚀 Quick Start

### Prerequisites

- Java 8+
- GCC compiler
- Grid5000 access (or local for testing)

### Setup
```bash
# Compile everything
bash deploy/setup.sh
```

### Local Testing (without Grid5000)
```bash
# Terminal 1 - Start worker
java -cp bin network.worker.WorkerNode localhost

# Terminal 2 - Run master
java -cp bin scheduler.Main "[localhost]"
```

### Grid5000 Deployment
```bash
# 1. Reserve nodes
oarsub -I -l nodes=5,walltime=1:00:00

# 2. Deploy and run
bash deploy/run_distributed.sh
```

## 📊 Example Output
```
[PARSER] Successfully parsed Makefile: 6 tasks found
[SCHEDULER] Starting task execution...
[TASK count1.txt] Assigned to worker: nancy-2.grid5000.fr
[TASK count2.txt] Assigned to worker: nancy-3.grid5000.fr
...
[SCHEDULER] ✅ All tasks completed!

📊 Total word count: 75000
```

## 🛠️ Technologies

- **Java RMI** - Remote Method Invocation
- **Grid5000** - Experimental distributed infrastructure
- **GNU Make** - Dependency management

## 📖 Documentation

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture.

## 📄 License

Educational project for distributed systems course.
