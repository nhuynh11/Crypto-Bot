from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "Server running."

def run():
  app.run(host='0.0.0.0', port=8080)

# pinging replit server to keep it up
def keep_alive():
  t = Thread(target=run)
  t.start()