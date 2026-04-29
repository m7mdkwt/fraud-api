from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import joblib
import requests
import os

app = FastAPI()

# 🔥 DATABASE URL (ضع الباسورد)
DATABASE_URL = "postgresql://postgres:11223344mmddmM@@@db.nuocuctzsidctyohecep.supabase.co:5432/postgres"

# تحميل الموديل
model = joblib.load("model.pkl")


# -------- DB --------
def get_db():
    return psycopg2.connect(DATABASE_URL)


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
            "region": res.get("regionName", "Unknown")
        }
    except:
        return {"country": "Unknown", "region": "Unknown"}


# =========================
# 🔐 Trusted IP
# =========================
def load_trusted():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT ip FROM trusted_ips")
    data = cur.fetchall()
    cur.close()
    db.close()
    return [x[0] for x in data]


@app.post("/add-ip")
def add_ip(data: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO trusted_ips (ip) VALUES (%s) ON CONFLICT DO NOTHING", (data["ip"],))
    db.commit()
    cur.close()
    db.close()
    return {"msg": "added"}


@app.post("/delete-ip")
def delete_ip(data: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM trusted_ips WHERE ip=%s", (data["ip"],))
    db.commit()
    cur.close()
    db.close()
    return {"msg": "deleted"}


# =========================
# 🌍 Countries
# =========================
def load_countries():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT country FROM allowed_countries")
    data = cur.fetchall()
    cur.close()
    db.close()
    return [x[0] for x in data]


def load_blocked():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT country FROM blocked_countries")
    data = cur.fetchall()
    cur.close()
    db.close()
    return [x[0] for x in data]


# =========================
# 🔍 Prediction
# =========================
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    geo = get_geo(data.ip)
    country = geo["country"]
    region = geo["region"]

    # 🚫 Block
    if country in load_blocked():
        return {
            "status": "blocked",
            "country": country,
            "region": region
        }

    # 🔐 Trusted
    if data.ip in load_trusted():
        risk -= 3

    # 🌍 Allowed
    if country in load_countries():
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
    X = [[1, 1, 1]]
    risk += int(model.predict(X)[0])

    # 🎯 Result
    if risk <= 0:
        status = "safe"
    elif risk == 1:
        status = "medium"
    else:
        status = "fraud"

    return {
        "status": status,
        "country": country,
        "region": region
    }
