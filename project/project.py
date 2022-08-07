import datetime
from flask import Flask, Response, send_from_directory
import httpx
from os.path import exists

app = Flask(__name__)

now = datetime.datetime.now().strftime("%Y%m%d")

@app.route("/health")
def health():
  return "Ready"

@app.route("/")
def root():
  if not exists(f"/data/{now}.jpg"):
    print("Daily image missing. Fetching new image!")
    req = httpx.get("https://picsum.photos/300", follow_redirects=True)
    f = open(f"/data/{now}.jpg","wb")
    f.write(req.content)
  resp = f"""
<img src="pics/{now}.jpg"><br>
<form method="post" action="/todos">
<input type="text" name="todo" maxlength="140">
<input type="submit" value="Create TODO">
</form>
<ul>"""
  req = httpx.get("http://backend-svc/todos")
  todos = req.json()
  for todo in req.json():
    resp = resp + f"<li>{todo}</li>"
  resp = resp + "</ul>"
  return resp

@app.route("/pics/<string:pic>")
def picture(pic):
  return send_from_directory("/data", pic)


