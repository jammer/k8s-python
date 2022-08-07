from markupsafe import escape
from flask import Flask, Response, request
import psycopg
import os
import sys
import asyncio
import nats

app = Flask(__name__)


async def sendmessage(message):
  nc = await nats.connect(os.getenv("NATS","nats://127.0.0.1:4222"))
  await nc.publish("todos",message.encode())
  await nc.flush()

def database():
  conn = psycopg.connect(os.getenv("SERVER",""))
  curs = conn.cursor()
  curs.execute("CREATE TABLE IF NOT EXISTS todos (id SERIAL PRIMARY KEY, task VARCHAR(140), done BOOLEAN DEFAULT FALSE)")
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
  curs.execute("SELECT id, task, done FROM todos")
  todos = []
  for todo in curs:
    todos.append({"id": todo[0], "task": todo[1], "done": todo[2]})
  conn.commit()
  curs.close()
  conn.close()
  return todos

@app.route("/todos/<int:todo>", methods=["PUT"])
def done_todo(todo):
  conn, curs = database()
  curs.execute("UPDATE todos SET done = TRUE where id = %s", [todo])
  conn.commit()
  curs.execute("SELECT task FROM todos where id = %s", [todo])
  result = curs.fetchone()
  asyncio.run(sendmessage(f"Completed todo: {result[0]}"))
  curs.close()
  conn.close()
  return f"Todo done!"

@app.route("/todos", methods=["POST"])
def post_todo():
  conn, curs = database()
  curs.execute("INSERT INTO todos (task) VALUES (%s)", [request.form["todo"]])
  conn.commit()
  asyncio.run(sendmessage(f"""Created todo: {request.form["todo"]}"""))
  curs.close()
  conn.close()
  return f"Todo added!"

@app.route("/")
def root():
  return "Project Backend"
