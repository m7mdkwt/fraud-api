from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import requests

app = FastAPI()

# 🔥 DATABASE
DATABASE_URL = "postgresql://postgres:11223344mmddmM%40%40@db.nuocuctzsidctyohecep.supabase.co:5432/postgres"


# -------- DB Helper --------
def query_db(query, params=None):
    try:
        db = psycopg2.connect(DATABASE_URL)
        cur = db.cursor()
        cur.execute(query, params or ())
        data = cur.fetchall() if cur.description else None
        db.commit()
        cur.close()
        db.close()
        return data
    except Exception as e:
        print("DB ERROR:", e)
        return []


# -------- Request --------
class RequestData(BaseModel):
    ip: str
    device: str
    time: str


# -------- Home --------
@app.get("/")
def home():
    return {"message": "API Running 🚀"}


# =========================
# 🔐 Trusted IP
# =========================
@app.get("/ips")
def get_ips():
    data = query_db("SELECT ip FROM trusted_ips")
    return [x[0] for x in data]


@app.post("/add-ip")
def add_ip(data: dict):
    query_db("INSERT INTO trusted_ips (ip) VALUES (%s) ON CONFLICT DO NOTHING", (data["ip"],))
    return {"msg": "added"}


@app.post("/delete-ip")
def delete_ip(data: dict):
    query_db("DELETE FROM trusted_ips WHERE ip=%s", (data["ip"],))
    return {"msg": "deleted"}


# =========================
# 🌍 Countries
# =========================
@app.get("/countries")
def get_countries():
    data = query_db("SELECT country FROM allowed_countries")
    return [x[0] for x in data]


@app.post("/add-country")
def add_country(data: dict):
    query_db("INSERT INTO allowed_countries (country) VALUES (%s) ON CONFLICT DO NOTHING", (data["country"],))
    return {"msg": "added"}


@app.post("/delete-country")
def delete_country(data: dict):
    query_db("DELETE FROM allowed_countries WHERE country=%s", (data["country"],))
    return {"msg": "deleted"}


# =========================
# 🚫 Blocked Countries
# =========================
@app.get("/blocked-countries")
def get_blocked():
    data = query_db("SELECT country FROM blocked_countries")
    return [x[0] for x in data]


@app.post("/add-block")
def add_block(data: dict):
    query_db("INSERT INTO blocked_countries (country) VALUES (%s) ON CONFLICT DO NOTHING", (data["country"],))
    return {"msg": "added"}


@app.post("/delete-block")
def delete_block(data: dict):
    query_db("DELETE FROM blocked_countries WHERE country=%s", (data["country"],))
    return {"msg": "deleted"}


# =========================
# 🔍 Prediction
# =========================
@app.post("/predict")
def predict(data: RequestData):

    # 🌍 Geo (مع timeout)
    try:
        geo = requests.get(f"http://ip-api.com/json/{data.ip}", timeout=3).json()
    except:
        geo = {}

    country = geo.get("country", "Unknown")
    region = geo.get("regionName", "Unknown")

    blocked = get_blocked()
    allowed = get_countries()

    if country in blocked:
        return {"status": "blocked", "country": country}

    if country in allowed:
        status = "safe"
    else:
        status = "fraud"

    return {
        "status": status,
        "country": country,
        "region": region
    }
