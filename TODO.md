# Guild Loot Bot Fix: Allclanpoints Command Error

## Steps:
- [x] 1. Create TODO.md with plan steps (current).
- [x] 2. Edit commands/summary.py: Add `await interaction.response.defer()` immediately, replace all `interaction.response.send_message(...)` with `await interaction.followup.send(...)` (3 places: no points, no valid members, success summary).
- [x] 3. Verify edit success.
- [x] 4. Update TODO.md with completion.
- [ ] 5. Test command in Discord (run bot, use /allclanpoints on empty/full DB).
- [ ] 6. attempt_completion once fixed.

