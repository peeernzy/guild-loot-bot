import discord
from discord.ext import commands

# Replace the 3 hardcoded strings in helpcommands.py
old_texts = [
    '`/items` - Browse loot shop',
    '`/items` - Shop',
    '`/itemlist` - Full table'
]

new_texts = [
    '`/inventory` - Browse loot shop',
    '`/inventory` - Shop',
    '`/inventory_list` - Full table'
]

with open('commands/helpcommands.py', 'r') as f:
    content = f.read()

for old, new in zip(old_texts, new_texts):
    content = content.replace(old, new)

with open('commands/helpcommands_fixed.py', 'w') as f:
    f.write(content)

print('Fixed file saved as commands/helpcommands_fixed.py')
print('Restart bot → use new file')

