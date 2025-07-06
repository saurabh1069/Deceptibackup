from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from database.db_connector import get_db
from ai.anomaly_classifier import classify_log_anomaly
from ai.behavior_labeler import summarize_daily_behavior
from ai.threat_explainer import explain_threat
from ai.decoy_generator import generate_fake_page
from dotenv import load_dotenv
import openai
import os

# Load API key securely
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/decepticoders")
db = get_db(MONGO_URI)
ai_routes = Blueprint('ai', __name__)


@ai_routes.route('/ai')
def ai_dashboard():
    ai_summary = db['ai_insights'].find_one({"type": "daily_summary"}, sort=[("timestamp", -1)])
    anomalies = list(db['ai_anomalies'].find().sort("score", -1).limit(10))
    behaviors = list(db['ai_behavior'].find().sort("timestamp", -1).limit(10))
    return render_template("ai_dashboard.html", summary=ai_summary, anomalies=anomalies, behaviors=behaviors)

@ai_routes.route('/ai/run-summary', methods=['POST'])
def run_ai_summary():
    logs = list(db['decoy_logs'].find())

    for log in logs[-30:]:  # 🔍 Run anomaly classifier
        result = classify_log_anomaly(log)
        if result:
            db['ai_anomalies'].insert_one({
                "ip": log.get("ip"),
                "score": result.get("score", 5),
                "reason": result.get("reason", "Unclear"),
                "timestamp": log.get("timestamp")
            })

    summary = summarize_daily_behavior(logs)  # 🤖 Summarize behaviors
    db['ai_insights'].insert_one({
        "type": "daily_summary",
        "timestamp": datetime.utcnow(),
        "summary": summary
    })
    db['ai_behavior'].insert_one({
        "timestamp": datetime.utcnow(),
        "label": "Daily Profile",
        "notes": summary
    })

    return jsonify({"status": "ok", "summary": summary})

@ai_routes.route('/ai/explain')
def explain_ip():
    ip = request.args.get("ip")
    log = db['decoy_logs'].find_one({"ip": ip}, sort=[("timestamp", -1)])
    if not log:
        return jsonify({"error": "No log found for this IP."}), 404
    explanation = explain_threat(log)
    return render_template("ai_dashboard.html", explanation={"ip": ip, "text": explanation})

@ai_routes.route('/ai/generate-decoy', methods=['POST'])
def generate_decoy():
    topic = request.form.get("topic", "admin panel")
    html = generate_fake_page(topic)
    return render_template("ai_dashboard.html", decoy_html=html)
