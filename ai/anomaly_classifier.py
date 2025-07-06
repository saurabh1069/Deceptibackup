def classify_log_anomaly(log):
    ip = log.get("ip", "unknown")
    if "admin" in str(log).lower():
        return {"score": 9, "reason": "Accessed suspicious admin page"}
    elif "login" in str(log).lower():
        return {"score": 7, "reason": "Attempted login interaction"}
    elif "backup" in str(log).lower():
        return {"score": 6, "reason": "Accessed backup resource"}
    else:
        return {"score": 3, "reason": "Low-risk generic behavior"}
