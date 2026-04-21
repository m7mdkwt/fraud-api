from sklearn.tree import DecisionTreeClassifier
import numpy as np

# بيانات تدريب بسيطة
X = [
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 1],
]

y = [0, 1, 0, 1, 0]

model = DecisionTreeClassifier()
model.fit(X, y)

def predict_risk(ip_score, device_score, time_score):
    result = model.predict([[ip_score, device_score, time_score]])
    return int(result[0])