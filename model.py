from sklearn.tree import DecisionTreeClassifier
import numpy as np

# بيانات تدريب
X = [
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 1],
    [1, 0, 1],
    [0, 1, 1],
    [1, 1, 0],
]

y = [0, 1, 0, 1, 0, 1, 1, 1]

model = DecisionTreeClassifier()
model.fit(X, y)

def predict_risk(ip, device, time):
    return int(model.predict([[ip, device, time]])[0])
