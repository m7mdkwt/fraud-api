import pandas as pd
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv("logs.csv")

def encode_device(d):
    return {
        "Windows": 0,
        "Mac": 1,
        "Linux": 2,
        "Android": 3,
        "iPhone": 4
    }[d]

def encode_ip(ip):
    return 1 if not ip.startswith("192") else 0

def encode_time(t):
    hour = int(t.split(":")[0])
    return 1 if hour < 6 or hour > 23 else 0

X = []
y = []

for _, row in df.iterrows():
    X.append([
        encode_ip(row["ip"]),
        encode_device(row["device"]),
        encode_time(row["time"])
    ])
    y.append(row["fraud"])

model = DecisionTreeClassifier()
model.fit(X, y)

print("Model trained successfully 🚀")