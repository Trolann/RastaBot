import discord
import os
from replit import db
import random

intents = discord.Intents.default()
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

def set_welcome_message_season(season):
	"""Sets the season for the welcome message service"""
	db["season"] = season

def new_welcome_message_season(season):
	available_welcome_messages = db["welcome_message"]
	if season in available_welcome_messages:
		return '{} is already available'.format(season)
	
	available_welcome_messages[season] = ''
	db["welcome_message"] = available_welcome_messages

	return '{} added successfully'.format(season) 
	
def get_welcome_message_season():
	"""Returns the current season from the replit db"""
	return db["season"]

def new_welcome_message(season, welcome_message):
	"""Loads a new welcome message to the season list"""
	available_welcome_messages = db["welcome_message"]
	if season not in available_welcome_messages:
		return '{} must be added as a season first.'.format(season)

	if available_welcome_messages[season] is None:
		available_welcome_messages[season] = [welcome_message]
		db["welcome_message"] = available_welcome_messages
		return '{} created in {}'.format(welcome_message, season)

	available_welcome_messages[season].append(welcome_message)
	db["welcome_message"] = available_welcome_messages
	return '{} added to {}'.format(welcome_message, season)

def get_welcome_message(season):
	"""Returns a random welcome message from the current season"""
	seasonal_welcome_messages = db["welcome_message"][season]
	size = len(seasonal_welcome_messages)
	print('get_welcome_message.size| {}'.format(size))
	random_index = random.randrange(0, size)
	print('random_index| {}'.format(random_index))
	reply = seasonal_welcome_messages[random_index]
	print(reply)
	return reply

DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets

client = discord.Client(intents = intents)

@client.event
async def on_member_join(member):
	count_members()
	print('{} joined the server'.format(member))
	await member.send("Welcome. Please abide by the rules")
	guild = member.guild
	channel = guild.system_channel
	season = db["season"]
	reply = get_welcome_message(season)
	await channel.send(reply.format(member.name))

@client.event
async def on_ready(): # When ready
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): # On every message
	count_message()
	
	if message.author == client.user: # Cancel own message
		return

	if message.content.startswith('ping'):
		await message.channel.send('pong!')
	
	if message.content.startswith('!get_season'):
		reply = get_welcome_message_season()
		await message.channel.send(reply)
	
	if message.content.startswith('!set_season'):
		split_message = message.content.split()
		reply = set_welcome_message_season(split_message[1])
		await message.channel.send(reply)

	if message.content.startswith('!new_season'):
		split_message = message.content.split()
		updated_season = split_message[1] # !new_season [1]
		reply = new_welcome_message_season(updated_season)
		print(get_welcome_message_season(), '| {}'.format(reply))
		await message.channel.send(reply)

	if message.content.startswith('!new_welcome_message'):
		split_message = message.content.split()
		updated_welcome_message_season = split_message[1]
		updated_welcome_message = split_message[2:]
		updated_welcome_message = ' '.join(updated_welcome_message)
		reply = new_welcome_message(updated_welcome_message_season, updated_welcome_message)
		print(reply)
		await message.channel.send(reply)
	
	if message.content.startswith('!list_welcome_messages'):
		current_season = db["season"]
		seasonal_welcome_messages = db["welcome_message"][current_season]
		for i in range(len(seasonal_welcome_messages)):
			await message.channel.send('{}: {}'.format(i, seasonal_welcome_messages[i]))

	if message.content.startswith('!delete_welcome_message'):
		split_message = message.content.split()
		index_to_delete = int(split_message[1])
		current_season = db["season"]
		seasonal_welcome_messages = db["welcome_message"][current_season]
		deleted_welcome_message = seasonal_welcome_messages[index_to_delete]
		del seasonal_welcome_messages[index_to_delete]
		db["welcome_message"][current_season] = seasonal_welcome_messages
		print('Deleted {}: {} from {}'.format(index_to_delete, deleted_welcome_message, current_season))
		await message.channel.send('Deleted {}: {} from {}'.format(index_to_delete, deleted_welcome_message, current_season))


	if message.content.startswith('!keys'):
		keys = db.keys()
		print(keys)


client.run(DISCORD_TOKEN)
