"""
RastaBot developed by Trolan (Trevor Mathisen).

This bot:
1) Welcomes new members to the discord sever
2) Has the ability to adjust welcome messages based on season
3) TODO: Add roles to users based on their methods of grow
4) TODO: Facilitate auctions and raffles
TODO: Mas comments 
"""
#import discord
from replit import db
import random
import rastabot_config

intents = rastabot_config.intents
REQUEST_PREFIX, COMMAND_PREFIX = rastabot_config.REQUEST_PREFIX, rastabot_config.COMMAND_PREFIX
about = rastabot_config.about
DISCORD_TOKEN = rastabot_config.DISCORD_TOKEN
client = rastabot_config.client

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
	print('Season updated to {}'.format(season))
	reply = 'Season updated to {}'.format(season)
	return reply

def new_welcome_message_season(season):
	available_welcome_messages = db["welcome_message"]
	if season in available_welcome_messages:
		return '{} is already available'.format(season)
	
	available_welcome_messages[season] = ''
	db["welcome_message"] = available_welcome_messages

	return '{} added successfully'.format(season) 
	
def get_welcome_message_season():
	"""Returns the current season from the replit db"""
	print('get_welcome_message_season(): {}'.format(db["season"]))
	return db["season"]

def new_welcome_message(season, welcome_message):
	"""Loads a new welcome message to the season list"""
	available_welcome_messages = db["welcome_message"]
	if season not in available_welcome_messages:
		print('{} must be added as a season first.'.format(season))
		return '{} must be added as a season first.'.format(season)

	if available_welcome_messages[season] is None:
		available_welcome_messages[season] = [welcome_message]
		db["welcome_message"] = available_welcome_messages
		print('{} created in {}'.format(welcome_message, season))
		return '{} created in {}'.format(welcome_message, season)

	available_welcome_messages[season].append(welcome_message)
	db["welcome_message"] = available_welcome_messages
	print('{} added to {}'.format(welcome_message, season))
	return '{} added to {}'.format(welcome_message, season)

def get_welcome_message(season):
	"""Returns a random welcome message from the current season"""
	seasonal_welcome_messages = db["welcome_message"][season]
	size = len(seasonal_welcome_messages)
	random_index = random.randrange(0, size)
	reply = seasonal_welcome_messages[random_index]
	print(reply)
	return reply

def update_rules_message(rules_message):
	db["rules_message"] = rules_message
	print(rules_message)
	reply = 'Successfull changed rules message to {}'
	return reply.format(rules_message)

def update_rules_dm(rules_dm):
	db["rules_dm"] = rules_dm
	print('length of rules_dm: {}'.format(len(rules_dm)))
	reply = 'Successfull changed rules dm to {}'
	return reply.format(rules_dm)

async def help_request(member):
	print('Help request from {}'.format(member.name))
	await member.send('Hi {}, I\'m RastaBot. How can I help?'.format(member.name))
	requests_list = db["requests_list"]
	dm_contents = ''
	for req in requests_list:
		desc = requests_list[req]
		dm_contents += '{rp}{r}: {d}\n'.format(rp = REQUEST_PREFIX, r = req, d = desc)
	await member.send(dm_contents)

@client.event
async def on_member_join(member):
	count_members()
	# TODO: Check against list of previously welcomed members
	# TODO: Add !debug_remove_user to clear welcomed members for testing
	print('{} joined the server'.format(member))
	rules_dm = db["rules_dm"]
	await member.send(rules_dm)
	guild = member.guild
	channel = guild.system_channel
	season = db["season"]
	reply = get_welcome_message(season)
	rules_message = db["rules_message"]
	await channel.send(reply.format(member.name))
	await channel.send(rules_message)

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

	if message.content.startswith(REQUEST_PREFIX):
		if message.content.startswith('{}help'.format(REQUEST_PREFIX)):
			await message.channel.send('{}, check your DM\'s for help.'.format(message.author.name))
			await help_request(message.author)

		if message.content.startswith('{}about'.format(REQUEST_PREFIX)):
			print('{}about request recieved from {}'.format(REQUEST_PREFIX, message.author))
			await message.author.send(about)

	if message.content.startswith('!'): # All commands for the bot
		bot_manager_role = False # Assume nothing

		for role in message.author.roles: # Find if the user is a BotManager
			role_str = str(role)
			if role_str.find('BotManager') != -1:
				bot_manager_role = True
			
		if bot_manager_role == False:
			await message.author.send('Please don\'t use ! at the start of messages.')
			return

		if bot_manager_role == True: # Commands for the BotManagers
			print('Command issued by BotManager {}'.format(message.author))

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

			if message.content.startswith('!update_rules_message'):
				new_rules_message = message.content[21:]
				reply = update_rules_message(new_rules_message)
				await message.channel.send(reply)

			if message.content.startswith('!update_rules_dm'):
				new_rules_dm = message.content[16:]
				reply = update_rules_dm(new_rules_dm)
				await message.channel.send(reply)

			if message.content.startswith('!keys'):
				keys = db.keys()
				print(keys)


client.run(DISCORD_TOKEN)
