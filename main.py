from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# تحميل الموديل
model = joblib.load("model.pkl")


# -------- Health Check --------
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running 🚀"}


# -------- Request Schema --------
class RequestData(BaseModel):
    ip: str
    device: str
    time: str   # نرسل فقط الساعة (H)


# -------- Encoding --------
def encode_ip(ip):
    return 1 if not ip.startswith("192") else 0


def encode_device(device):
    device = device.lower()

    if "windows" in device:
        return 0
    elif "mac" in device:
        return 1
    elif "linux" in device:
        return 2
    elif "android" in device:
        return 3
    elif "iphone" in device:
        return 4
    else:
        return 5


def encode_time(hour):
    hour = int(hour)
    return 1 if hour < 6 else 0


# -------- Prediction --------
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    # 🧠 Rule 1: IP داخلي = آمن
    if data.ip.startswith("192"):
        risk -= 1

    # 🧠 Rule 2: وقت مشبوه (ليل)
    hour = int(data.time)
    if hour < 5:
        risk += 1

    # 🧠 Rule 3: جهاز طبيعي
    if "windows" in data.device.lower() or "iphone" in data.device.lower():
        risk -= 1

    # 🤖 AI Prediction
    X = [[
        encode_ip(data.ip),
        encode_device(data.device),
        encode_time(data.time)
    ]]

    model_result = model.predict(X)[0]

    risk += int(model_result)

    # 🎯 القرار النهائي
    if risk <= 0:
        status = "safe"
    elif risk == 1:
        status = "medium"
    else:
        status = "fraud"

    return {
        "risk_score": int(risk),
        "status": status
    }
