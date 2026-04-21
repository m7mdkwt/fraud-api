from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class RequestData(BaseModel):
    ip: str
    device: str
    time: str

@app.get("/")
def home():
    return {"message": "Fraud Detection API Running 🚀"}

@app.post("/predict")
def predict(data: RequestData):
    risk = 0

    # rule 1: IP مختلف
    if not data.ip.startswith("192.168"):
        risk += 40

    # rule 2: جهاز غريب
    if "Windows" not in data.device:
        risk += 20

    # rule 3: وقت غريب
    hour = int(data.time.split(":")[0])
    if hour < 6 or hour > 23:
        risk += 30

    # simulate AI
    risk += random.randint(0, 20)

    if risk < 40:
        status = "low"
    elif risk < 70:
        status = "medium"
    else:
        status = "high"

    return {
        "risk_score": risk,
        "status": status
    }