"""
RastaBot developed by Trolan (Trevor Mathisen).

"""
import discord
import os
from replit import db
import random
import count

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
REQUEST_PREFIX = '$' # Prefix for users to interact with bot
COMMAND_PREFIX = '!' # Prefix for managers to command the bot
about = db["about"] # Longwinded info about this bot
DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets
client = discord.Client(intents = intents)
role_vet_id = 880475302420152351
role_army_id = 880475456841871401
requests_avail = {
	'help':'This request sends a DM containing all possible requests from a user',
	'links':'(TODO)Sends a user a DM with links to Irie Genetics beans, Grow From Your Heart podcast locations and other important links',
	'rules':'(TODO)DM the user the current rules message',
	'waffle_rules':'(TODO)Sends a user a DM with the rules of waffles',
	'action_rules':'(TODO)Sends a user a DM with the rules of actions',
	'about':'Sends a user a DM with information about RastaBot'
}

db["requests_list"] = requests_avail

def set_welcome_message_season(season):
	"""Sets the season for the welcome message service"""
	db["season"] = season
	print('Season updated to {}'.format(season))
	reply = 'Season updated to {}'.format(season)
	return reply

def new_welcome_message_season(season):
	"""Created a new season to add welcome messages to"""
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
	if season not in available_welcome_messages: # See if it has been added
		print('{} must be added as a season first.'.format(season))
		return '{} must be added as a season first.'.format(season)

	if available_welcome_messages[season] is None: # If empty season, add it as first value
		available_welcome_messages[season] = [welcome_message]
		db["welcome_message"] = available_welcome_messages
		print('{} created in {}'.format(welcome_message, season)) # Show it was created
		return '{} created in {}'.format(welcome_message, season)

	available_welcome_messages[season].append(welcome_message) # Append to current season
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
	"""Updates built in rules_message posted in system_channel after welcome_message"""
	db["rules_message"] = rules_message
	print(rules_message)
	reply = 'Successfull changed rules message to {}'
	return reply.format(rules_message)

def update_rules_dm(rules_dm):
	"""Updates built in rules_dm sent to new users after welcome_message"""
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
	count.members()
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
async def on_raw_reaction_add(payload):
	count.reactions()
	if payload.message_id == 880475873961185350:
		print('Role Reaction received from {}'.format(payload.member))
		
		if str(payload.emoji) == '1️⃣':
			print('Received {}army_role reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			irie_army_role = irie_guild.get_role(role_army_id)
			await payload.member.add_roles(irie_army_role)
			print(payload.member.roles)

		if str(payload.emoji) == '2️⃣':
			print('Received {}veteran reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			irie_vet_role = irie_guild.get_role(role_vet_id)
			await payload.member.add_roles(irie_vet_role)
			print(payload.member.roles)			

@client.event
async def on_raw_reaction_remove(payload):
	count.reactions()
	if payload.message_id == 880475873961185350:
		split_payload = str(payload).split()
		user_id = split_payload[2][8:]
		irie_guild = client.get_guild(879408430283128843)
		member = irie_guild.get_member(int(user_id))
		print('Role Reaction removal received from {}'.format(member))

		if str(payload.emoji) == '1️⃣':
			print('Received {}army_role removal reaction from {}'.format(REQUEST_PREFIX, member))
			irie_army_role = irie_guild.get_role(role_army_id)
			await member.remove_roles(irie_army_role)
			print(member.roles)

		if str(payload.emoji) == '2️⃣':
			print('Received {}veteran removal reaction from {}'.format(REQUEST_PREFIX, member))
			irie_vet_role = irie_guild.get_role(role_vet_id)
			await member.remove_roles(irie_vet_role)
			print(member.roles)	

		
@client.event
async def on_message(message): # On every message
	count.message() # Count it
	
	if message.author == client.user: # Cancel own message
		return

	if message.content.startswith('ping'): # Simple test the bot is working
		await message.channel.send('pong!')

	if message.content.startswith(REQUEST_PREFIX): # Route Requests
		irie_army_role = False # Assume nothing

		for role in message.author.roles: # Find if the user is a BotManager
			role_str = str(role)
			if role_str.find('Irie Army') != -1:
				irie_army_role = True
			
		if irie_army_role == False:
			await message.author.send('Please read the #rules-and-etiquette room and react to the appropriate message to add the @Irie Army role')
			return

		if irie_army_role == True: # Commands for the BotManagers
			if message.content.startswith('{}help'.format(REQUEST_PREFIX)):
				await message.channel.send('{}, check your DM\'s for help.'.format(message.author.name))
				await help_request(message.author)

			if message.content.startswith('{}veteran'.format(REQUEST_PREFIX)):
				print('Received {}veteran request from {}'.format(REQUEST_PREFIX, message.author))
				irie_guild = message.author.guild
				irie_vet_role = irie_guild.get_role(role_vet_id)
				await message.author.add_roles(irie_vet_role)
				print(message.author.roles)

			if message.content.startswith('{}army_role'.format(REQUEST_PREFIX)):
				print('Received {}army_role request from {}'.format(REQUEST_PREFIX, message.author))
				irie_guild = message.author.guild
				irie_army_role = irie_guild.get_role(role_army_id)
				await message.author.add_roles(irie_army_role)
				print(message.author.roles)

			if message.content.startswith('{}about'.format(REQUEST_PREFIX)):
				print('{}about request recieved from {}'.format(REQUEST_PREFIX, message.author))
				await message.author.send(about)

	if message.content.startswith(COMMAND_PREFIX): # All commands for the bot
		bot_manager_role = False # Assume nothing

		for role in message.author.roles: # Find if the user is a BotManager
			role_str = str(role)
			if role_str.find('BotManager') != -1:
				bot_manager_role = True
			
		if bot_manager_role == False:
			await message.author.send('Please don\'t use {} at the start of messages.'.format(COMMAND_PREFIX))
			return

		if bot_manager_role == True: # Commands for the BotManagers
			print('Command issued by BotManager {}'.format(message.author))

			if message.content.startswith('{}get_season'.format(COMMAND_PREFIX)):
				reply = get_welcome_message_season()
				await message.channel.send(reply)
			
			if message.content.startswith('{}set_season'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				reply = set_welcome_message_season(split_message[1])
				await message.channel.send(reply)

			if message.content.startswith('{}new_season'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				updated_season = split_message[1] # {}new_season [1]
				reply = new_welcome_message_season(updated_season)
				print(get_welcome_message_season(), '| {}'.format(reply))
				await message.channel.send(reply)

			if message.content.startswith('{}new_welcome_message'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				updated_welcome_message_season = split_message[1]
				updated_welcome_message = split_message[2:]
				updated_welcome_message = ' '.join(updated_welcome_message)
				reply = new_welcome_message(updated_welcome_message_season, updated_welcome_message)
				print(reply)
				await message.channel.send(reply)
			
			if message.content.startswith('{}list_welcome_messages'.format(COMMAND_PREFIX)):
				current_season = db["season"]
				seasonal_welcome_messages = db["welcome_message"][current_season]
				for i in range(len(seasonal_welcome_messages)):
					await message.channel.send('{}: {}'.format(i, seasonal_welcome_messages[i]))

			if message.content.startswith('{}delete_welcome_message'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				index_to_delete = int(split_message[1])
				current_season = db["season"]
				seasonal_welcome_messages = db["welcome_message"][current_season]
				deleted_welcome_message = seasonal_welcome_messages[index_to_delete]
				del seasonal_welcome_messages[index_to_delete]
				db["welcome_message"][current_season] = seasonal_welcome_messages
				print('Deleted {}: {} from {}'.format(index_to_delete, deleted_welcome_message, current_season))
				await message.channel.send('Deleted {}: {} from {}'.format(index_to_delete, deleted_welcome_message, current_season))

			if message.content.startswith('{}update_rules_message'.format(COMMAND_PREFIX)):
				new_rules_message = message.content[21:]
				reply = update_rules_message(new_rules_message)
				await message.channel.send(reply)

			if message.content.startswith('{}update_rules_dm'.format(COMMAND_PREFIX)):
				new_rules_dm = message.content[16:]
				reply = update_rules_dm(new_rules_dm)
				await message.channel.send(reply)

			if message.content.startswith('{}keys'.format(COMMAND_PREFIX)):
				keys = db.keys()
				print(keys)

client.run(DISCORD_TOKEN)
