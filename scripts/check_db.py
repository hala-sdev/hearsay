from hearsay.config import db_url
import psycopg

with psycopg.connect(db_url, connect_timeout=10) as conn:
    row = conn.execute("SELECT version()").fetchone()
    print(f"Connected to database: {row[0]}")