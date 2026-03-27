# Migrate loot_items to DB

**Status: In Progress**

## Steps:
1. [✅] Create items table in logger.py initialize()
2. [✅] Import current json to DB
3. [ ] Replace load_loot_items() with DB query
4. [ ] Update reloaditems/item_import to upsert DB
5. [ ] Remove loot_items.json + git rm
6. [ ] Update checkitemstore (no json count)
7. [ ] Test /items /reloaditems /impitems
8. [ ] Complete
