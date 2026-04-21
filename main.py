from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# تحميل الموديل
model = joblib.load("model.pkl")

class RequestData(BaseModel):
    ip: str
    device: str
    time: str

def encode_device(d):
    return {
        "Windows": 0,
        "Mac": 1,
        "Linux": 2,
        "Android": 3,
        "iPhone": 4
    }.get(d, 0)

def encode_ip(ip):
    return 1 if not ip.startswith("192") else 0

def encode_time(t):
    hour = int(t.split(":")[0])
    return 1 if hour < 6 or hour > 23 else 0

@app.post("/predict")
def predict(data: RequestData):

    X = [[
        encode_ip(data.ip),
        encode_device(data.device),
        encode_time(data.time)
    ]]

    result = model.predict(X)[0]

    return {
        "risk_score": int(result),
        "status": "fraud" if result == 1 else "safe"
    }
