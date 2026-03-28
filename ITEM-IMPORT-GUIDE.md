# Item Import/Export Guide

## **`/impitems [CSV] [force:true]`** (Mod/Elder)
**CSV Format**:
```
code,name,cost,rule,stock,rarity
1,Rare Sword,15,Bidding,5,rare
2,Common Shield,5,Claim,10,common
```
**Required**: code,name,cost,rule
**Optional**: stock=999, rarity=common
**Valid rarities**: common,uncommon,rare,epic,legend,mythic

**Actions**:
1. Validates CSV
2. **Upserts** DB (`INSERT ... ON CONFLICT UPDATE`)
3. `reload_loot_items()` → `/items` updated
4. Warns active claims/bids missing (use `force:true`)

## **`/expitems`** → Downloads CSV
**From**: `loot_items.json` (legacy, **update to DB export**)
**To**: `loot_items_export.csv`

## **Workflow**:
```
/inventoryclear → checkitemstore=0 → /impitems → 66 items → /items works
/expitems → backup CSV → edit → /impitems
```

**Example**: ITEMS-EXAMPLE.csv ready!

**Pro Tip**: `/inventoryclear` + `/impitems` = clean slate 🎉
