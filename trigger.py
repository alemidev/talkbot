import json
import re

from pyrogram import filters
from pyrogram.raw.functions.account import UpdateStatus

from bot import alemiBot

from util.permission import is_allowed, is_superuser
from util.getters import get_text
from util.message import is_me, edit_or_reply
from util.command import filterCommand
from util.decorators import report_error, set_offline
from util.help import HelpCategory

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("TRIGGER")

TRIGGERS = {}
try:
	with open("data/triggers.json") as f:
		buf = json.load(f)
		for k in buf:
			TRIGGERS[k] = { "pattern" : re.compile(k), "reply" : buf[k] }
except FileNotFoundError:
	with open("data/triggers.json", "w") as f:
		json.dump({}, f)
except:
	logger.exception("Could not load triggers from file")

def serialize():
	global TRIGGERS
	with open("data/triggers.json", "w") as f:
		json.dump({ key : TRIGGERS[key]["reply"] for key in TRIGGERS }, f)

HELP.add_help(["trigger", "trig"], "register a new trigger",
			"Add a new trigger sequence and corresponding message. Regex can be used. Use " +
			"sigle quotes `'` to wrap triggers with spaces (no need to wrap message). " +
			"Use this command to list triggers (`-list`), add new (`-n`) and delete (`-d`). " +
			"Triggers will always work in private chats, but only work when mentioned in groups." ,
			args="( -list | -d <trigger> | -n <trigger> <message> )")
@alemiBot.on_message(is_superuser & filterCommand(["trigger", "trig"], list(alemiBot.prefixes), options={
	"new" : ["-n", "-new"],
	"del" : ["-d", "-del"]
}, flags=["-list"]))
@report_error(logger)
@set_offline
async def trigger_cmd(client, message):
	global TRIGGERS
	args = message.command

	changed = False
	if "-list" in args["flags"]:
		logger.info("Listing triggers")
		out = ""
		for t in TRIGGERS:
			out += f"`{TRIGGERS[t]['pattern'].pattern} → ` {TRIGGERS[t]['reply']}\n"
		if out == "":
			out += "` → Nothing to display`"
		await edit_or_reply(message, out)
	elif "new" in args and "arg" in args:
		logger.info("New trigger")
		pattern = re.compile(args["new"])
		TRIGGERS[args["new"]] = { "pattern": pattern, "reply" : args["arg"] }
		await edit_or_reply(message, f"` → ` New trigger `{pattern.pattern}`")
		changed = True
	elif "del" in args:
		logger.info("Removing trigger")
		if TRIGGERS.pop(args["del"], None) is not None:
			await edit_or_reply(message, "` → ` Removed trigger")
			changed = True
	else:
		return await edit_or_reply(message, "`[!] → ` Wrong use")
	if changed:
		serialize()

@alemiBot.on_message(~filters.me & ~filters.bot & ~filters.edited & (filters.text | filters.caption), group=8)
async def search_triggers(client, message):
	global TRIGGERS
	if message.chat.type != "private" and not message.mentioned:
		return # in groups only get triggered in mentions
	for key in TRIGGERS:
		if TRIGGERS[key]["pattern"].search(get_text(message)):
			await message.reply(TRIGGERS[key]["reply"])
			await client.send(UpdateStatus(offline=True))
			logger.info("T R I G G E R E D")
