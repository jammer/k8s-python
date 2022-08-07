from flask import Flask, Response
import os
import httpx
import uuid

app = Flask(__name__)
myid = uuid.uuid4()

@app.route("/health")
def health():
  try:
    r = httpx.get("http://pingpong-svc/pong")
    if r.status_code == httpx.codes.OK:
      return "Ready"
  except httpx.HTTPError as e:
    print(e)
  return Response("Not Ready", status=500)

@app.route("/")
def root():
  time = "time missing"
  if os.path.exists("/data/time.txt"):
    f = open("/data/time.txt","r")
    time = f.readline()
  counter = "error"
  r = httpx.get("http://pingpong-svc/pong")
  if r.status_code == httpx.codes.OK:
    counter = r.text
  message = os.getenv("MESSAGE","Greeting not set")
  return f"{message}<br>{time.strip()} {myid}<br>Ping / Pongs: {counter}"
