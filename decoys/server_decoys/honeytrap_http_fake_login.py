# decoys/server_decoys/honeytrap_http_fake_login.py
from flask import Flask, request, Response
from pymongo import MongoClient
from datetime import datetime
import os
import logging

fake_login_app = Flask("fake_login_decoy")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
client = MongoClient(MONGO_URI)
db = client.get_database()
collection = db["decoy_logs"]

# Logger setup
LOG_FILE = "decoy_http_fake_login.log"
logger = logging.getLogger("FakeLoginHTTP")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(fh)

# Fake login page with hidden debug field
@fake_login_app.route('/login.html', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        debug = request.form.get('debug')
        if debug == 'true':
            log_attempt("POST", "/login.html", f"HoneyTrap Alert: Fake HIDDEN Form Data Manipulated | Username: {username} | Password: {password}")
        else:
            log_attempt("POST", "/login.html", f"Submitted login form with: {username}:{password}")
        return Response("Invalid credentials. Try again.", 403)

    log_attempt("GET", "/login.html", "Accessed fake login form with hidden debug field")
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <h3>Add entry</h3>
        <p>Add another Article</p>
        <form action="/login.html" method="post">
            <label for="username">Username:</label>
            <input name="username" id="username"><br>
            <label for="password">Password:</label>
            <input type="text" name="password" id="password"><br>
            <button type="submit">Login</button>
            <input type="hidden" name="debug" value="false">
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
