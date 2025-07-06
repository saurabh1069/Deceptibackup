from flask import Flask, request, Response
from pymongo import MongoClient
from datetime import datetime
import logging
import os
import base64

backup_app = Flask("backup_decoy")

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
client = MongoClient(MONGO_URI)
db = client.get_database()
collection = db['decoy_logs']

# File logger
LOG_FILE = "decoy_http_backup.log"
logger = logging.getLogger("BackupHTTP")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Sample fake robots.txt
ROBOTS_TXT = """User-agent: *
Allow: /
User-agent: Googlebot
Disallow: /backup/
Disallow: /cgi-bin/
Disallow: /admin.bak/
Disallow: /old/
Disallow: /db_backup.1560534496/   # Old DB crash data
"""

@backup_app.route('/robots.txt')
def robots():
    return Response(ROBOTS_TXT, mimetype='text/plain')

@backup_app.route('/db_backup.1560534496/')
def fake_db():
    auth = request.headers.get('Authorization')
    ip = request.remote_addr
    timestamp = datetime.utcnow().isoformat()

    if not auth:
        logger.info(f"{timestamp} | IP {ip} | Attempted access to /db_backup.1560534496/ with NO auth")
        return Response(
            "Authentication required",
            401,
            {'WWW-Authenticate': 'Basic realm="Admin"'}
        )

    # Decode the Basic Auth header
    try:
        encoded = auth.split(" ")[1]
        decoded = base64.b64decode(encoded).decode('utf-8')
        username, password = decoded.split(":", 1)
    except Exception as e:
        logger.warning(f"{timestamp} | IP {ip} | Malformed Authorization header")
        return Response("Bad Request", 400)

    message = f"HoneyTrap Alert: Authentication Attempt to Fake Resource. Credentials used: {username}:{password}"

    log_data = {
        "timestamp": timestamp,
        "ip": ip,
        "endpoint": "/db_backup.1560534496/",
        "credentials": {"username": username, "password": password},
        "user_agent": request.headers.get("User-Agent", ""),
        "message": message
    }

    collection.insert_one(log_data)
    logger.info(f"{timestamp} | IP {ip} | {message} | User-Agent: {log_data['user_agent']}")

    return Response("<h1>UserName Password Incorrect. Try again.</h1>", 403)
