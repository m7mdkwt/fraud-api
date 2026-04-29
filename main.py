from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import requests

app = FastAPI()

# 🔥 DB
DATABASE_URL = "postgresql://postgres:11223344mmddmM%40%40@db.nuocuctzsidctyohecep.supabase.co:5432/postgres"

def get_db():
    return psycopg2.connect(DATABASE_URL)

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
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT ip FROM trusted_ips")
    data = [row[0] for row in cur.fetchall()]
    cur.close()
    db.close()
    return data

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
@app.get("/countries")
def get_countries():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT country FROM allowed_countries")
    data = [row[0] for row in cur.fetchall()]
    cur.close()
    db.close()
    return data

@app.post("/add-country")
def add_country(data: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO allowed_countries (country) VALUES (%s) ON CONFLICT DO NOTHING", (data["country"],))
    db.commit()
    cur.close()
    db.close()
    return {"msg": "added"}

@app.post("/delete-country")
def delete_country(data: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM allowed_countries WHERE country=%s", (data["country"],))
    db.commit()
    cur.close()
    db.close()
    return {"msg": "deleted"}

# =========================
# 🚫 Blocked Countries
# =========================
@app.get("/blocked-countries")
def get_blocked():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT country FROM blocked_countries")
    data = [row[0] for row in cur.fetchall()]
    cur.close()
    db.close()
    return data

@app.post("/add-block")
def add_block(data: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO blocked_countries (country) VALUES (%s) ON CONFLICT DO NOTHING", (data["country"],))
    db.commit()
    cur.close()
    db.close()
    return {"msg": "added"}

@app.post("/delete-block")
def delete_block(data: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM blocked_countries WHERE country=%s", (data["country"],))
    db.commit()
    cur.close()
    db.close()
    return {"msg": "deleted"}

# =========================
# 🔍 Prediction
# =========================
@app.post("/predict")
def predict(data: RequestData):

    geo = requests.get(f"http://ip-api.com/json/{data.ip}").json()
    country = geo.get("country", "Unknown")
    region = geo.get("regionName", "Unknown")

    # 🚫 Block
    blocked = get_blocked()
    if country in blocked:
        return {"status": "blocked", "country": country}

    # 🌍 Allowed
    allowed = get_countries()

    if country in allowed:
        status = "safe"
    else:
        status = "fraud"

    return {
        "status": status,
        "country": country,
        "region": region
    }
