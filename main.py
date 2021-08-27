"""
RastaBot developed by Trolan (Trevor Mathisen).

"""
import discord
import os
from replit import db
import count

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
REQUEST_PREFIX = '$' # Prefix for users to interact with bot
COMMAND_PREFIX = '!' # Prefix for managers to command the bot
about = db["about"] # Longwinded info about this bot
DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets
client = discord.Client(intents = intents)
role_army_id = int(os.environ['ROLE_ARMY_ID']) # Role ID: @Irie Army
role_actions_id = int(os.environ['ROLE_ACTIONS_ID']) # Role ID: @Actions
soil_grow_id = int(os.environ['SOIL_GROW_ID']) # Role ID: @Soil
hydro_grow_id = int(os.environ['HYDRO_GROW_ID']) # Role ID: @Soilless
coco_grow_id = int(os.environ['COCO_GROW_ID']) # Role ID: @Coco
rules_channel_id = int(os.environ['RULES_CHANNEL_ID']) # Channel ID: #rules_and_etiquiette
actions_rules_channel_id = int(os.environ['ACTIONS_RULES_CHANNEL_ID']) # Channel ID: #how-to-play
links_channel_id = int(os.environ['LINKS_CHANNEL_ID']) # Channel ID: #irie-genetics-links
action_rules = ''


#*****************************************************#
#  Function Group: Database Update Functions          #
#  Description: Functions to manually add keys and    #
#               values to the database. Used for      #
#               intiial setup on a new sever          #
#       Contains: command_db_update(key, value)       #
#                 command_db_delete(key)              #
#*****************************************************#
def command_db_update(key, value):
	"""Manual DB update processing. """
	db[key] = value
	return ('Added {}:{}'.format(key, value))

def command_db_delete(key):
	"""Manual DB key:value delete processing. Console confirmationr """
	response = input('Are you sure you want to delete {}?'.format(key)).lower()
	# This response/input is required in the console, an extra layer of security
	if response in ('yes', 'y'):
		del db[key]
		print('Delete {}'.format(key))
		return 'Deleted {}'.format(key)
	else:
		print('Negative response received. Did not delete {}'.format(key))
		return 'Negative response received. Did not delete {}'.format(key)

#*****************************************************#
#  Function Group: Database Update Functions          #
#  Description: Functions to manually add keys and    #
#               values to the database. Used for      #
#               intiial setup on a new sever          #
#       Contains: command_db_update(key, value)       #
#                 command_db_delete(key)              #
#*****************************************************#
async def help_request(channel, member):
	"""Retrieve all requests and send formatted message to channel"""
	print('Help request from {}'.format(member.name))
	await channel.send('Hi {}, I\'m RastaBot. How can I help?'.format(member.mention))
	requests_list = db["requests_list"] # Get loaded requests from db
	msg_contents = ''
	for req in requests_list: # read every key
		# TODO: enumerate()
		desc = requests_list[req] # read every value
		msg_contents += '{rp}{r}: {d}\n'.format(rp = REQUEST_PREFIX, r = req, d = desc)
	await channel.send(msg_contents)

async def commands_help_request(channel, member):
	"""Retrieve all commands and send formatted message to channel"""
	print('Commands help request from {}'.format(member.name))
	await channel.send('RastaBot commands available for {}'.format(member.mention))
	commands_list = db["commands_list"]
	msg_contents = ''
	for cmd in commands_list: # read every key
		# TODO: enumerate()
		desc = commands_list[cmd] # read every value
		msg_contents += '{cp}{c}: {d}\n'.format(cp = COMMAND_PREFIX, c = cmd, d = desc)
	await channel.send(msg_contents)

def get_about():
	"""Return about information (TODO)"""
	print('TODO: get_about()')
	return about

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
	random_index = db["welcome_message_index"] # "Random" is cycling through each one
	                                           # Appears more random
	if random_index != size - 1: # If not at the end
		random_index += 1 # Move to next welcome message
		db["welcome_message_index"] = random_index
	else:
		random_index = 0
		db["welcome_message_index"] = random_index
	reply = seasonal_welcome_messages[random_index] # Send from the seasonal batch
	print(reply)
	return reply

#*****************************************************#
#  Function Group: Welcome messages                   #
#  Description: Functions related to setting          #
#               getting or deleting welcome messages  #
#               rules messages and dm's and the       #
#               associated season                     #
#  Contains: set_welcome_message_season(season)       #
#            new_welcome_message(season)              #
#            get_welcome_message_season()             #
#         new_welcome_message(season, welcome_message)#
#            get_welcome_message(season)              #
#            update_rules_message(rules_message)      #
#            update_rules_dm(rules_dm)                #
#*****************************************************#
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

#*****************************************************#
#  Function Group: Bad words                          #
#  Description: Functions which process bad words     #
#  Contains: list_bad_words(channel)                  #
#            bad_words_check(message)                 #
#*****************************************************#
def sort_bad_words():
	"""Sorts list of bad words alphabetically and puts back in db"""
	bad_words_list = db["bad_word_list"]
	sorted_list = [ ] 
	for word in bad_words_list: # Transfer to simple list to .sort()
		sorted_list.append(word)
	sorted_list.sort()
	db["bad_word_list"] = sorted_list

async def list_bad_words(channel):
	"""Send a list of bad words to a channel"""
	reply = ''
	sort_bad_words()
	bad_words_list = db["bad_word_list"]
	for word in bad_words_list:
		reply += '{}, '.format(word)
	await channel.send(reply)

def bad_words_check(message):
	words_said = '' # Blank reply
	bad_word_check = db["bad_word_list"]
	for word in bad_word_check: # For every bad word we have
		if word in message.clean_content.lower(): # See if its in the message
			if words_said == '': # If it's the first word found, add it
				words_said += word
			else:
				words_said += ' or {}'.format(word) # or add to list if its not
	word_count = words_said.count(' or')

	if word_count != 1:
		words_said = words_said.replace(' or', ',', word_count - 1)
	
	return words_said # Send back {}, {} or {} of bad words

#*****************************************************#
#                      On ready:                      #
#                    Basic actions                    #
#                      Process:                       #
#      - Prints to console when ready                 #
#*****************************************************#
@client.event
async def on_ready(): # When ready
	print('We have logged in as {0.user}'.format(client))

#*****************************************************#
#               Member Join Processing:               #
#        Processes a new member to the server         #
#                      Process:                       #
#      - Counts every member                          #
#      - Checks if member was welcomed before         #
#      - Gets a welcome message based on season       #
#      - Adds welcomed member to welcomed list        #
#      - Sends the welcome message                    #
#*****************************************************#
@client.event
async def on_member_join(member):
	count.members()

	print('{} joined the server'.format(member))
	welcomed_members = db["welcomed_members"] # Find out who we welcomed

	if int(member.id) in welcomed_members: # Don't welcome people a second time
		return
	else:
		#rules_dm = str(db["rules_dm"])
		#await member.send(rules_dm.format(member.name, REQUEST_PREFIX)) # Send them a DM
		guild = member.guild
		channel = guild.system_channel
		season = db["season"]
		reply = get_welcome_message(season) # Get a semi-random welcome message
		#rules_message = db["rules_message"]
		welcomed_members.append(int(member.id)) # Note you've welcomed this person
		await channel.send(reply.format(member.mention, REQUEST_PREFIX)) # Send it
		#await channel.send(rules_message) #Only send one message for now

#*****************************************************#
#              Reaction Add Processing:               #
#            Reaction adds processed here             #
#                      Process:                       #
#     - Count every reaction                          #
#     - Loads reaction message from db                #
#     - Adds role based on reaction                   #
#     - TODO: Base roles on list (needs commands)     #
#*****************************************************#
@client.event
async def on_raw_reaction_add(payload):
	count.reactions()
	role_reaction_id = db["role_reaction_message"] # Message to watch for @Irie Army role
	action_reaction_id = db["action_reaction_message"] # Message to watch for @Actions role
	grow_reaction_id = db["grow_reaction_message"] # Message to watch for @Grow roles

	# TODO: Update to list driven menu
	if payload.message_id == int(role_reaction_id): # @Irie Army role reaction
		print('Role Reaction received from {}'.format(payload.member))
		
		if str(payload.emoji) == '✅':
			print('Received {}army_role reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			irie_army_role = irie_guild.get_role(role_army_id)
			await payload.member.add_roles(irie_army_role)
			print(payload.member.roles)
	
	elif payload.message_id == int(action_reaction_id): # @Actions role reaction
		print('Action Reaction received from {}'.format(payload.member))
		
		if str(payload.emoji) == '✅':
			print('Received {}action_role reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			actions_role = irie_guild.get_role(role_actions_id)
			await payload.member.add_roles(actions_role)
			print(payload.member.roles)

	elif payload.message_id == int(grow_reaction_id): # Grow Roles role reaction
		print('Grow Reaction received from {}'.format(payload.member))
		
		if str(payload.emoji) == '🌳': # @Soil
			print('Received {}grow_role reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			soil_role = irie_guild.get_role(soil_grow_id)
			await payload.member.add_roles(soil_role)
			print(payload.member.roles)

		if str(payload.emoji) == '💦': # @Soilless
			print('Received {}grow_role reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			hydro_role = irie_guild.get_role(hydro_grow_id)
			await payload.member.add_roles(hydro_role)
			print(payload.member.roles)	

		if str(payload.emoji) == '🥥': # @Coco
			print('Received {}grow_role reaction from {}'.format(REQUEST_PREFIX, payload.member))
			irie_guild = payload.member.guild
			coco_role = irie_guild.get_role(coco_grow_id)
			await payload.member.add_roles(coco_role)
			print(payload.member.roles)

#*****************************************************#
#            Reaction Removal Processing:             #
#          Reaction removals processed here           #
#                      Process:                       #
#     - Count every reaction                          #
#     - Loads guild object                            #
#     - Strips user_id from payload                   #
#     - Loads member from user_id and guild           #
#     - Loads reaction message from db                #
#     - Removes role based on reaction                #
#*****************************************************#
@client.event
async def on_raw_reaction_remove(payload):
	count.reactions()

	# Member object not passed, so load it based on the message id
	irie_guild = client.get_guild(879408430283128843)
	split_payload = str(payload).split()
	user_id = split_payload[2][8:]
	member = irie_guild.get_member(int(user_id))
	
	role_reaction_id = db["role_reaction_message"] # Message to watch for @Irie Army role
	action_reaction_id = db["action_reaction_message"] # Message to watch for @Actions role
	grow_reaction_id = db["grow_reaction_message"] # Message to watch for @Grow roles

	print('on_raw_reaction_remove(): member: {}'.format(member))

	if payload.message_id == role_reaction_id: # @Irie Army role reaction

		print('Role Reaction removal received from {}'.format(member))

		if str(payload.emoji) == '✅':
			print('Received {}army_role removal reaction from {}'.format(REQUEST_PREFIX, member))
			irie_army_role = irie_guild.get_role(role_army_id)
			await member.remove_roles(irie_army_role)
			print(member.roles)

	elif payload.message_id == action_reaction_id: # @Actions role reaction

		print('Action Reaction removal received from {}'.format(member))
		
		if str(payload.emoji) == '✅':
			print('Received {}action_role removal reaction from {}'.format(REQUEST_PREFIX, member))
			actions_role = irie_guild.get_role(role_actions_id)
			await member.remove_roles(actions_role)
			print(member.roles)
	
	elif payload.message_id == grow_reaction_id: # Grow Role role reaction

		print('Action Reaction removal received from {}'.format(member))
		
		if str(payload.emoji) == '🌳': # Soil
			print('Received {}action_role removal reaction from {}'.format(REQUEST_PREFIX, member))
			soil_role = irie_guild.get_role(soil_grow_id)
			await member.remove_roles(soil_role)
			print(member.roles)
		
		if str(payload.emoji) == '💦': # Soilless
			print('Received {}action_role removal reaction from {}'.format(REQUEST_PREFIX, member))
			hydro_role = irie_guild.get_role(hydro_grow_id)
			await member.remove_roles(hydro_role)
			print(member.roles)

		if str(payload.emoji) == '🥥': # Coco
			print('Received {}action_role removal reaction from {}'.format(REQUEST_PREFIX, member))
			coco_role = irie_guild.get_role(coco_grow_id)
			await member.remove_roles(coco_role)
			print(member.roles)

#*****************************************************#
#                 Message Processing:                 #
#     Channel and Private messages processed here     #
#                      Process:                       #
#     - Count every message                           #
#     - Don't process the bot's own message           #
#     - Tell DM senders DM's aren't supported         #
#     - Process ping/pong checks                      #
#     - Check if the user is a BotManager             #
#     - Run message through bad word detector         #
#                       (if not a bot manager         #
#     - Then the message is processed                 #
#           - Requests: Require @IrieArmy role        #
#           - Commands: Require @BotManager role      #
#*****************************************************#
@client.event
async def on_message(message): # On every message
	count.message() # Count it
	
	if message.author == client.user: # Cancel own message
		return

	if str(message.channel.type) == 'private': # DM's aren't supported, return
		await message.author.send('Sorry, DM\'s to RastaBot are not currently supported.')
		return

	if message.content.startswith('ping') or message.content.startswith('Ping'): # Simple test the bot is working
		await message.channel.send('pong!')

	bot_manager_role = False # Assume nothing

	for role in message.author.roles: # Find if the user is a BotManager
		role_str = str(role)
		if role_str.find('BotManager') != -1:
			bot_manager_role = True

	# You can't filter bad_words from commands and be able to add/remove bad_words with commands
	if not message.content.startswith('{}'.format(COMMAND_PREFIX)) and bot_manager_role == True: 
		bad_words_in_message = bad_words_check(message)
		if bad_words_in_message != '':
			await message.channel.send('Hey {}, watch your mouth. We don\'t mention {} around here.'.format(message.author.mention, bad_words_in_message))
			return

	if message.content.startswith(REQUEST_PREFIX): # Route Requests
		irie_army_role = False # Assume nothing

		for role in message.author.roles: # Find if the user is a BotManager
			role_str = str(role)
			if role_str.find('Irie Army') != -1:
				irie_army_role = True
			
		if irie_army_role == False:
			await message.author.send('Please read the #rules-and-etiquette room and react to the appropriate message to add the @Irie Army role')
			return

		if irie_army_role == True: # Commands for the users
			if message.content.startswith('{}help'.format(REQUEST_PREFIX)):
				await help_request(message.channel, message.author)

			if message.content.startswith('{}about'.format(REQUEST_PREFIX)):
				print('{}about request recieved from {}'.format(REQUEST_PREFIX, message.author))
				about_msg = get_about() # TODO
				await message.channel.send(about_msg)
				await message.channel.send('RastaBot has processed {} users, {} messages and {} reactions.'.format(db["members"], db["messages"], db["reactions"]))
			
			if message.content.startswith('{}rules'.format(REQUEST_PREFIX)):
				print('{}rules request received from {}'.format(REQUEST_PREFIX, message.author))
				rules_msg_id = db["rules_message_id"]
				member = message.author
				rules_channel = member.guild.get_channel(rules_channel_id)
				rules_msg = await rules_channel.fetch_message(rules_msg_id)
				await member.send(rules_msg.content)
				await message.channel.send('{}, you can find the rules in the {} channel and I\'ve sent them as a DM as well. Let the mods know if you need any help or have questions.'.format(member.mention, rules_channel.mention))

			if (message.content.startswith('{}action_rules'.format(REQUEST_PREFIX))) or (message.content.startswith('{}waffle_rules'.format(REQUEST_PREFIX))) or (message.content.startswith('{}actions_rules'.format(REQUEST_PREFIX))) or (message.content.startswith('{}waffles_rules'.format(REQUEST_PREFIX))):
				print('{}action/waffle_rules request received from {}'.format(REQUEST_PREFIX, message.author))
				actions_rules_msg_id = db["actions_rules_message_id"]
				member = message.author
				actions_rules_channel = member.guild.get_channel(actions_rules_channel_id)
				actions_rules_msg = await actions_rules_channel.fetch_message(actions_rules_msg_id)
				await member.send(actions_rules_msg.content)
				await message.channel.send('{}, rules for actions and waffles can be found in the {} channel and I\'ve sent them as a DM as well. Let the mods know if you need any help or have questions.'.format(member.mention, actions_rules_channel.mention))
				
			if message.content.startswith('{}links'.format(REQUEST_PREFIX)):
				print('{}links request received from {}'.format(REQUEST_PREFIX, message.author))
				links_msg_id = db["links_message_id"]
				member = message.author
				links_channel = member.guild.get_channel(links_channel_id)
				links_msg = await links_channel.fetch_message(links_msg_id)
				await member.send(links_msg.content)
				await message.channel.send('{}, I sent you a copy of the links from {}. Let us know if something should be added!'.format(member.mention, links_channel.mention))

	if message.content.startswith(COMMAND_PREFIX): # All commands for the bot			
		if bot_manager_role == False:
			await message.author.send('Please don\'t use {} at the start of messages.'.format(COMMAND_PREFIX))
			return

		if bot_manager_role == True: # Commands for the BotManagers
			print('Command issued by BotManager {}'.format(message.author))

			if message.content.startswith('{}help'.format(COMMAND_PREFIX)):
				await commands_help_request(message.channel, message.author)

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
				split_message = message.content.split()
				new_rules_dm = split_message[2:]
				new_rules_dm = ' '.join(new_rules_dm)
				reply = update_rules_dm(new_rules_dm)
				await message.channel.send(reply)

			if message.content.startswith('{}keys'.format(COMMAND_PREFIX)):
				keys = db.keys()
				print(keys)
				await message.channel.send(keys)

			if message.content.startswith('{}clear_welcomed_members'.format(COMMAND_PREFIX)):
				welcomed_members = ['']
				db["welcomed_members"] = welcomed_members
				await message.channel.send('Done')
			
			if message.content.startswith('{}new_role_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["role_reaction_message"] = int(new_message_id)
				await message.channel.send('Done')

			if message.content.startswith('{}new_action_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["action_reaction_message"] = int(new_message_id)
				await message.channel.send('Done')

			if message.content.startswith('{}new_grow_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["grow_reaction_message"] = int(new_message_id)
				await message.channel.send('Done')

			if message.content.startswith('{}new_rules_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["rules_message_id"] = int(new_message_id)
				await message.channel.send('Done')

			if message.content.startswith('{}new_actions_rules_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["actions_rules_message_id"] = int(new_message_id)
				await message.channel.send('Done')

			if message.content.startswith('{}new_links_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["links_message_id"] = int(new_message_id)
				await message.channel.send('Done')

			if message.content.startswith('{}db_update'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				db_key = split_message[1]
				db_value = split_message[2]
				reply = command_db_update(db_key, db_value)
				await message.channel.send(reply)

			if message.content.startswith('{}db_delete'.format(COMMAND_PREFIX)):
				db_key = message.content[11:]
				reply = command_db_delete(db_key)
				await message.channel.send(reply)

			if message.content.startswith('{}add_bad_word'.format(COMMAND_PREFIX)):
				bad_word_list = db["bad_word_list"]
				bad_word_list.append(message.clean_content[14:])
				db["bad_word_list"] = bad_word_list
				sort_bad_words()
				await message.channel.send('Added {} to bad_word_list'.format(bad_word_list[-1]))

			if message.content.startswith('{}list_bad_words'.format(COMMAND_PREFIX)):
				await list_bad_words(message.channel)

			if message.content.startswith('{}delete_bad_word'.format(COMMAND_PREFIX)):
				to_delete = message.clean_content[17:]
				bad_word_list = db["bad_word_list"]
				bad_word_list.remove(to_delete)
				db["bad_word_list"] = bad_word_list
				await message.channel.send('Deleted {} from the list'.format(to_delete))
				await list_bad_words(message.channel)
				

client.run(DISCORD_TOKEN)
