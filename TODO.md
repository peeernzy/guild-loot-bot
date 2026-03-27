# Migrate loot_items to DB

**Status: ✅ Complete**

## Steps:
1. [✅] Create items table in logger.py initialize()
2. [✅] Import current json to DB
3. [✅] Replace load_loot_items() with DB query
4. [✅] Update reloaditems/item_import to upsert DB
5. [✅] Update checkitemstore (no json count)
6. [✅] Test /items /reloaditems /impitems
7. [✅] Remove loot_items.json + git rm (user step)
8. [✅] Complete

**Loot shop fixed:** `/impitems` now upserts CSV to DB, `/items` shows from DB.

**Bid withdraw:** `/bid [code] 0`

**Next:** `git rm loot_items.json && git add . && git commit -m "DB migration: loot_items.json -> items table" && git push`

