from fastapi import FastAPI
from pydantic import BaseModel
from model import predict_risk

app = FastAPI()

class RequestData(BaseModel):
    ip: str
    device: str
    time: str

def score_ip(ip):
    return 1 if not ip.startswith("192.168") else 0

def score_device(device):
    return 1 if "Windows" not in device else 0

def score_time(time):
    hour = int(time.split(":")[0])
    return 1 if hour < 6 or hour > 23 else 0

@app.post("/predict")
def predict(data: RequestData):

    ip_s = score_ip(data.ip)
    dev_s = score_device(data.device)
    time_s = score_time(data.time)

    risk = predict_risk(ip_s, dev_s, time_s)

    return {
        "risk_score": risk,
        "status": "fraud" if risk == 1 else "safe"
    }
