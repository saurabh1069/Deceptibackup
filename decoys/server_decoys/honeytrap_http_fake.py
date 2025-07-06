from flask import Flask, request
from pymongo import MongoClient
import logging
from datetime import datetime
import os

decoy_app = Flask("decoy")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
client = MongoClient(MONGO_URI)
decoy_db = client.get_database()
decoy_collection = decoy_db['decoy_logs']

LOG_FILE = "decoy_http_fake.log"
logger = logging.getLogger("DecoyHTTP")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def log_decoy_request(req):
    timestamp = datetime.utcnow().isoformat()
    ip = req.remote_addr or 'unknown'
    method = req.method
    path = req.path
    headers = dict(req.headers)

    message = f" IP {ip} tried reaching fake decoy port"

    log_entry = {
        "timestamp": timestamp,
        "ip": ip,
        "method": method,
        "path": path,
        "headers": headers,
        "message": message
    }

    decoy_collection.insert_one(log_entry)

    logger.info(
        f"{timestamp} | {ip} | {method} | {path} | {message} | Headers: {headers}"
    )

@decoy_app.route("/", methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def hello_world():
    log_decoy_request(request)
    return """
    <!DOCTYPE html>
    <html><body>
    <h1>Hello World</h1>
    <p>This is a decoy HTTP server running on a separate port.</p>
    </body></html>
    """
