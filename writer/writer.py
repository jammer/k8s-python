from datetime import datetime
import time

while True:
  now = datetime.now().isoformat()
  print(now)
  f = open("/data/time.txt","w")
  f.write(now + "\n")
  time.sleep(5)
