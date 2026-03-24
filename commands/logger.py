import json
import datetime

LOG_FILE = "loot_log.json"

def log_event(event_type, user_id, item, amount=None):
    """
    Write a loot event to the log file.
    event_type: "claim", "bid", "win", "grant", "refund"
    user_id: Discord user ID
    item: Item name or "Points"
    amount: Points spent/awarded (optional)
    """
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event_type,
        "user_id": user_id,
        "item": item,
        "amount": amount
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
