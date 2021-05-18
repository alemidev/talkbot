import os
import re
import asyncio

from pyrogram.types import Message

from util.message import send_media

class Trigger:
	def __init__(self, regex:str,
			response:str = "",
			from_self:bool = False,
			from_others:bool = True,
			mention:bool = True,
			media_path:str = "",
			auto_vanish:int = -1,
			):
		self.regex = re.compile(regex)
		self.response = response
		self.from_self = from_self
		self.from_others = from_others
		self.mention = mention
		self.path = media_path
		self.vanish = auto_vanish

	@staticmethod
	def unserialize(obj):
		return Trigger(obj["regex"],
				response=obj["response"],
				from_self=obj["from_self"],
				from_others=obj["from_others"],
				mention=obj["mention"],
				media_path=obj["path"],
				auto_vanish=obj["vanish"])

	def check(self, message:Message) -> bool:
		if message.from_user.is_self:
			if not self.from_self:
				return False
		elif not self.from_others:
			return False
		if self.mention and message.chat.type != "private" and not message.mentioned:
			return False
		if self.regex.search(message.text):
			return True
		return False

	async def fire(self, client, message:Message):
		if self.path:
			msg = await send_media(client, message.chat.id, self.path,
					reply_to_message_id=message.message_id, caption=self.response)
		else:
			msg = await message.reply(self.response)
		if self.vanish >= 0:
			await asyncio.sleep(self.auto_vanish)
			await msg.delete()

	def serialize(self) -> dict:
		return {
			"regex": self.regex.pattern,
			"response": self.response,
			"from_self": self.from_self,
			"from_others": self.from_others,
			"mention": self.mention,
			"path": self.path,
			"vanish": self.vanish
		}

class TriggerList:
	def __init__(self):
		if os.path.isfile("data/triggers.json"):
			with open("data/triggers.json") as f:
				self.data = json.load(f)
		else:
			self.data = []
			with open("data/triggers.json", "w") as f:
				json.dump(self.data, f)

	def serialize(self):
		with open("data/triggers.json", "w") as f:
			json.dump(self.data, f)

	def __iter__(self):
		return self.data.__iter__()

# TRIGGERS = TriggerList()
