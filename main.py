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
BLOCKED_FILE = "blocked_countries.json"


# -------- Load / Save --------
def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r") as f:
        return json.load(f)


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


# -------- Trusted --------
def load_trusted():
    return load_json(TRUSTED_FILE, [])


def save_trusted(data):
    save_json(TRUSTED_FILE, data)


# -------- Allowed Countries --------
def load_countries():
    return load_json(COUNTRIES_FILE, ["Kuwait", "United States"])


def save_countries(data):
    save_json(COUNTRIES_FILE, data)


# -------- Blocked Countries --------
def load_blocked():
    return load_json(BLOCKED_FILE, [])


def save_blocked(data):
    save_json(BLOCKED_FILE, data)


# -------- Request --------
class RequestData(BaseModel):
    ip: str
    device: str
    time: str


# -------- Geo --------
def get_geo(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return {
            "country": res.get("country", "Unknown"),
            "region": res.get("regionName", "Unknown"),
            "city": res.get("city", "Unknown")
        }
    except:
        return {"country": "Unknown", "region": "Unknown", "city": "Unknown"}


# -------- Encoding --------
def encode_ip(ip):
    return 1 if not ip.startswith("192") else 0


def encode_device(device):
    d = device.lower()
    if "windows" in d:
        return 0
    elif "iphone" in d:
        return 1
    elif "android" in d:
        return 2
    return 3


def encode_time(hour):
    return 1 if int(hour) < 6 else 0


# -------- Health --------
@app.get("/")
def home():
    return {"message": "Fraud API Running 🚀"}


# -------- Trusted IP APIs --------
@app.get("/ips")
def get_ips():
    return load_trusted()


@app.post("/add-ip")
def add_ip(data: dict):
    ips = load_trusted()
    ip = data.get("ip")

    if ip and ip not in ips:
        ips.append(ip)
        save_trusted(ips)

    return {"trusted_ips": ips}


@app.post("/delete-ip")
def delete_ip(data: dict):
    ips = load_trusted()
    ip = data.get("ip")

    if ip in ips:
        ips.remove(ip)
        save_trusted(ips)

    return {"trusted_ips": ips}


# -------- Allowed Countries APIs --------
@app.get("/countries")
def get_countries():
    return load_countries()


@app.post("/add-country")
def add_country(data: dict):
    countries = load_countries()
    c = data.get("country")

    if c and c not in countries:
        countries.append(c)
        save_countries(countries)

    return {"countries": countries}


@app.post("/delete-country")
def delete_country(data: dict):
    countries = load_countries()
    c = data.get("country")

    if c in countries:
        countries.remove(c)
        save_countries(countries)

    return {"countries": countries}


# -------- Blocked Countries APIs --------
@app.get("/blocked-countries")
def get_blocked():
    return load_blocked()


@app.post("/add-block")
def add_block(data: dict):
    blocked = load_blocked()
    c = data.get("country")

    if c and c not in blocked:
        blocked.append(c)
        save_blocked(blocked)

    return {"blocked": blocked}


@app.post("/delete-block")
def delete_block(data: dict):
    blocked = load_blocked()
    c = data.get("country")

    if c in blocked:
        blocked.remove(c)
        save_blocked(blocked)

    return {"blocked": blocked}


# -------- Prediction --------
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    # 🌍 Geo
    geo = get_geo(data.ip)
    country = geo["country"]
    region = geo["region"]

    # 🚫 BLOCK CHECK (أهم شيء)
    blocked = load_blocked()
    if country in blocked:
        return {
            "status": "blocked",
            "risk_score": 999,
            "country": country,
            "region": region
        }

    # 🔐 Trusted IP
    trusted = load_trusted()
    if data.ip in trusted:
        if country == "Kuwait":
            risk -= 3
        elif country == "United States":
            risk -= 2
        else:
            risk -= 1

    # 🌍 Allowed Countries
    allowed = load_countries()
    if country in allowed:
        risk -= 2
    else:
        risk += 2

    # 🕒 Time
    if int(data.time) < 5:
        risk += 2

    # 💻 Device
    if "windows" in data.device.lower() or "iphone" in data.device.lower():
        risk -= 1

    # 🤖 AI
    X = [[
        encode_ip(data.ip),
        encode_device(data.device),
        encode_time(data.time)
    ]]

    risk += int(model.predict(X)[0])

    # 🎯 Decision
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
