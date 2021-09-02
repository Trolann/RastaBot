"""
RastaBot developed by Trolan (Trevor Mathisen). 
"""
import discord
import os
from replit import db
import count
import rastabot
import bad_words
import welcome_messages
import rules_messages

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)
irie_guild = ''
rules_channel = ''
actions_rules_channel = ''
yoga_rules_channel = ''
links_channel = ''
REQUEST_PREFIX = db["REQUEST_PREFIX"] # Prefix for users to interact with bot
COMMAND_PREFIX = db["COMMAND_PREFIX"] # Prefix for managers to command the bot
DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets
IRIE_GUILD_ID = int(os.environ['IRIE_GUILD_ID']) # Stored in secrets

#*****************************************************#
#                      On ready:                      #
#                    Basic actions                    #
#                      Process:                       #
#      - Prints to console when ready                 #
#*****************************************************#
@client.event
async def on_ready(): # When ready
	global irie_guild
	global rules_channel
	global actions_rules_channel
	global links_channel
	global yoga_rules_channel
	irie_guild = client.get_guild(IRIE_GUILD_ID)
	print(irie_guild)
	rules_channel = irie_guild.get_channel(int(db["rules_channel_id"]))
	print(rules_channel)
	actions_rules_channel = irie_guild.get_channel(int(db["actions_rules_channel_id"]))
	print(actions_rules_channel)
	links_channel = irie_guild.get_channel(int(db["links_channel_id"]))
	print(links_channel)
	yoga_rules_channel = irie_guild.get_channel(int(db["yoga_channel_id"]))
	print(yoga_rules_channel)
	print(rastabot.update_all())
	print('We have logged in as {0.user}'.format(client))
	was_killed = bool(db["system_killed"])
	killed_by = str(db["system_killed_by"])

	if was_killed:
		print('*' * 35)
		print('SYSTEM RECOVERED FROM KILL COMMAND')
		print('System kill issued by {}'.format(killed_by))
		try:
			db["system_killed"] = bool(False)
			db["system_killed_by"] = ''
			print('Database successfully updated')
			print('System reset')
		except:
			print('Error updating database!')
		print('*' * 35)

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
		rules_dm = str(db["rules_dm"])
		await member.send(rules_dm.format(member.name, REQUEST_PREFIX)) # Send them a DM
		#guild = member.guild
		channel = irie_guild.system_channel
		season = db["season"]
		reply = welcome_messages.get_message(season) # Get a semi-random welcome message
		#rules_message = db["rules_message"]
		welcomed_members.append(int(member.id)) # Note you've welcomed this person
		db["welcomed_members"] = welcomed_members
		await channel.send(reply.format(member.mention, REQUEST_PREFIX)) # Send it
		#await channel.send(rules_message) # Only send one message for now

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

	reaction_dict = db["role_reaction_message_list"]
	message_id = str(payload.message_id)

	if payload.emoji.is_custom_emoji():
		emoji_id = str(payload.emoji.name)
	else:
		emoji_id = payload.emoji.name

	if message_id in reaction_dict:	
		for key in reaction_dict[message_id]:
			if key == emoji_id:
				role_id = reaction_dict[message_id][key]
				role = irie_guild.get_role(int(role_id))
				await payload.member.add_roles(role)
				print('{} reaction received. Added {} to {}'.format(emoji_id, role, payload.member))

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
	reaction_dict = db["role_reaction_message_list"]
	user_id = int(payload.user_id)
	message_id = str(payload.message_id)
	member = irie_guild.get_member(user_id)

	if payload.emoji.is_custom_emoji():
		emoji_id = str(payload.emoji.name)
	else:
		emoji_id = payload.emoji.name

	if message_id in reaction_dict:
		for key in reaction_dict[message_id]:
			if key == emoji_id:
				role_id = reaction_dict[message_id][key]
				role = irie_guild.get_role(int(role_id))
				await member.remove_roles(role)
				print('{} removal reaction received. Removed {} from {}'.format(emoji_id, role, member))

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

	if message.content.lower().startswith('ping'): # Simple test the bot is working
		print('ping?/pong! processed from {}'.format(message.author))
		await message.channel.send('pong!')

	if str(message.channel.type) == 'private':
		member = irie_guild.get_member(message.author.id)
		channel = member
		print('MEMBER: {}'.format(member))
	else:
		member = message.author
		channel = message.channel

	welcomed_members = db["welcomed_members"] # Pull up welcomed members
	if int(member.id) not in welcomed_members: # See if this person has been welcomed
		welcomed_members.append(int(member.id))
		db["welcomed_members"] = welcomed_members
		# If they're sending messages but haven't been welcomed, they joined the server
		# before the bot did. This will prevent us from welcoming them if they leave/join

	#TODO: Break out into rastabot_config
	bot_manager = False
	if message.content.startswith('{}'.format(COMMAND_PREFIX)):
		for id in member.roles:
			if id == irie_guild.get_role(int(db["bot_manager_id"])):
				bot_manager = True
	
	if str(message.author) == 'Trolan#7880':
		bot_manager = True

	# TODO: bad_words.check_message(message) return reply
	# You can't filter bad_words from commands and be able to add/remove bad_words with commands
	if not message.content.startswith('{}delete_bad_word'.format(COMMAND_PREFIX)) and not bot_manager: 
		# Process bad words if it's not a command from a BotManager or not a DM
		bad_words_in_message = bad_words.check_message(message)
		if bad_words_in_message != '':
			await channel.send('Hey {}, watch your mouth. We don\'t mention {} around here.'.format(member.mention, bad_words_in_message))
			return

	try:
		if message.clean_content[0] not in (REQUEST_PREFIX, COMMAND_PREFIX):
			return
	except:
		return

	# # This loads the trigger, message content and clean versions to support
	# # DM's and messages within channels using the same functions
	# if message.clean_content.find(' ') == -1:
	# 	trigger = message.clean_content[0:]
	# else:
	# 	trigger = message.clean_content[0:message.clean_content.find(' ') + 1]
	# content = message.content[message.content.find(' ') + 1:]
	# clean_content = message.clean_content[message.clean_content.find(' ') + 1:]
	# print('(DEBUG) Trigger: {}'.format(trigger))

	# # This is needed to have the help messages be formatted differently
	# # If REQUEST_PREFIX + 2/3 of these words are said first...
	# actions_or_waffle_request = 0
	# for word in ('action', 'waffle', 'rule'):
	# 	if trigger.find(word) != -1:
	# 		actions_or_waffle_request += 1
	# if actions_or_waffle_request == 2:
	# 	trigger = '{}action_rules/actions_rules'.format(trigger[0])

	# # We know it's a request
	# if trigger[1:] in db["requests_list"].keys() or (trigger[1:] in db["commands_list"].keys() and bot_manager):
	# 	print('(DEBUG) process_message(request, member, content, clean_content)')
	# 	print('(DEBUG) process_message({}, {}, {}, {})'.format(trigger, member, content, clean_content))
	# 	reply = rastabot.process_message(trigger, member, content, clean_content)
	# 	if type(reply) is list:
	# 		print('(DEBUG) Processing a list')
	# 		for i in range(len(reply)):
	# 			if reply[i] is not None:
	# 				await channel.send(reply[i])
	# 	else:
	# 		print('(DEBUG) Processing a non-list')
	# 		if reply is not None:
	# 			await channel.send(reply)
	# 	# REMOVE WHEN DONE ADDING NEW COMMANDS
	# 	# PREVENTS FURTHER COMMANDS FROM BEING RAN
	# 	if reply is not None:
	# 		return

	if message.content.startswith(REQUEST_PREFIX): # Route Requests

		if message.content.startswith('{}help'.format(REQUEST_PREFIX)):
			reply = rastabot.help_request(message.author)
			await channel.send(reply)

		if message.content.startswith('{}about'.format(REQUEST_PREFIX)):
			print('{}about request recieved from {}'.format(REQUEST_PREFIX, member))
			about_msg = rastabot.get_about()
			for i in range(len(about_msg)):
	 			if about_msg[i] is not None:
	 				await channel.send(about_msg[i])
		
		if message.content.startswith('{}rules'.format(REQUEST_PREFIX)):
			print('{}rules request received from {}'.format(REQUEST_PREFIX, member))
			rules_msg_id = db["rules_message_id"]
			rules_msg = await rules_channel.fetch_message(rules_msg_id)
			await member.send(rules_msg.content)
			await channel.send('{}, you can find the rules in the {} channel and I\'ve sent them as a DM as well. Let the mods know if you need any help or have questions.'.format(member.mention, rules_channel.mention))

		if (message.content.startswith('{}'.format(REQUEST_PREFIX))) and ((message.content.find('action') != -1 or message.content.find('waffle') != -1) and message.content.find('rule') != -1):
			print('{}action/waffle_rules request received from {}'.format(REQUEST_PREFIX, member))
			actions_rules_msg_id = db["actions_rules_message_id"]
			actions_rules_msg = await actions_rules_channel.fetch_message(actions_rules_msg_id)
			await member.send(actions_rules_msg.content)
			await channel.send('{}, rules for actions and waffles can be found in the {} channel and I\'ve sent them as a DM as well. Let the mods know if you need any help or have questions.'.format(member.mention, actions_rules_channel.mention))

		if message.content.startswith('{}yoga'.format(REQUEST_PREFIX)):
			print('{}yoga request received from {}'.format(REQUEST_PREFIX, member))
			yoga_rules_msg_id = int(db["yoga_message_id"])
			yoga_rules_msg = await yoga_rules_channel.fetch_message(yoga_rules_msg_id)
			await member.send(yoga_rules_msg.content)
			await channel.send('{}, information about Stoner Yoga can be found in the {} channel and I\'ve sent them as a DM as well. Let the mods know if you need any help or have questions.'.format(member.mention, yoga_rules_channel.mention))
			
			
		if message.content.startswith('{}links'.format(REQUEST_PREFIX)):
			print('{}links request received from {}'.format(REQUEST_PREFIX, member))
			links_msg_id = db["links_message_id"]
			links_msg = await links_channel.fetch_message(links_msg_id)
			await member.send(links_msg.content)
			await channel.send('{}, I sent you a copy of the links from {}. Let us know if something should be added!'.format(member.mention, links_channel.mention))

	if message.content.startswith(COMMAND_PREFIX): # All commands for the bot			
		if bot_manager == False:
			print('{} command attempted by {}'.format(COMMAND_PREFIX, member))
			return

		if bot_manager == True: # Commands for the BotManagers
			print('Command issued by BotManager {}'.format(member))

			if message.content.startswith('{}help'.format(COMMAND_PREFIX)):
				reply = rastabot.help_commands(member)
				await channel.send(reply)

			if message.content.startswith('{}get_season'.format(COMMAND_PREFIX)):
				reply = welcome_messages.get_season()
				await channel.send(reply)
			
			if message.content.startswith('{}set_season'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				reply = welcome_messages.set_season(split_message[1])
				await channel.send(reply)

			if message.content.startswith('{}new_season'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				updated_season = split_message[1] # {}new_season [1]
				reply = welcome_messages.new_season(updated_season)
				print(welcome_messages.get_season(), '| {}'.format(reply))
				await channel.send(reply)

			if message.content.startswith('{}new_welcome_message'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				updated_welcome_message_season = split_message[1]
				updated_welcome_message = split_message[2:]
				updated_welcome_message = ' '.join(updated_welcome_message)
				reply = welcome_messages.new_message(updated_welcome_message_season, updated_welcome_message)
				print('Welcome message added by {}. {}'.format(member.name, reply))
				await channel.send(reply)
			
			if message.content.startswith('{}list_welcome_messages'.format(COMMAND_PREFIX)):
				current_season = db["season"]
				seasonal_welcome_messages = db["welcome_message"][current_season]
				for i in range(len(seasonal_welcome_messages)):
					await channel.send('{}: {}'.format(i, seasonal_welcome_messages[i]))

			if message.content.startswith('{}delete_welcome_message'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				index_to_delete = int(split_message[1])
				current_season = db["season"]
				seasonal_welcome_messages = db["welcome_message"][current_season]
				deleted_welcome_message = seasonal_welcome_messages[index_to_delete]
				del seasonal_welcome_messages[index_to_delete]
				db["welcome_message"][current_season] = seasonal_welcome_messages
				print('Deleted {}: {} from {}'.format(index_to_delete, deleted_welcome_message, current_season))
				await channel.send('Deleted {}: {} from {}'.format(index_to_delete, deleted_welcome_message, current_season))

			if message.content.startswith('{}update_rules_message'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				if len(split_message) != 2:
					await channel.send('Usage: {}update_rules_message [msg_id]'.format(COMMAND_PREFIX))
					return
				msg_id = int(split_message[1])
				new_rules_message = await rules_channel.fetch_message(msg_id)
				reply = rules_messages.update_message(new_rules_message)
				await channel.send(reply)

			if message.content.startswith('{}update_rules_dm'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_rules_dm = split_message[1:]
				new_rules_dm = ' '.join(new_rules_dm)
				reply = rules_messages.update_dm(new_rules_dm)
				await channel.send(reply)

			if message.content.startswith('{}keys'.format(COMMAND_PREFIX)):
				keys = db.keys()
				print(keys)
				await channel.send(keys)

			if message.content.startswith('{}clear_welcomed_members'.format(COMMAND_PREFIX)):
				welcomed_members = ['']
				db["welcomed_members"] = welcomed_members
				await channel.send('Done')

			if message.content.startswith('{}new_action_message_id'.format(COMMAND_PREFIX)):
				#TODO: REMOVE
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["action_reaction_message"] = int(new_message_id)
				await channel.send('Done')

			if message.content.startswith('{}new_rules_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["rules_message_id"] = int(new_message_id)
				await channel.send('Done')

			if message.content.startswith('{}new_actions_rules_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["actions_rules_message_id"] = int(new_message_id)
				await channel.send('Done')

			if message.content.startswith('{}new_links_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["links_message_id"] = int(new_message_id)
				await channel.send('Done')

			if message.content.startswith('{}new_yoga_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["yoga_message_id"] = int(new_message_id)
				await channel.send('Done')

			if message.content.startswith('{}db_update'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				db_key = split_message[1]
				db_value = split_message[2]
				reply = rastabot.command_db_update(db_key, db_value)
				await channel.send(reply)

			if message.content.startswith('{}db_delete'.format(COMMAND_PREFIX)):
				db_key = message.content[11:]
				reply = rastabot.command_db_delete(db_key)
				await channel.send(reply)

			if message.content.startswith('{}add_bad_word'.format(COMMAND_PREFIX)):
				bad_word_list = db["bad_word_list"]
				bad_word_list.append(message.clean_content[14:])
				db["bad_word_list"] = bad_word_list
				await channel.send('Added {} to bad_word_list'.format(bad_word_list[-1]))

			if message.content.startswith('{}list_bad_words'.format(COMMAND_PREFIX)):
				reply = bad_words.list()
				await channel.send(reply)

			if message.content.startswith('{}delete_bad_word'.format(COMMAND_PREFIX)):
				to_delete = message.clean_content[17:]
				bad_word_list = db["bad_word_list"]
				bad_word_list.remove(to_delete)
				db["bad_word_list"] = bad_word_list
				await channel.send('Deleted {} from the list'.format(to_delete))
				bad_words_reply = bad_words.list()
				await channel.send(bad_words_reply)

		if message.content.startswith('{}new_reaction_message'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 2:
				await channel.send('Usage: {}new_reaction_message [msg_id]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			db_dict = db["role_reaction_message_list"]
			db_dict.update({msg_id:''})
			db["role_reaction_message_list"] = db_dict
			await channel.send('Added {} to messages to monitor for'.format(msg_id))

		if message.content.startswith('{}delete_reaction_message'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 2:
				await channel.send('Usage: {}delete_reaction_message [msg_id]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			db_dict = db["role_reaction_message_list"]
			del db_dict[msg_id]
			db["role_reaction_message_list"] = db_dict
			await channel.send('Deleted {} from messages to monitor for'.format(msg_id))

		if message.content.startswith('{}new_role_reaction'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 4:
				await channel.send('Usage: {}new_role_reaction [msg_id] [emoji] [role_id]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			emoji = split_message[2]
			role_id = split_message[3]
			db_dict = db["role_reaction_message_list"]

			if len(emoji) > 1:
				emoji_id = emoji_id = str(emoji[2:emoji.rfind(':')])
			else:
				emoji_id = emoji

			if msg_id not in db_dict:
				await channel.send('{} not found, try again'.format(msg_id))
				return

			if db_dict[msg_id] == '':
				db_dict[msg_id] = {emoji_id:role_id}
				await channel.send('Added {}:{} to {}'.format(emoji_id, role_id, msg_id))
			else:
				db_dict[msg_id].update({emoji_id:role_id})
				await channel.send('Added {}:{} to {}'.format(emoji_id, role_id, msg_id))
			db["role_reaction_message_list"] = db_dict

			await channel.send('Role reactions available for message {}'.format(msg_id))
			for emoji in db_dict[msg_id]:
				await channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = irie_guild.get_role(int(db_dict[msg_id][emoji])), ri = db_dict[msg_id][emoji]))

		# TODO: Copy role reaction [old_msg_id] [new_msg_id]
	
		if message.content.startswith('{}delete_role_reaction'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 3:
				await channel.send('Usage: {}new_role_reaction [msg_id] [emoji]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			emoji_id = split_message[2]
			db_dict = db["role_reaction_message_list"]

			if msg_id not in db_dict:
				await channel.send('{} not found, try again'.format(msg_id))
				return

			if emoji_id in db_dict[msg_id]:
				del db_dict[msg_id][emoji_id]
				await channel.send('{} deleted from {}'.format(emoji_id, msg_id))
			else:
				await channel.send('{} not found for {}, try again'.format(emoji_id, msg_id))

			await channel.send('Role reactions available for message {}'.format(msg_id))
			for emoji in db_dict[msg_id]:
				await channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = irie_guild.get_role(int(db_dict[msg_id][emoji])), ri = db_dict[msg_id][emoji]))

		if message.content.startswith('{}kill'.format(COMMAND_PREFIX)):
			db["system_killed"] = bool(True)
			db["system_killed_by"] = member.name
			os.system('kill 1')
			return

		if message.content.startswith('{}list_role_reaction'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			print(split_message)
			if len(split_message) != 2:
				await channel.send('Usage: {}list_role_reaction [msg_id]'.format(COMMAND_PREFIX))
				return
			
			msg_id = split_message[1]
			db_dict = db["role_reaction_message_list"]

			await channel.send('Role reactions available for message {}'.format(msg_id))
			for emoji in db_dict[msg_id]:
				await channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = irie_guild.get_role(int(db_dict[msg_id][emoji])), ri = db_dict[msg_id][emoji]))

client.run(DISCORD_TOKEN)