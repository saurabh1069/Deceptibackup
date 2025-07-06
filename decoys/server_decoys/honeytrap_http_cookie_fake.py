# 📄 decoys/server_decoys/honeytrap_http_cookie_fake.py
from flask import Flask, request, Response
from pymongo import MongoClient
from datetime import datetime
import os
import logging

fake_cookie_app = Flask("cookie_debug_trap")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
client = MongoClient(MONGO_URI)
db = client.get_database()
collection = db["decoy_logs"]

# Logger
LOG_FILE = "decoy_http_cookie_fake.log"
logger = logging.getLogger("FakeCookieTrap")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(fh)

@fake_cookie_app.route('/login.html', methods=['GET', 'POST'])
def fake_cookie_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cookie = request.headers.get('Cookie', '')

        log_attempt("POST", "/login.html", f"HoneyTrap Alert: Received login: {username}:{password} | Cookie: {cookie}")
        return Response("Invalid credentials.", 403)

    log_attempt("GET", "/login.html", "Accessed fake login page with cookie trap")
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <h3>Add entry</h3>
        <p>Add another Article</p>
        <form action="/login.html" method="post">
            <label for="username">Username</label>
            <input type="text" id="username" name="username">
            <br><br>
            <label for="password">Password:</label>
            <input type="text" id="password" name="password">
            <br><br>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """

def log_attempt(method, path, message):
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")
    timestamp = datetime.utcnow().isoformat()

    entry = {
        "timestamp": timestamp,
        "ip": ip,
        "method": method,
        "path": path,
        "user_agent": user_agent,
        "message": message
    }

    collection.insert_one(entry)
    logger.info(f"{timestamp} | {ip} | {method} | {path} | {message} | UA: {user_agent}")
