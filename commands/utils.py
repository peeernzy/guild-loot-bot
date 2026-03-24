import datetime

# =========================
# DATA STORAGE
# =========================
points_data = {}           # ✅ REAL POINTS STORAGE
weekly_spent = {}          # tracks total points spent per week
weekly_item_claims = {}    # tracks item-specific claims per week

# =========================
# HELPERS
# =========================
def _current_week():
    return datetime.date.today().isocalendar()[1]

def get_points(member_id: int) -> int:
    """Get user's current points."""
    return points_data.get(member_id, 0)

# =========================
# MAIN CHECK
# =========================
def can_spend(member_id: int, amount: int, item: str = None) -> bool:
    current_week = _current_week()

    # ✅ CHECK REAL POINTS (FIXED)
    if get_points(member_id) < amount:
        return False

    # Weekly total record
    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})
    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}
    weekly_spent[member_id] = record

    # Weekly cap
    if record["spent"] + amount > 50:
        return False

    # Item-specific limits
    item_record = weekly_item_claims.get(member_id, {"week": current_week, "items": {}})
    if item_record["week"] != current_week:
        item_record = {"week": current_week, "items": {}}
    weekly_item_claims[member_id] = item_record

    if item:
        count = item_record["items"].get(item, 0)

        if item == "Middle Horn" and count >= 1:
            return False

        if item == "Lesser Horn" and count >= 3:
            return False

    return True

# =========================
# SPEND POINTS
# =========================
def spend_points(member_id: int, amount: int, item: str = None):
    current_week = _current_week()

    # ✅ DEDUCT REAL POINTS
    points_data[member_id] = get_points(member_id) - amount

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

# =========================
# ADD POINTS (REWARD)
# =========================
def add_points(member_id: int, amount: int):
    """Add points to user."""
    points_data[member_id] = get_points(member_id) + amount
    return points_data[member_id]

# =========================
# REMAINING CLAIMS
# =========================
def remaining_claims(member_id: int, item: str) -> int:
    current_week = _current_week()

    item_record = weekly_item_claims.get(member_id, {"week": current_week, "items": {}})
    if item_record["week"] != current_week:
        item_record = {"week": current_week, "items": {}}

    count = item_record["items"].get(item, 0)

    if item == "Middle Horn":
        return max(0, 1 - count)

    if item == "Lesser Horn":
        return max(0, 3 - count)

    return None