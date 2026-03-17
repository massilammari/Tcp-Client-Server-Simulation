import socket
import time
import random

# =====================
# إعدادات العميل
# =====================
HOST = '127.0.0.1'
PORT = 12345
CLIENT_RETRY = 3
REQUEST_SIZE = 4096
REQUEST_INTERVAL = (2, 5)

# =====================
# تحميل الطلبات من الملف
# =====================
try:
    with open("requests.txt", "r") as f:
        REQUESTS = [line.strip() for line in f.readlines() if line.strip()]
    print(f"✅ Loaded {len(REQUESTS)} requests from requests.txt")
except FileNotFoundError:
    print("❌ requests.txt not found!")
    exit()

# =====================
# اسم العميل
# =====================
client_name = input("Enter client name: ")

# =====================
# دالة إرسال طلب واحد
# =====================
def send_request(request):
    for attempt in range(1, CLIENT_RETRY + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            s.send(request.encode())
            s.settimeout(15)
            response = s.recv(REQUEST_SIZE).decode()
            s.close()
            return response

        except ConnectionRefusedError:
            # الخادم أغلق = المحاكاة انتهت
            print(f"[{client_name}] 🔴 Server is closed. Simulation has ended.")
            return "Simulation has ended"

        except socket.timeout:
            print(f"[{client_name}] ⏰ Timeout!")
            return None

        except Exception as e:
            print(f"[{client_name}] ⚠️  Error: {e}")
            return None

    return None

# =====================
# تشغيل العميل
# =====================
print(f"\n[{client_name}] 🚀 Starting simulation...")
print(f"[{client_name}] 📋 Sending random requests every {REQUEST_INTERVAL[0]}-{REQUEST_INTERVAL[1]}s")
print("-"*50)

request_count = 0
dropped_count = 0

try:
    while True:
        wait_time = random.uniform(*REQUEST_INTERVAL)
        time.sleep(wait_time)

        request = random.choice(REQUESTS)
        request_count += 1

        print(f"\n[{client_name}] 📤 Sending [{request_count}]: {request}")

        response = send_request(request)

        if response is None:
            print(f"[{client_name}] ⚠️  No response received.")
            continue

        if "Simulation has ended" in response:
            print(f"[{client_name}] ⏰ Simulation ended. Stopping.")
            break

        elif "DROPPED" in response:
            dropped_count += 1
            print(f"[{client_name}] ❌ {response}")

        else:
            print(f"[{client_name}] 📩 Response: {response}")

        print("-"*50)

except KeyboardInterrupt:
    print(f"\n[{client_name}] 🔴 Stopped manually.")

finally:
    print("\n" + "="*50)
    print(f"  [{client_name}] 📊 FINAL STATS")
    print("="*50)
    print(f"  Total Sent    : {request_count}")
    print(f"  Dropped       : {dropped_count}")
    print(f"  Successful    : {request_count - dropped_count}")
    print("="*50)