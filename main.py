from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import requests

app = FastAPI()

model = joblib.load("model.pkl")


# -------- Request --------
class RequestData(BaseModel):
    ip: str
    device: str
    time: str


# -------- GeoIP --------
def get_geo(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        res = requests.get(url).json()

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


# -------- Prediction --------
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    # 🧠 GeoIP
    geo = get_geo(data.ip)
    country = geo["country"]
    region = geo["region"]

    # 🟢 Allow rules
    if country == "Kuwait":
        risk -= 2

    elif country == "United States":
        if "Florida" in region or "New York" in region:
            risk -= 1
        else:
            risk += 2
    else:
        risk += 2

    # 🧠 Time rule
    hour = int(data.time)
    if hour < 5:
        risk += 1

    # 🧠 Device rule
    if "windows" in data.device.lower() or "iphone" in data.device.lower():
        risk -= 1

    # 🤖 AI
    X = [[
        encode_ip(data.ip),
        encode_device(data.device),
        encode_time(data.time)
    ]]

    model_result = model.predict(X)[0]
    risk += int(model_result)

    # 🎯 Final decision
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
