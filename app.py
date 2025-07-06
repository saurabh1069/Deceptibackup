from flask import Flask, render_template, request
from database.db_connector import get_db
from pymongo import MongoClient
from datetime import datetime
import threading
import os
import logging

# === Decoy Servers ===
from decoys.server_decoys.honeytrap_http_fake import decoy_app
from decoys.server_decoys.honeytrap_http_backup import backup_app
from decoys.server_decoys.honeytrap_http_login import login_app
from decoys.server_decoys.honeytrap_http_fake_login import fake_login_app
from decoys.server_decoys.honeytrap_http_cookie_fake import fake_cookie_app

# ✅ AI Blueprint
from routes.ai_routes import ai_routes

# === MAIN APP: dashboard ===
app = Flask(__name__, template_folder='web/templates')
app.config['MONGO_URI'] = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
db = get_db(app.config['MONGO_URI'])

# ✅ Register AI Routes
app.register_blueprint(ai_routes)

# === DASHBOARD ROUTES ===
@app.route('/')
def dashboard():
    alerts = db['alerts'].find().sort("timestamp", -1)
    return render_template('dashboard.html', alerts=alerts)

@app.route('/alerts')
def alert_view():
    alerts = db['alerts'].find().sort("timestamp", -1)
    return render_template('alerts.html', alerts=alerts)

@app.route('/create-test-alert')
def create_test_alert():
    test_alert = {
        "message": "🔥 Intrusion Detected: Port Scan from 192.168.1.100",
        "timestamp": datetime.utcnow().isoformat()
    }
    db['alerts'].insert_one(test_alert)
    return "Test alert inserted!"

@app.route('/log', methods=['POST'])
def log_decoy():
    data = request.json
    db['decoy_logs'].insert_one(data)
    return {'status': 'logged'}, 201


# === THREADS FOR ALL FAKE SERVICES ===
def run_dashboard():
    app.run(port=5000)

def run_decoy():
    decoy_app.run(port=8888)

def run_backup_decoy():
    backup_app.run(port=9091)

def run_login_decoy():
    login_app.run(port=9092)

def run_fake_login_decoy():
    fake_login_app.run(port=9093)

def run_cookie_fake():
    fake_cookie_app.run(port=9094)

if __name__ == '__main__':
    t1 = threading.Thread(target=run_dashboard)
    t2 = threading.Thread(target=run_decoy)
    t3 = threading.Thread(target=run_backup_decoy)
    t4 = threading.Thread(target=run_login_decoy)
    t5 = threading.Thread(target=run_fake_login_decoy)
    t6 = threading.Thread(target=run_cookie_fake)

    # Start all honeypot threads
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()

    # Wait for them to complete (they won’t unless killed)
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
