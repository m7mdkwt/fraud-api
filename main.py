from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import requests
from dotenv import load_dotenv
import os

app = FastAPI()

# 🔥 تحميل .env
load_dotenv()

# 🔥 DATABASE URL (من .env)
DATABASE_URL = os.getenv("DATABASE_URL")


# -------- DB --------
def get_db():
    return psycopg2.connect(DATABASE_URL)


def safe_close(cur=None, db=None):
    try:
        if cur:
            cur.close()
        if db:
            db.close()
    except:
        pass


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
# 🔐 Trusted IPs
# =========================

@app.get("/ips")
def get_ips():
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT ip FROM trusted_ips")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


@app.post("/add-ip")
def add_ip(data: dict):
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute(
            "INSERT INTO trusted_ips (ip) VALUES (%s) ON CONFLICT (ip) DO NOTHING",
            (data["ip"],)
        )
        db.commit()

        if cur.rowcount == 0:
            return {"status": "exists", "message": "IP already exists"}

        return {"status": "success", "message": "IP added"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


@app.post("/delete-ip")
def delete_ip(data: dict):
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("DELETE FROM trusted_ips WHERE ip=%s", (data["ip"],))
        db.commit()

        return {"status": "success", "message": "IP deleted"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


# =========================
# 🌍 Allowed Countries
# =========================

@app.get("/countries")
def get_countries():
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT country FROM allowed_countries")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


@app.post("/add-country")
def add_country(data: dict):
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute(
            "INSERT INTO allowed_countries (country) VALUES (%s) ON CONFLICT (country) DO NOTHING",
            (data["country"],)
        )
        db.commit()

        if cur.rowcount == 0:
            return {"status": "exists", "message": "Country already exists"}

        return {"status": "success", "message": "Country added"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


@app.post("/delete-country")
def delete_country(data: dict):
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("DELETE FROM allowed_countries WHERE country=%s", (data["country"],))
        db.commit()

        return {"status": "success", "message": "Country removed"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


# =========================
# 🚫 Blocked Countries
# =========================

@app.get("/blocked-countries")
def get_blocked():
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT country FROM blocked_countries")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


@app.post("/add-block")
def add_block(data: dict):
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute(
            "INSERT INTO blocked_countries (country) VALUES (%s) ON CONFLICT (country) DO NOTHING",
            (data["country"],)
        )
        db.commit()

        if cur.rowcount == 0:
            return {"status": "exists", "message": "Already blocked"}

        return {"status": "success", "message": "Country blocked"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


@app.post("/delete-block")
def delete_block(data: dict):
    cur = None
    db = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("DELETE FROM blocked_countries WHERE country=%s", (data["country"],))
        db.commit()

        return {"status": "success", "message": "Block removed"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        safe_close(cur, db)


# =========================
# 🔍 Prediction
# =========================

@app.post("/predict")
def predict(data: RequestData):

    try:
        geo = requests.get(f"http://ip-api.com/json/{data.ip}", timeout=3).json()
    except:
        geo = {}

    country = geo.get("country", "Unknown")
    region = geo.get("regionName", "Unknown")

    cur = None
    db = None

    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT country FROM blocked_countries")
        blocked = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT country FROM allowed_countries")
        allowed = [row[0] for row in cur.fetchall()]

    except:
        blocked = []
        allowed = []

    finally:
        safe_close(cur, db)

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
