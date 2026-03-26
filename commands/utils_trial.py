import datetime
from .points import get_points as get_member_points, save_points

# =========================
# DATA STORAGE
# =========================
points_data = {}           # ✅ REAL POINTS STORAGE (now backed by points.json)
weekly_spent = {}          # tracks total points spent per week
weekly_item_claims = {}    # tracks item-specific claims per week (disabled for trial)

# =========================
# HELPERS
# =========================
def _current_week():
    return datetime.date.today().isocalendar()[1]

def get_points(member_id: int) -> int:
    """Get user's current points (from persistent storage)."""
    return get_member_points(member_id)

# =========================
# MAIN CHECK
# =========================
def can_spend(member_id: int, amount: int, item: str = None) -> bool:
    current_week = _current_week()

    # ✅ CHECK REAL POINTS (from persistent storage)
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

    # Item-specific limits DISABLED for trial
    return True

# =========================
# SPEND POINTS
# =========================
def spend_points(member_id: int, amount: int, item: str = None):
    current_week = _current_week()

    # ✅ DEDUCT REAL POINTS (and return updated balance)
    from .points import deduct_points
    new_balance = deduct_points(member_id, amount)

    # Weekly total record
    record = weekly_spent.get(member_id, {"week": current_week, "spent": 0})
    if record["week"] != current_week:
        record = {"week": current_week, "spent": 0}
    record["spent"] += amount
    weekly_spent[member_id] = record

    # Item-specific record DISABLED for trial

    return new_balance

# =========================
# ADD POINTS (REWARD)
# =========================
def add_points(member_id: int, amount: int):
    """Add points to user (persists to file)."""
    from .points import add_points as add_member_points
    return add_member_points(member_id, amount)

# =========================
# REMAINING CLAIMS
# =========================
def remaining_claims(member_id: int, item: str) -> int:
    # DISABLED for trial testing - unlimited claims
    return None
