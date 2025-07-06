from flask import Flask, request, send_from_directory, Response
from pymongo import MongoClient
from datetime import datetime
import os
import logging

login_app = Flask("login_decoy")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
client = MongoClient(MONGO_URI)
db = client.get_database()
collection = db["decoy_logs"]

# Logger
LOG_FILE = "decoy_http_login.log"
logger = logging.getLogger("LoginHTTP")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(fh)

# Serve /login.html with fake debug comment
@login_app.route('/login.html', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        log_attempt("POST", "/login.html", f"Submitted login form with: {username}:{password}")
        return Response("Invalid credentials. Try again.", 403)

    log_attempt("GET", "/login.html", "Accessed fake login form with debug comment")
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <h3>Add entry</h3>
        <p>Add another Article</p>
        <!-- DEBUG - the source code for the old login page is login.php.bak -->
        <form action="/login.html" method="post">
            Username: <input name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    """

# Trap 404 for login.php.bak
@login_app.route('/login.php.bak')
def trap_login_bak():
    log_attempt("GET", "/login.php.bak", "HoneyTrap Alert: Fake HTML Comment Data Use")
    return Response("Not Found", 404)

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
