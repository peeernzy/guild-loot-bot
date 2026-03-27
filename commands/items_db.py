from commands.points import using_postgres, get_sqlite_connection, get_postgres_connection
from commands.logger import initialize_history

def load_loot_items_from_db():
    initialize_history()
    costs = {}
    claim_aliases = {}
    bid_aliases = {}
    item_meta = {}
    
    claim_index = 1
    bid_index = 1
    
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, cost, rule, stock, rarity FROM items ORDER BY name")
                rows = cur.fetchall()
    else:
        with get_sqlite_connection() as conn:
            rows = conn.execute("SELECT name, cost, rule, stock, rarity FROM items ORDER BY name").fetchall()
    
    for row in rows:
        name, cost, rule, stock, rarity = row
        cost = int(cost)
        stock = int(stock)
        
        costs[name] = {"cost": cost, "rule": rule}
        
        is_bidding = str(rule).startswith("Bidding")
        scoped_code = str(bid_index if is_bidding else claim_index)
        item_meta[name] = {
            "source_code": scoped_code,
            "stock": stock,
            "rarity": rarity,
            "scoped_code": scoped_code,
            "aliases": [],
            "is_bidding": is_bidding,
        }
        
        target_aliases = bid_aliases if is_bidding else claim_aliases
        target_aliases[scoped_code] = name
        
        if is_bidding:
            bid_index += 1
        else:
            claim_index += 1
    
    return costs, claim_aliases, bid_aliases, item_meta

