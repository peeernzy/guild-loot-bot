from commands.points import using_postgres, get_sqlite_connection, get_postgres_connection
from commands.logger import initialize_history
import json

def import_json_to_db():
    """One-time migration of current loot_items.json to items table."""
    initialize_history()
    
    try:
        with open("loot_items.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No loot_items.json found")
        return
    
    items = []
    if isinstance(data, dict):
        items = list(data.items())
    elif isinstance(data, list):
        items = data
    
    inserted = 0
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                for item in items:
                    if isinstance(item, tuple):
                        name, details = item
                    else:
                        name = item["name"]
                        details = item
                    
                    cost = details.get("cost", 0)
                    rule = details.get("rule", "Claim")
                    stock = details.get("stock", 999)
                    rarity = details.get("rarity", "common")
                    
                    cur.execute("""
                        INSERT INTO items (name, cost, rule, stock, rarity)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                            cost = EXCLUDED.cost,
                            rule = EXCLUDED.rule,
                            stock = EXCLUDED.stock,
                            rarity = EXCLUDED.rarity
                    """, (str(name), int(cost), str(rule), int(stock), str(rarity)))
                    inserted += 1
            conn.commit()
    else:
        with get_sqlite_connection() as conn:
            for item in items:
                if isinstance(item, tuple):
                    name, details = item
                else:
                    name = item["name"]
                    details = item
                
                cost = details.get("cost", 0)
                rule = details.get("rule", "Claim")
                stock = details.get("stock", 999)
                rarity = details.get("rarity", "common")
                
                conn.execute("""
                    INSERT INTO items (name, cost, rule, stock, rarity)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        cost = excluded.cost,
                        rule = excluded.rule,
                        stock = excluded.stock,
                        rarity = excluded.rarity
                """, (str(name), int(cost), str(rule), int(stock), str(rarity)))
                inserted += 1
            conn.commit()
    
    print(f"Imported {inserted} items to DB")

if __name__ == "__main__":
    import_json_to_db()

