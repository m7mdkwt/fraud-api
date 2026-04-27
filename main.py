from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import requests
import json
import os

app = FastAPI()

# تحميل الموديل
model = joblib.load("model.pkl")

# ملف تخزين IPs
TRUSTED_FILE = "trusted_ips.json"


# -------- Load / Save Trusted IPs --------
def load_trusted():
    if not os.path.exists(TRUSTED_FILE):
        return []
    with open(TRUSTED_FILE, "r") as f:
        return json.load(f)


def save_trusted(data):
    with open(TRUSTED_FILE, "w") as f:
        json.dump(data, f)


# -------- Request Schema --------
class RequestData(BaseModel):
    ip: str
    device: str
    time: str


# -------- GeoIP --------
def get_geo(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        res = requests.get(url, timeout=3).json()

        return {
            "country": res.get("country", "Unknown"),
            "region": res.get("regionName", "Unknown"),
            "city": res.get("city", "Unknown")
        }
    except:
        return {
            "country": "Unknown",
            "region": "Unknown",
            "city": "Unknown"
        }


# -------- Encoding --------
def encode_ip(ip):
    return 1 if not ip.startswith("192") else 0


def encode_device(device):
    device = device.lower()

    if "windows" in device:
        return 0
    elif "iphone" in device:
        return 1
    elif "android" in device:
        return 2
    else:
        return 3


def encode_time(hour):
    hour = int(hour)
    return 1 if hour < 6 else 0


# -------- Health Check --------
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running 🚀"}


# -------- Add Trusted IP --------
@app.post("/add-ip")
def add_ip(data: dict):
    ip = data.get("ip")

    if not ip:
        return {"error": "IP is required"}

    trusted = load_trusted()

    if ip not in trusted:
        trusted.append(ip)
        save_trusted(trusted)

    return {"message": "IP added", "trusted_ips": trusted}


# -------- Get Trusted IPs --------
@app.get("/ips")
def get_ips():
    return load_trusted()


# -------- Delete Trusted IP --------
@app.post("/delete-ip")
def delete_ip(data: dict):
    ip = data.get("ip")

    trusted = load_trusted()

    if ip in trusted:
        trusted.remove(ip)
        save_trusted(trusted)

    return {"message": "IP removed", "trusted_ips": trusted}


# -------- Prediction --------
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    # 🧠 GeoIP
    geo = get_geo(data.ip)
    country = geo["country"]
    region = geo["region"]

    # 🔐 Trusted IPs (أولوية قصوى)
    trusted_ips = load_trusted()
   # 🔐 Smart Trusted IP
trusted_ips = load_trusted()

if data.ip in trusted_ips:
    risk -= 3

    # 🌍 الدولة
    if country == "Kuwait":
        risk -= 2

    elif country == "United States":
        if "Florida" in region or "New York" in region:
            risk -= 1
        else:
            risk += 2
    else:
        risk += 2

    # 🕒 الوقت
    hour = int(data.time)
    if hour < 5:
        risk += 2

    # 💻 الجهاز
    if "windows" in data.device.lower() or "iphone" in data.device.lower():
        risk -= 1

    # 🤖 AI Model
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
        "status": status,
        "risk_score": int(risk),
        "country": country,
        "region": region
    }
