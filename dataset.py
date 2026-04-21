import pandas as pd

data = [
    # ip_new, device_unknown, odd_time, fraud
    [0, 0, 0, 0],  # normal user
    [1, 0, 0, 1],  # suspicious IP
    [0, 1, 0, 0],  # new device but safe
    [1, 1, 1, 1],  # fraud pattern
    [0, 0, 1, 0],  # late login but safe
    [1, 0, 1, 1],  # suspicious time + IP
    [0, 1, 1, 1],  # risky behavior
    [1, 1, 0, 1],  # mixed risk
]

df = pd.DataFrame(data, columns=["ip", "device", "time", "fraud"])
print(df)