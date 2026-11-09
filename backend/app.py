import os
import psycopg2
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "banking")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "secure_password")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# تهيئة جدول العمليات عند الإقلاع
@app.on_event("startup")
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id SERIAL PRIMARY KEY,
                sender VARCHAR(50),
                receiver VARCHAR(50),
                amount NUMERIC,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Init Warning (Normal if Read-Only Standby): {e}")

class TransferRequest(BaseModel):
    sender: str
    receiver: str
    amount: float

@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT pg_is_in_recovery();")
        replica = cur.fetchone()[0]
        conn.close()
        r.ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if replica:
        raise HTTPException(status_code=503, detail="replica")
    return {"status": "healthy", "node": os.getenv("NODE_ROLE", "unknown")}

@app.post("/api/transfers")
def create_transfer(payload: TransferRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transfers (sender, receiver, amount) VALUES (%s, %s, %s) RETURNING id;",
            (payload.sender, payload.receiver, payload.amount)
        )
        transfer_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        # كسر أو تحديث الكاش
        r.delete("latest_transfers")
        return {"success": True, "transfer_id": transfer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database write failed: {str(e)}")

@app.get("/api/transfers")
def get_transfers():
    cached = r.get("latest_transfers")
    if cached:
        return {"data": eval(cached), "source": "redis_cache"}

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, sender, receiver, amount, created_at FROM transfers ORDER BY id DESC LIMIT 5;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    result = [{"id": row[0], "sender": row[1], "receiver": row[2], "amount": float(row[3]), "date": str(row[4])} for row in rows]
    r.setex("latest_transfers", 60, str(result))
    return {"data": result, "source": "database"}
