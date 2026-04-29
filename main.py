from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import requests
import pymysql

app = FastAPI()

# تحميل الموديل
model = joblib.load("model.pkl")

# -------- MySQL Connection --------
def get_db():
    return pymysql.connect(
        host="localhost",
        user="me",
        password="11223344mmddmM@@m",
        database="detect_db",
        cursorclass=pymysql.cursors.DictCursor
    )


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


# =========================
# 🔐 Trusted IP
# =========================
def load_trusted():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT ip FROM trusted_ips")
        return [row["ip"] for row in cur.fetchall()]


@app.get("/ips")
def get_ips():
    return load_trusted()


@app.post("/add-ip")
def add_ip(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("INSERT IGNORE INTO trusted_ips (ip) VALUES (%s)", (data.get("ip"),))
        db.commit()
    return {"message": "IP added"}


@app.post("/delete-ip")
def delete_ip(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM trusted_ips WHERE ip=%s", (data.get("ip"),))
        db.commit()
    return {"message": "IP removed"}


# =========================
# 🌍 Allowed Countries
# =========================
def load_countries():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT country FROM allowed_countries")
        return [row["country"] for row in cur.fetchall()]


@app.get("/countries")
def get_countries():
    return load_countries()


@app.post("/add-country")
def add_country(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("INSERT IGNORE INTO allowed_countries (country) VALUES (%s)", (data.get("country"),))
        db.commit()
    return {"message": "Country added"}


@app.post("/delete-country")
def delete_country(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM allowed_countries WHERE country=%s", (data.get("country"),))
        db.commit()
    return {"message": "Country removed"}


# =========================
# 🚫 Blocked Countries
# =========================
def load_blocked():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT country FROM blocked_countries")
        return [row["country"] for row in cur.fetchall()]


@app.get("/blocked-countries")
def get_blocked():
    return load_blocked()


@app.post("/add-block")
def add_block(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("INSERT IGNORE INTO blocked_countries (country) VALUES (%s)", (data.get("country"),))
        db.commit()
    return {"message": "Blocked added"}


@app.post("/delete-block")
def delete_block(data: dict):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM blocked_countries WHERE country=%s", (data.get("country"),))
        db.commit()
    return {"message": "Blocked removed"}


# =========================
# 🔍 Prediction
# =========================
@app.post("/predict")
def predict(data: RequestData):

    risk = 0

    geo = get_geo(data.ip)
    country = geo["country"]
    region = geo["region"]

    # 🚫 Block Check
    blocked = load_blocked()
    if country in blocked:
        return {
            "status": "blocked",
            "risk_score": 999,
            "country": country,
            "region": region
        }

    # 🔐 Trusted
    trusted = load_trusted()
    if data.ip in trusted:
        if country == "Kuwait":
            risk -= 3
        elif country == "United States":
            risk -= 2
        else:
            risk -= 1

    # 🌍 Allowed
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
