import datetime

weekly_spent = {}          # tracks total points spent per week
weekly_item_claims = {}    # tracks item-specific claims per week

def can_spend(member_id: int, amount: int, item: str = None) -> bool:
    """Check if a member can spend points without exceeding weekly cap or item limits."""
    current_week = datetime.date.today().isocalendar()[1]

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
    current_week = datetime.date.today().isocalendar()[1]

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
