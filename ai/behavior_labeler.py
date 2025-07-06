def summarize_daily_behavior(logs):
    total = len(logs)
    suspicious = sum(1 for log in logs if "admin" in str(log).lower() or "login" in str(log).lower())
    return f"Total logs: {total}, Suspicious activity: {suspicious}, Normal: {total - suspicious}"
