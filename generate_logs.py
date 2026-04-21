import random
import pandas as pd
from datetime import datetime, timedelta

def random_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

def random_device():
    return random.choice(["Windows", "Mac", "Linux", "Android", "iPhone"])

def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

def label(ip, device, time):
    score = 0

    if not ip.startswith("192"):  # simulate unknown IP
        score += 1
    if device in ["Linux", "Android"]:
        score += 1
    hour = int(time.split(":")[0])
    if hour < 6 or hour > 23:
        score += 1

    return 1 if score >= 2 else 0  # fraud = 1

data = []

for _ in range(120):  # 120 records
    ip = random_ip()
    device = random_device()
    time = random_time()
    fraud = label(ip, device, time)

    data.append([ip, device, time, fraud])

df = pd.DataFrame(data, columns=["ip", "device", "time", "fraud"])
df.to_csv("logs.csv", index=False)

print("Dataset generated: logs.csv")