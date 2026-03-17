import socket
import threading
import queue
import time
import random
import os
import json

# =====================
# إعدادات الخادم
# =====================
HOST = '127.0.0.1'
PORT = 12345
SERVER_PROCESS_TIME = (1, 3)
REQUEST_SIZE = 4096

# حجم الطابور يدوياً
while True:
    try:
        QUEUE_SIZE = int(input("Enter queue size: "))
        if QUEUE_SIZE > 0:
            break
        print("❌ Please enter a number greater than 0.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

# وقت المحاكاة يدوياً
while True:
    try:
        SIMULATION_TIME = int(input("Enter simulation time (seconds): "))
        if SIMULATION_TIME > 0:
            break
        print("❌ Please enter a number greater than 0.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

# =====================
# تحميل قاعدة البيانات
# =====================
try:
    with open("database.json", "r") as f:
        database = json.load(f)
    print("[SERVER] ✅ Database loaded successfully.")
except FileNotFoundError:
    print("[SERVER] ❌ database.json not found!")
    exit()

# =====================
# إحصائيات
# =====================
stats = {
    "received": 0,
    "processed": 0,
    "dropped": 0
}

# =====================
# الطابور والحالة
# =====================
server_queue = queue.Queue(maxsize=QUEUE_SIZE)
server_busy = False
server_busy_lock = threading.Lock()
simulation_running = True

# =====================
# معالج الطلبات
# =====================
def handle_request(request):
    parts = request.strip().split()

    if len(parts) == 2 and parts[0] == "GET":
        filename = parts[1]
        filepath = os.path.join("files", filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            return f"✅ FILE [{filename}]:\n{content}"
        else:
            return f"❌ ERROR: File '{filename}' not found."

    elif len(parts) == 4 and parts[0] == "CALC":
        try:
            a = float(parts[1])
            op = parts[2]
            b = float(parts[3])
            if op == "+":   result = a + b
            elif op == "-": result = a - b
            elif op == "*": result = a * b
            elif op == "/":
                if b == 0:
                    return "❌ ERROR: Division by zero."
                result = a / b
            else:
                return f"❌ ERROR: Unknown operator '{op}'."
            return f"✅ CALC [{a} {op} {b}] = {result}"
        except:
            return "❌ ERROR: Invalid CALC format."

    elif len(parts) == 3 and parts[0] == "DB" and parts[1] == "GET":
        sid = parts[2]
        if sid in database:
            s = database[sid]
            return f"✅ DB [Student {sid}]: Name={s['name']} | Age={s['age']} | Major={s['major']}"
        else:
            return f"❌ ERROR: Student ID '{sid}' not found."

    else:
        return "❌ ERROR: Unknown request. Use GET / CALC / DB GET"

# =====================
# معالجة الطابور
# =====================
def process_queue():
    global server_busy

    while simulation_running:
        try:
            client_socket, request, address = server_queue.get(timeout=1)
        except queue.Empty:
            continue

        process_time = random.uniform(*SERVER_PROCESS_TIME)
        print(f"\n[SERVER] ⚙️  Processing '{request}' from {address} ({process_time:.1f}s)")
        time.sleep(process_time)

        response = handle_request(request)

        try:
            client_socket.send(response.encode())
            client_socket.close()
        except:
            pass

        stats["processed"] += 1
        print(f"[SERVER] ✅ Done: '{request}'")
        print(f"[SERVER] 📊 Received: {stats['received']} | Processed: {stats['processed']} | Dropped: {stats['dropped']} | Queue: {server_queue.qsize()}/{QUEUE_SIZE}")

        with server_busy_lock:
            if server_queue.empty():
                server_busy = False

        server_queue.task_done()

# =====================
# استقبال العملاء
# =====================
def handle_client(client_socket, address):
    global server_busy

    if not simulation_running:
        try:
            client_socket.send("❌ Simulation has ended.".encode())
        except:
            pass
        client_socket.close()
        return

    try:
        data = client_socket.recv(REQUEST_SIZE).decode().strip()
        if not data:
            client_socket.close()
            return

        stats["received"] += 1
        print(f"\n[SERVER] 📥 Request from {address}: '{data}'")

        with server_busy_lock:
            is_busy = server_busy
            if not server_busy:
                server_busy = True

        # محاولة وضع الطلب في الطابور
        try:
            server_queue.put_nowait((client_socket, data, address))
            print(f"[SERVER] 📋 Queued. Queue: {server_queue.qsize()}/{QUEUE_SIZE}")
        except queue.Full:
            stats["dropped"] += 1
            print(f"[SERVER] ❌ Queue Full! Dropped: '{data}' from {address}")
            try:
                client_socket.send("❌ DROPPED: Queue is full. Try again later.".encode())
            except:
                pass
            client_socket.close()

    except ConnectionResetError:
        print(f"[SERVER] ⚠️  Client {address} disconnected.")
        client_socket.close()

# =====================
# مؤقت المحاكاة
# =====================
def simulation_timer():
    global simulation_running

    time.sleep(SIMULATION_TIME)
    simulation_running = False

    print("\n\n" + "="*50)
    print("       ⏰ SIMULATION TIME IS UP!")
    print("="*50)
    print(f"  Total Received  : {stats['received']}")
    print(f"  Total Processed : {stats['processed']}")
    print(f"  Total Dropped   : {stats['dropped']}")
    print("="*50)
    print("[SERVER] 🔴 Server stopped.")
    time.sleep(2)
    os._exit(0)

# =====================
# تشغيل الخادم
# =====================

# thread معالجة الطابور
processor = threading.Thread(target=process_queue, daemon=True)
processor.start()

# thread المؤقت
timer = threading.Thread(target=simulation_timer, daemon=True)
timer.start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(QUEUE_SIZE + 1)

print("\n" + "="*50)
print("       🖥️  SERVER IS RUNNING")
print(f"       📍 {HOST}:{PORT}")
print(f"       📋 Queue Size: {QUEUE_SIZE}")
print(f"       ⏱️  Simulation Time: {SIMULATION_TIME}s")
print(f"       ⚙️  Process Time: {SERVER_PROCESS_TIME[0]}s - {SERVER_PROCESS_TIME[1]}s")
print("="*50)
print("  📄 GET file1.txt / file2.txt / file3.txt")
print("  🔢 CALC <num> <op> <num>  → CALC 15 + 30")
print("  🎓 DB GET <id>            → DB GET 3")
print("="*50 + "\n")

try:
    while simulation_running:
        server_socket.settimeout(1)
        try:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.daemon = True
            thread.start()
        except socket.timeout:
            continue
except KeyboardInterrupt:
    print("[SERVER] 🔴 Stopped manually.")
finally:
    server_socket.close()