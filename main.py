from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import requests
import json
import os

app = FastAPI()

# تحميل الموديل
model = joblib.load("model.pkl")

# ملفات التخزين
TRUSTED_FILE = "trusted_ips.json"
COUNTRIES_FILE = "allowed_countries.json"


# -------- Load / Save Trusted IPs --------
def load_trusted():
    if not os.path.exists(TRUSTED_FILE):
        return []
    with open(TRUSTED_FILE, "r") as f:
        return json.load(f)


def save_trusted(data):
    with open(TRUSTED_FILE, "w") as f:
        json.dump(data, f)


# -------- Load / Save Countries --------
def load_countries():
    if not os.path.exists(COUNTRIES_FILE):
        return ["Kuwait", "United States"]  # default
    with open(COUNTRIES_FILE, "r") as f:
        return json.load(f)


def save_countries(data):
    with open(COUNTRIES_FILE, "w") as f:
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


# -------- Health --------
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running 🚀"}


# -------- Trusted IP APIs --------
@app.get("/ips")
def get_ips():
    return load_trusted()


@app.post("/add-ip")
def add_ip(data: dict):
    ip = data.get("ip")

    trusted = load_trusted()

    if ip and ip not in trusted:
        trusted.append(ip)
        save_trusted(trusted)

    return {"trusted_ips": trusted}


@app.post("/delete-ip")
def delete_ip(data: dict):
    ip = data.get("ip")

    trusted = load_trusted()

    if ip in trusted:
        trusted.remove(ip)
        save_trusted(trusted)

    return {"trusted_ips": trusted}


# -------- Countries APIs --------
@app.get("/countries")
def get_countries():
    return load_countries()


@app.post("/add-country")
def add_country(data: dict):
    country = data.get("country")

    countries = load_countries()

    if country and country not in countries:
        countries.append(country)
        save_countries(countries)

    return {"countries": countries}


@app.post("/delete-country")
def delete_country(data: dict):
    country = data.get("country")

    countries = load_countries()

    if country in countries:
        countries.remove(country)
        save_countries(countries)

    return {"countries": countries}


# -------- Prediction --------
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    # 🌍 Geo
    geo = get_geo(data.ip)
    country = geo["country"]
    region = geo["region"]

    # 🔐 Trusted IP (Smart)
    trusted_ips = load_trusted()
    if data.ip in trusted_ips:
        if country == "Kuwait":
            risk -= 3
        elif country == "United States":
            risk -= 2
        else:
            risk -= 1

    # 🌍 Allowed Countries
    allowed_countries = load_countries()

    if country in allowed_countries:
        risk -= 2
    else:
        risk += 2

    # 🕒 Time
    hour = int(data.time)
    if hour < 5:
        risk += 2

    # 💻 Device
    device_lower = data.device.lower()
    if "windows" in device_lower or "iphone" in device_lower:
        risk -= 1

    # 🤖 AI Model
    X = [[
        encode_ip(data.ip),
        encode_device(data.device),
        encode_time(data.time)
    ]]

    model_result = model.predict(X)[0]
    risk += int(model_result)

    # 🎯 Final Decision
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
