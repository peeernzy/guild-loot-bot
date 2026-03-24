import datetime

weekly_spent = {}  # shared dictionary

def can_spend(member_id: int, amount: int) -> bool:
    """Check if a member can spend points without exceeding weekly cap."""
    current_week = datetime.date.today().isocalendar()[1]
    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})

    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}

    return record["spent"] + amount <= 50

def spend_points(member_id: int, amount: int):
    """Deduct points from weekly spending record."""
    current_week = datetime.date.today().isocalendar()[1]
    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})

    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}

    record["spent"] += amount
    weekly_spent[member_id] = record
