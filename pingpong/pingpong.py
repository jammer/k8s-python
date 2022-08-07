from markupsafe import escape
from flask import Flask, Response
import psycopg
import os
import sys

app = Flask(__name__)

def database():
  conn = psycopg.connect(os.getenv("SERVER",""))
  curs = conn.cursor()
  curs.execute("CREATE TABLE IF NOT EXISTS pingpong (id SERIAL PRIMARY KEY)")
  return conn, curs

@app.route("/health")
def health():
  conn, curs = database()
  conn.commit()
  curs.close()
  conn.close()
  return "Ready"

@app.route("/pingpong")
def pinpgpong():
  conn, curs = database()
  curs.execute("INSERT INTO pingpong(id) VALUES(DEFAULT)")
  curs.execute("SELECT COUNT(id) FROM pingpong")
  count = curs.fetchone()
  conn.commit()
  curs.close()
  conn.close()
  return f"Pong {count[0]}"

@app.route("/pong")
def pong():
  conn, curs = database()
  curs.execute("SELECT COUNT(id) FROM pingpong")
  count = curs.fetchone()
  conn.commit()
  curs.close()
  conn.close()
  return f"{count[0]}"

@app.route("/")
def root():
  return "Pingpong"
