# tcp-client-server-simulation

A Python simulation of a TCP server offering multiple services (FILE, CALC, DB)
to multiple concurrent clients. Demonstrates how a real server handles client
requests, manages a bounded queue, and drops overflow requests — with full stats
tracking.

---

## 📌 About

This project simulates a real TCP client-server system built with Python using
actual sockets, real threading, and real services — meaning the server genuinely
processes every request it receives, not just pretends to.

What makes it a **simulation** is:
- The client sends requests **randomly** based on a configurable time interval
- The server **artificially delays** processing each request (random delay in a
  chosen range) to simulate real workload
- The server processes **one request at a time** (intentionally) to observe how
  requests pile up in the queue and how the server handles overflow — something
  that wouldn't happen in a real production server

> With small changes, this simulation can be turned into a fully functional
> real-world server ready for production use.

---

## ⚙️ How It Works

### Server
- Listens on `127.0.0.1:12345`
- Accepts multiple clients, each handled in a separate thread
- Places incoming requests into a **bounded queue**
- Processes requests **one by one** with a simulated delay (1–3 seconds)
- **Drops requests** when the queue is full and notifies the client
- Stops automatically after the configured simulation time
- Prints live stats after every processed request

### Client
- Connects to the server and sends **random requests** from `requests.txt`
- Waits a random interval (2–5 seconds) between each request
- Displays the server's response or drop notification
- Prints a final summary (total sent / dropped / successful) at the end

---

## 🛠️ Services

| Request | Format | Example |
|---|---|---|
| File retrieval | `GET <filename>` | `GET file1.txt` |
| Calculator | `CALC <num> <op> <num>` | `CALC 15 / 3` |
| Database lookup | `DB GET <id>` | `DB GET 2` |

---

## 📁 Project Structure
```
tcp-client-server-simulation/
│
├── Server.py          # Server logic (queue, threading, services)
├── Client.py          # Client logic (random requests, retry, stats)
├── database.json      # Student database used by DB GET service
├── requests.txt       # List of requests the client randomly picks from
└── files/
    ├── file1.txt
    ├── file2.txt
    └── file3.txt
```

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/tcp-client-server-simulation.git
cd tcp-client-server-simulation
```

### 2. Start the server
```bash
python Server.py
```
You will be asked to enter:
- **Queue size** → max number of requests the server can hold at once
- **Simulation time** → how long the server runs (in seconds)

### 3. Start one or more clients (in separate terminals)
```bash
python Client.py
```
You will be asked to enter a client name.

> You can open **multiple terminals** and run several clients at the same time
> to see how the server manages the queue and drops requests under load.

---

## 📊 Stats

### Server (printed live and at the end)
- Total requests received
- Total requests processed
- Total requests dropped

### Client (printed at the end)
- Total requests sent
- Total dropped (server was full)
- Total successful

---

## 💡 Key Concepts Demonstrated

- TCP socket programming
- Multithreading with `threading` module
- Bounded queue management with `queue.Queue`
- Request dropping and overflow handling
- Simulation of server load and client behavior
- Real service implementation (file I/O, arithmetic, JSON database)

---

## 🔧 Requirements

- Python 3.x
- No external libraries required (standard library only)

---

## 👨‍💻 Author

**Massil**  
Computer Science Student — M1  
University of Biskra
