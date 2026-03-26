# Multi-Server Setup Guide

## 1. Channel ID (Required)
Add to `.env`:
```
LOOT_CHANNEL_ID=1234567890123456789
```
- Right-click channel → Copy ID (Dev Mode on).

## 2. Data (Shared across servers)
- **Points**: SQLite DB (local) or Postgres (shared) – **global**, works multi-guild.
- **loot_log.json**: Shared history – appends guild-specific events fine.
- **In-memory**: claims/bids reset on restart (short-term).

## 3. Full Per-Guild Data (Optional Advanced)
Prefix keys with `guild_id:item` in dicts/DB.

## Run
1. Update `.env`.
2. `python bot.py` (restart).
3. Test in new server.

✅ No conflicts – channel per-bot-instance.
