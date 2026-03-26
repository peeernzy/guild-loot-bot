# Bid Embed Update - Success!

**Previous:** Fixed refundpoints NameError.

**Update:** /bid command embed footer now displays:
```
Current Points: {remaining}pts + (bidding {bid_amount}pts)
Total Points: {total} pts
```

**Changes:**
- Rewrote commands/bid.py footer logic.
- user_points = get_points(user_id)  # remaining after bid deduction
- bidding_amount from bids dict
- Matches requested format.

**Status:** Complete. Test with `python bot.py` then `/bid`.

Steps:
- [x] Plan & edits
- [x] bid.py updated
- [x] Verified format
