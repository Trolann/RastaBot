import discord
import os
from discord.ext import commands
from replit import db

intents = discord.Intents.all()
intents.members = True

def count_message():
	"""Counts total messages processed. Called on every on_message()"""
	messages = db["messages"] # Always get previous value from DB
	messages += 1
	db["messages"] = messages # Store new value
	print('Messages processed: {}'.format(messages)) # Console log

def count_members():
	"""Counts total members processed. Called on every on_member_joined()"""
	members = db["members"] # Always get previous value from DB
	members += 1
	db["members"] = members # Store new value
	print('Members processed: {}'.format(members)) # Console log

DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets

client = commands.Bot(command_prefix = "!", intents = intents)

@client.event
async def on_member_join(member):
	count_members()
	print('{} joined the server'.format(member))
	await member.send("Welcome. Please abide by the rules")
	guild = member.guild
	channel = guild.system_channel
	await channel.send('Welcome {}'.format(member.name))

@client.event
async def on_ready(): # When ready
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): # On every message
	count_message()
	
	if message.author == client.user: # Cancel own message
		return

	if message.content.startswith('ping'):
		await message.channel.send('pong')

client.run(DISCORD_TOKEN)
