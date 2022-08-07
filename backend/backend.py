from markupsafe import escape
from flask import Flask, Response, request
import psycopg
import os
import sys

app = Flask(__name__)

def database():
  conn = psycopg.connect(os.getenv("SERVER",""))
  curs = conn.cursor()
  curs.execute("CREATE TABLE IF NOT EXISTS todos (id SERIAL PRIMARY KEY, task VARCHAR(140))")
  return conn, curs

@app.route("/health")
def health():
  conn, curs = database()
  conn.commit()
  curs.close()
  conn.close()
  return "Ready"

@app.route("/todos", methods=["GET"])
def get_todos():
  conn, curs = database()
  curs.execute("SELECT task FROM todos")
  todos = []
  for todo in curs:
    todos.append(todo[0])
  conn.commit()
  curs.close()
  conn.close()
  return todos

@app.route("/todos", methods=["POST"])
def post_todo():
  conn, curs = database()
  curs.execute("INSERT INTO todos (task) VALUES (%s)", [request.form["todo"]])
  conn.commit()
  curs.close()
  conn.close()
  return f"Todo added!"

@app.route("/")
def root():
  return "Project Backend"
