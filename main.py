"""
RastaBot developed by Trolan (Trevor Mathisen).
"""
import discord
import os
from replit import db
import count
import rastabot_config
import bad_words
import welcome_messages
import rules_messages

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)
irie_guild = ''
rules_channel = ''
actions_channel = ''
REQUEST_PREFIX = db["REQUEST_PREFIX"] # Prefix for users to interact with bot
COMMAND_PREFIX = db["COMMAND_PREFIX"] # Prefix for managers to command the bot
DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets

#TODO: Add: !new_rules_channel, !new_actions_rules_channel, !new_waffles_rules_channel, !new_links_channel
#TODO: Once ^ done, remove v these 
rules_channel_id = int(os.environ['RULES_CHANNEL_ID']) # Channel ID: #rules_and_etiquiette
actions_rules_channel_id = int(os.environ['ACTIONS_RULES_CHANNEL_ID']) # Channel ID: #how-to-play
links_channel_id = int(os.environ['LINKS_CHANNEL_ID']) # Channel ID: #irie-genetics-links

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
	global actions_channel
	irie_guild = client.get_guild(879408430283128843)
	rules_channel = irie_guild.get_channel(rules_channel_id)
	actions_channel = irie_guild.get_channel(actions_rules_channel_id)
	print(rastabot_config.update_all())
	print('We have logged in as {0.user}'.format(client))
	was_killed = bool(db["system_killed"])
	killed_by = str(db["system_killed_by"])

	if was_killed:
		print('*' * 25)
		print('SYSTEM RECOVERED FROM KILL COMMAND')
		print('System kill issued by {}'.format(killed_by))
		try:
			db["system_killed"] = bool(False)
			db["system_killed_by"] = ''
			print('Database successfully updated')
			print('System reset')
		except:
			print('Error updating database!')
		print('*' * 25)

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
	#TODO : Check commands length and return usage is incorrect

	if message.author == client.user: # Cancel own message
		return

	if message.content.lower().startswith('ping'): # Simple test the bot is working
		print('ping?/pong! processed from {}'.format(message.author))
		await message.channel.send('pong!')

	if str(message.channel.type) == 'private':
		await message.author.send('DM\'s are not supported yet. Please interact with the bot via a text channel')
		return
	else:
		member = message.author

	welcomed_members = db["welcomed_members"] # Pull up welcomed members
	if int(member.id) not in welcomed_members: # See if this person has been welcomed
		welcomed_members.append(int(member.id))
		db["welcomed_members"] = welcomed_members
		# If they're sending messages but haven't been welcomed, they joined the server
		# before the bot did. This will prevent us from welcoming them if they leave/join

	bot_manager_role = False
	if message.content.startswith('{}'.format(COMMAND_PREFIX)):
		for id in member.roles:
			if id == message.guild.get_role(int(db["bot_manager_id"])):
				bot_manager_role = True

	# You can't filter bad_words from commands and be able to add/remove bad_words with commands
	if not message.content.startswith('{}delete_bad_word'.format(COMMAND_PREFIX)) and not bot_manager_role: 
		# Process bad words if it's not a command from a BotManager or not a DM
		bad_words_in_message = bad_words.check_message(message)
		if bad_words_in_message != '':
			await message.channel.send('Hey {}, watch your mouth. We don\'t mention {} around here.'.format(message.author.mention, bad_words_in_message))
			return

	if message.content.startswith(REQUEST_PREFIX): # Route Requests

		if message.content.startswith('{}help'.format(REQUEST_PREFIX)):
			reply = rastabot_config.help_request(message.author)
			await message.channel.send(reply)

		if message.content.startswith('{}about'.format(REQUEST_PREFIX)):
			print('{}about request recieved from {}'.format(REQUEST_PREFIX, message.author))
			about_msg = rastabot_config.get_about()
			for line in about_msg:
				await message.channel.send(line)
			await message.channel.send('RastaBot has processed {} users, {} messages and {} reactions.'.format(db["members"], db["messages"], db["reactions"]))
		
		if message.content.startswith('{}rules'.format(REQUEST_PREFIX)):
			print('{}rules request received from {}'.format(REQUEST_PREFIX, message.author))
			rules_msg_id = db["rules_message_id"]
			member = message.author
			#rules_channel = member.guild.get_channel(rules_channel_id)
			rules_msg = await rules_channel.fetch_message(rules_msg_id)
			await member.send(rules_msg.content)
			await message.channel.send('{}, you can find the rules in the {} channel and I\'ve sent them as a DM as well. Let the mods know if you need any help or have questions.'.format(member.mention, rules_channel.mention))

		if (message.content.startswith('{}action_rules'.format(REQUEST_PREFIX))) or (message.content.startswith('{}waffle_rules'.format(REQUEST_PREFIX))) or (message.content.startswith('{}actions_rules'.format(REQUEST_PREFIX))) or (message.content.startswith('{}waffles_rules'.format(REQUEST_PREFIX))):
			print('{}action/waffle_rules request received from {}'.format(REQUEST_PREFIX, message.author))
			actions_rules_msg_id = db["actions_rules_message_id"]
			member = message.author
			actions_rules_channel = irie_guild.get_channel(actions_rules_channel_id)
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
				reply = rastabot_config.help_commands(message.author)
				await message.channel.send(reply)

			if message.content.startswith('{}get_season'.format(COMMAND_PREFIX)):
				reply = welcome_messages.get_season()
				await message.channel.send(reply)
			
			if message.content.startswith('{}set_season'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				reply = welcome_messages.set_season(split_message[1])
				await message.channel.send(reply)

			if message.content.startswith('{}new_season'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				updated_season = split_message[1] # {}new_season [1]
				reply = welcome_messages.new_season(updated_season)
				print(welcome_messages.get_season(), '| {}'.format(reply))
				await message.channel.send(reply)

			if message.content.startswith('{}new_welcome_message'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				updated_welcome_message_season = split_message[1]
				updated_welcome_message = split_message[2:]
				updated_welcome_message = ' '.join(updated_welcome_message)
				reply = welcome_messages.new_message(updated_welcome_message_season, updated_welcome_message)
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
				split_message = message.content.split()
				if len(split_message) != 2:
					await message.channel.send('Usage: {}update_rules_message [msg_id]'.format(COMMAND_PREFIX))
					return
				msg_id = int(split_message[1])
				new_rules_message = await rules_channel.fetch_message(msg_id)
				reply = rules_messages.update_message(new_rules_message)
				await message.channel.send(reply)

			if message.content.startswith('{}update_rules_dm'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_rules_dm = split_message[2:]
				new_rules_dm = ' '.join(new_rules_dm)
				reply = rules_messages.update_dm(new_rules_dm)
				await message.channel.send(reply)

			if message.content.startswith('{}keys'.format(COMMAND_PREFIX)):
				keys = db.keys()
				print(keys)
				await message.channel.send(keys)

			if message.content.startswith('{}clear_welcomed_members'.format(COMMAND_PREFIX)):
				welcomed_members = ['']
				db["welcomed_members"] = welcomed_members
				await message.channel.send('Done')

			if message.content.startswith('{}new_action_message_id'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				new_message_id = int(split_message[1])
				db["action_reaction_message"] = int(new_message_id)
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
				reply = rastabot_config.command_db_update(db_key, db_value)
				await message.channel.send(reply)

			if message.content.startswith('{}db_delete'.format(COMMAND_PREFIX)):
				db_key = message.content[11:]
				reply = rastabot_config.command_db_delete(db_key)
				await message.channel.send(reply)

			if message.content.startswith('{}add_bad_word'.format(COMMAND_PREFIX)):
				bad_word_list = db["bad_word_list"]
				bad_word_list.append(message.clean_content[14:])
				db["bad_word_list"] = bad_word_list
				await message.channel.send('Added {} to bad_word_list'.format(bad_word_list[-1]))

			if message.content.startswith('{}list_bad_words'.format(COMMAND_PREFIX)):
				reply = bad_words.list()
				await message.channel.send(reply)

			if message.content.startswith('{}delete_bad_word'.format(COMMAND_PREFIX)):
				to_delete = message.clean_content[17:]
				bad_word_list = db["bad_word_list"]
				bad_word_list.remove(to_delete)
				db["bad_word_list"] = bad_word_list
				await message.channel.send('Deleted {} from the list'.format(to_delete))
				bad_words_reply = bad_words.list()
				await message.channel.send(bad_words_reply)

		if message.content.startswith('{}new_reaction_message'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 2:
				await message.channel.send('Usage: {}new_reaction_message [msg_id]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			db_dict = db["role_reaction_message_list"]
			db_dict.update({msg_id:''})
			db["role_reaction_message_list"] = db_dict
			await message.channel.send('Added {} to messages to monitor for'.format(msg_id))

		if message.content.startswith('{}delete_reaction_message'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 2:
				await message.channel.send('Usage: {}delete_reaction_message [msg_id]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			db_dict = db["role_reaction_message_list"]
			del db_dict[msg_id]
			db["role_reaction_message_list"] = db_dict
			await message.channel.send('Deleted {} from messages to monitor for'.format(msg_id))

		if message.content.startswith('{}new_role_reaction'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 4:
				await message.channel.send('Usage: {}new_role_reaction [msg_id] [emoji] [role_id]'.format(COMMAND_PREFIX))
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
				await message.channel.send('{} not found, try again'.format(msg_id))
				return

			if db_dict[msg_id] == '':
				db_dict[msg_id] = {emoji_id:role_id}
				await message.channel.send('Added {}:{} to {}'.format(emoji_id, role_id, msg_id))
			else:
				db_dict[msg_id].update({emoji_id:role_id})
				await message.channel.send('Added {}:{} to {}'.format(emoji_id, role_id, msg_id))
			db["role_reaction_message_list"] = db_dict

			await message.channel.send('Role reactions available for message {}'.format(msg_id))
			for emoji in db_dict[msg_id]:
				await message.channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = message.guild.get_role(int(db_dict[msg_id][emoji])), ri = db_dict[msg_id][emoji]))

		# TODO: Copy role reaction [old_msg_id] [new_msg_id]
	
		if message.content.startswith('{}delete_role_reaction'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			if len(split_message) != 3:
				await message.channel.send('Usage: {}new_role_reaction [msg_id] [emoji]'.format(COMMAND_PREFIX))
				return
			msg_id = split_message[1]
			emoji_id = split_message[2]
			db_dict = db["role_reaction_message_list"]

			if msg_id not in db_dict:
				await message.channel.send('{} not found, try again'.format(msg_id))
				return

			if emoji_id in db_dict[msg_id]:
				del db_dict[msg_id][emoji_id]
				await message.channel.send('{} deleted from {}'.format(emoji_id, msg_id))
			else:
				await message.channel.send('{} not found for {}, try again'.format(emoji_id, msg_id))

			await message.channel.send('Role reactions available for message {}'.format(msg_id))
			for emoji in db_dict[msg_id]:
				await message.channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = message.guild.get_role(int(db_dict[msg_id][emoji])), ri = db_dict[msg_id][emoji]))

		if message.content.startswith('{}kill'.format(COMMAND_PREFIX)):
			db["system_killed"] = bool(True)
			db["system_killed_by"] = message.author.name
			os.system('kill 1')
			return

		if message.content.startswith('{}list_role_reaction'.format(COMMAND_PREFIX)):
			split_message = message.content.split()
			print(split_message)
			if len(split_message) != 2:
				await message.channel.send('Usage: {}list_role_reaction [msg_id]'.format(COMMAND_PREFIX))
				return
			
			msg_id = split_message[1]
			db_dict = db["role_reaction_message_list"]

			await message.channel.send('Role reactions available for message {}'.format(msg_id))
			for emoji in db_dict[msg_id]:
				await message.channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = message.guild.get_role(int(db_dict[msg_id][emoji])), ri = db_dict[msg_id][emoji]))

client.run(DISCORD_TOKEN)