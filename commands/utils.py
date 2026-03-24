import datetime

weekly_spent = {}          # tracks total points spent per week
weekly_item_claims = {}    # tracks item-specific claims per week

def _current_week():
    """Return current ISO week number."""
    return datetime.date.today().isocalendar()[1]

def can_spend(member_id: int, amount: int, item: str = None) -> bool:
    """Check if a member can spend points without exceeding weekly cap or item limits."""
    current_week = _current_week()

    # Weekly total record
    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})
    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}
    weekly_spent[member_id] = record

    # ✅ Weekly cap check
    if record["spent"] + amount > 50:
        return False

    # ✅ Item-specific limits
    item_record = weekly_item_claims.get(member_id, {"week": current_week, "items": {}})
    if item_record["week"] != current_week:
        item_record = {"week": current_week, "items": {}}
    weekly_item_claims[member_id] = item_record

    if item:
        count = item_record["items"].get(item, 0)

        # Middle Horn → max 1 per week
        if item == "Middle Horn" and count >= 1:
            return False

        # Lesser Horn → max 3 per week
        if item == "Lesser Horn" and count >= 3:
            return False

    return True

def spend_points(member_id: int, amount: int, item: str = None):
    """Deduct points and record item claim."""
    current_week = _current_week()

    # Weekly total record
    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})
    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}
    record["spent"] += amount
    weekly_spent[member_id] = record

    # Item-specific record
    item_record = weekly_item_claims.get(member_id, {"week": current_week, "items": {}})
    if item_record["week"] != current_week:
        item_record = {"week": current_week, "items": {}}
    if item:
        item_record["items"][item] = item_record["items"].get(item, 0) + 1
    weekly_item_claims[member_id] = item_record

def remaining_claims(member_id: int, item: str) -> int:
    """Return how many claims a member has left for a specific item this week."""
    current_week = _current_week()
    item_record = weekly_item_claims.get(member_id, {"week": current_week, "items": {}})
    if item_record["week"] != current_week:
        item_record = {"week": current_week, "items": {}}
    count = item_record["items"].get(item, 0)

    if item == "Middle Horn":
        return max(0, 1 - count)
    if item == "Lesser Horn":
        return max(0, 3 - count)
    return None  # unlimited items

def add_points(member_id: int, amount: int):
    """Refund points to a member (reduce their weekly spent)."""
    current_week = _current_week()

    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})
    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}

    # ✅ Subtract from spent to simulate refund
    record["spent"] = max(0, record["spent"] - amount)
    weekly_spent[member_id] = record
    return record["spent"]
