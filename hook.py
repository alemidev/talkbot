from pyrogram import filters

from bot import alemiBot

# from plugins.talkbot.util.trig import TRIGGERS

# @alemiBot.on_message(~filters.bot & ~filters.edited & 
# 		(filters.text | filters.caption), group=9821)
# async def search_triggers(client, message):
# 	for trig in TRIGGERS:
# 		if trig.check(message):
# 			await trig.fire(client, message)
