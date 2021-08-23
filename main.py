import discord
from replit import db
import os

DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets

client = discord.Client()

def count_message():
	messages = db["messages"]
	messages += 1
	db["messages"] = messages
	print('Messages processed: {}'.format(messages))

@client.event
async def on_ready(): # When ready
		print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): # On every message
		count_message()
		if message.author == client.user: # Ignore if it's a bot message
			return

		if message.content.startswith('$hello'):
			await message.channel.send('Hello!')

client.run(DISCORD_TOKEN)
