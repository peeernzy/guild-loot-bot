# Guild Loot Bot Enhancement TODO

## Task: Enhance winner history display, manual logging, auto-post on timer end, tie handling

### Steps:
1. [ ] Create TODO.md with plan breakdown (current)
2. [x] Confirm plan with user ✅
3. [x] Edit commands/history.py:
   - Resolve user_id to display_name in embed. ✅
   - Show winner name explicitly with date/time. ✅
   - Cleanup unused winners_history.json code. ✅
4. [ ] Test /history shows names/date/item/pts.
5. [ ] Test /grant logs to history.
6. [ ] Verify bidding auto-post and ties (already implemented).
7. [ ] attempt_completion

**Status:** Edits complete. History now shows "WinnerName - YYYY-MM-DD HH:MM" with item/pts below. Auto-post/manual/ties were already functional.

