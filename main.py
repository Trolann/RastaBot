import discord
import os
from replit import db

intents = discord.Intents.all()
intents.members = True

def count_message():
	"""Counts total messages processed. Called on every on_message()"""
	messages = db["messages"] # Always get previous value from DB
	messages += 1
	db["messages"] = messages # Store new value
	print('Messages processed: {}'.format(messages)) # Console log

DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets

client = discord.Client()

@client.event
async def on_member_join(member):
	print('Someone new!')
	await member.send("Welcome")

@client.event
async def on_ready(): # When ready
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): # On every message
	count_message()
	
	if message.author == client.user: # Cancel own message
		return

	if message.content.startswith('?'):
		await message.channel.send('Command')

client.run(DISCORD_TOKEN)
