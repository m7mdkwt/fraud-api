import pandas as pd
import random

data = []

for _ in range(120):
    ip = random.choice(["1.2.3.4", "192.168.1.5", "8.8.8.8"])
    device = random.choice(["Windows", "Linux", "Mac"])
    time = random.randint(0, 23)

    data.append([ip, device, time])

df = pd.DataFrame(data, columns=["ip", "device", "time"])

# 💾 هذا أهم سطر
df.to_csv("logs.csv", index=False)

print("✅ logs.csv created successfully")
