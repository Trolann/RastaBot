"""
RastaBot developed by Trolan (Trevor Mathisen). 
"""
import discord
import os
from replit import db
import asyncio
import count
import rastabot
import bad_words
import welcome_messages
import rules_messages
import podcast
import tester

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

# Guilds and channels will need global variables.
# TODO1: Update to dict[guild_name][channel][channel_id]
# Also I don't think I need to declare these here
irie_guild = ''
rules_channel = ''
actions_rules_channel = ''
links_channel = ''
bot_channel = ''
tester_channel = ''
voice_channel = ''
gfyh_podcast_channel = ''
irie_podcast_channel = ''
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
	# Pull in global variables (guild and channels)
	# TODO1: Update to dict[guild_name][channel][channel_id]
	global pc_vc
	global vc
	global irie_guild
	global rules_channel
	global actions_rules_channel
	global links_channel
	global bot_channel
	global tester_channel
	global voice_channel
	global irie_podcast_channel
	global gfyh_podcast_channel

	# Load then print each object
	# TODO2: Update channel IDs to TODO1's dict[guild_name][channel][channel_id]
	# TODO3: Define function to call, enumerate thru TODO1's dict and load objects     
	irie_guild = client.get_guild(IRIE_GUILD_ID)
	print(irie_guild)
	rules_channel = irie_guild.get_channel(int(db["rules_channel_id"]))
	print(rules_channel)
	actions_rules_channel = irie_guild.get_channel(int(db["actions_rules_channel_id"]))
	print(actions_rules_channel)
	links_channel = irie_guild.get_channel(int(db["links_channel_id"]))
	print(links_channel)
	bot_channel = irie_guild.get_channel(int(db["bot_channel"]))
	print(bot_channel)
	tester_channel = irie_guild.get_channel(int(db["tester_channel_id"]))
	print(tester_channel)
	voice_channel = irie_guild.get_channel(int(db["voice_channel_id"]))
	print(voice_channel)
	irie_podcast_channel = irie_guild.get_channel(int(db["irie_podcast_channel_id"]))
	print(irie_podcast_channel)
	gfyh_podcast_channel = irie_guild.get_channel(int(db["gfyh_podcast_channel_id"]))
	print(gfyh_podcast_channel)
	print(rastabot.update_all())
	print('We have logged in as {0.user}'.format(client))

	# Check if the bot is waking up from a kill, and if so print information
	# TODO4: Update to rastabot.py function. Function should alert bot_channel
	#        and write a file to the local directory
	was_killed = bool(db["system_killed"])
	killed_by = str(db["system_killed_by"])

	# Print to the console
	if was_killed:
		print('*' * 35)
		print('SYSTEM RECOVERED FROM KILL COMMAND')
		print('System kill issued by {}'.format(killed_by))
		# Cleanup - can fail if backend failure caused the initial !kill
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
		channel = irie_guild.system_channel
		season = db["season"]
		reply = welcome_messages.get_message(season) # Get a semi-random welcome message
		welcomed_members.append(int(member.id)) # Note you've welcomed this person
		db["welcomed_members"] = welcomed_members
		print(reply.format(member.mention, REQUEST_PREFIX))
		await channel.send(reply.format(member.mention, REQUEST_PREFIX)) # Send it


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
	# TODO5: Replace count.py with method in rastabot.py. rastabot.count(payload)
	#        function will determine based on payload what to count
	count.reactions() # Basic counter

	# TODO6: Replace with a reactions.py method which takes in the payload and returns
	#        a tuple of member, role and action (add/remove) if valid or None if invalid

	reaction_dict = db["role_reaction_message_list"] # Load available reaction messages
	message_id = str(payload.message_id) # Strip message id

	# Custom emoji's get processed as a text string. Basic emoji's are supported as-is.
	if payload.emoji.is_custom_emoji():
		emoji_id = str(payload.emoji.name)
	else:
		emoji_id = payload.emoji.name

	# If the reaction was to a watched message
	if message_id in reaction_dict:	
		for key in reaction_dict[message_id]:
			# And if the emoji is in the dictionary
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
	# TODO5: Replace count.py with method in rastabot.py. rastabot.count(payload)
	#        function will determine based on payload what to count
	count.reactions() # Basic counter

	# TODO6: Replace with a reactions.py method which takes in the payload and returns
	#        a tuple of member, role and action (add/remove) if valid or None if invalid
	# Member object not passed, so load it based on the message id
	reaction_dict = db["role_reaction_message_list"]
	# Reaction removal doesn't provide the member object, so we pull in user_id.
	user_id = int(payload.user_id)
	message_id = str(payload.message_id)
	member = irie_guild.get_member(user_id)

	# Custom emoji's get processed as a text string. Basic emoji's are supported as-is.
	if payload.emoji.is_custom_emoji():
		emoji_id = str(payload.emoji.name)
	else:
		emoji_id = payload.emoji.name

	# If the reaction was to a watched message
	if message_id in reaction_dict:
		for key in reaction_dict[message_id]:
			# And if the emoji is in the dictionary
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
	# TODO5: Replace count.py with method in rastabot.py. rastabot.count(payload)
	#        function will determine based on payload what to count
	count.message() # Basic counter

	####################################################################################
	####################################################################################
	#CONTINUE ADDING COMMENTS BELOW

	if message.author == client.user: # Cancel own message
		return

	if message.content.lower().startswith('rbping'): # Simple test the bot is working
		print('rbping?/pong! processed from {}, {}'.format(message.author, client.latency))
		await message.channel.send('pong!')

	if db["auto status"] == 1:
		name, url = podcast.check_new()
		if name is not None:
			await bot_channel.send('Found a new podcast. Updating')
			db["podcast status"] = 1
			db["gfyh number"] = name[1:4]
			db["gfyh url"] = url
			await gfyh_podcast_channel.send("Episode {} of the Grow From Your Heart ({}) podcast has been posted! \n {}".format(name[1:4], name[5:], url))
			await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name='GFYH Podcast #{}'.format(name[1:4]), url=url))
			print('New podcast found: {} at {}'.format(name[1:4], url))

	if db["podcast status"] == 1:
		db["podcast status"] = 1
		number = db["gfyh number"]
		new_url = db["gfyh url"]
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name='GFYH Podcast #{}'.format(number), url=new_url))

	if str(message.channel.type) == 'private':
		member = irie_guild.get_member(message.author.id)
		channel = member
		print('DM from: {}'.format(member))
		print('Message: {}'.format(message.clean_content))
	else:
		member = message.author
		channel = message.channel

	if message.channel.id == tester_channel.id:
		lower_message = message.clean_content.lower()
		articles = 0
		tester_id = int(message.author.id)
		# print(tester.check_if_notified(tester_id))
		if tester.check_if_notified(tester_id) is None:
			tester_obj = irie_guild.get_member(tester_id)
			for article in ('i', "i'", "i’", "ready", 'be', 'to', 'do', 'can', 'how'):
				if lower_message.find(article) != -1:
					articles += 1
				
			if articles > 2 and lower_message.find('test') != -1:
				await channel.send(db["tester_message"].format(tester_obj.mention))
				tester.add_tester(tester_id)
				
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
	
	if message.content.startswith('{}'.format(COMMAND_PREFIX)) and str(message.author) == 'Trolan#7880':
		bot_manager = True

	# TODO: bad_words.check_message(message) return reply
	# You can't filter bad_words from commands and be able to add/remove bad_words with commands
	if not message.content.startswith('{}'.format(COMMAND_PREFIX)) and not bot_manager: 
		# Process bad words if it's not a command from a BotManager or not a DM
		bad_words_in_message = bad_words.check_message(message)
		blacklist_in_message = bad_words.blacklist_check_message(message)
		if bad_words_in_message != '':
			await channel.send('Hey {}, watch your mouth. We don\'t mention that around here.'.format(member.mention, bad_words_in_message))
			return

		if blacklist_in_message != '':
			await bot_channel.send('{} said a blacklisted word(s) in {}: {}'.format(message.author, message.channel.mention, blacklist_in_message))
			print('BLACKLIST WORD DETECTED')

	try:
		if message.clean_content[0] not in (REQUEST_PREFIX, COMMAND_PREFIX):
			return
	except:
		return

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
			
			
		if message.content.startswith('{}links'.format(REQUEST_PREFIX)):
			print('{}links request received from {}'.format(REQUEST_PREFIX, member))
			links_msg_id = db["links_message_id"]
			links_msg = await links_channel.fetch_message(links_msg_id)
			await member.send(links_msg.content)
			await channel.send('{}, I sent you a copy of the links from {}. Let us know if something should be added!'.format(member.mention, links_channel.mention))

		if message.content.startswith('{}tester'.format(REQUEST_PREFIX)):
			try:
				tester_id = int(message.content[11:29])
			except:
				tester_id = None
			if tester_id is None:
				await channel.send(db["tester_message"].format(message.author.mention))
			else:
				tester_obj = irie_guild.get_member(tester_id)
				await channel.send(db["tester_message"].format(tester_obj.mention))
				tester.add_tester(tester_id)

		if message.content.startswith('{}dab'.format(REQUEST_PREFIX)):

			if ((message.channel.id == int(db["podcast_text_chanel_id"])) or (message.channel.id == int(db["hempire_text_channel_id"]))):

				admin = False
				for id in member.roles:
					if id == irie_guild.get_role(int(db["irie_admin_id"])):
						admin = True
				if not admin:
					return		

				global pc_vc
				global vc
				try:
					if(vc.is_playing() or vc.is_connected()):
						vc.disconnect()
				except:
					print('No other VoiceClients active.')
				try:
					pc_vc = await irie_podcast_channel.connect()
				except:
					await pc_vc.disconnect()
				print('Connecting to {}...'.format(irie_podcast_channel.name))
				connect_time = 0.0
				while(pc_vc.average_latency == float('inf')):
					connect_time += 0.5
					await asyncio.sleep(0.5)
				print('Connected to {} after {}sec with latency of {}'.format(irie_podcast_channel.name, connect_time, pc_vc.average_latency))
				try:
					pc_vc.play(discord.FFmpegPCMAudio('dabtime.mp3'))
					print('Playing dabtime.mp3 with latency of {}'.format(pc_vc.average_latency))
					pc_vc.source = discord.PCMVolumeTransformer(pc_vc.source, volume=0.35)
					while(pc_vc.is_playing()):
						await asyncio.sleep(0.5)
						continue
					print('Done playing dabtime.mp3 with latency of {}'.format(pc_vc.average_latency))
					await pc_vc.disconnect()
					return
				except:
					await pc_vc.disconnect()
					return
			if (message.channel.id != (int(db["voice_text_channel_id"]))):
					text_channel = irie_guild.get_channel(int(db["voice_text_channel_id"]))
					await message.channel.send('{}dab only usable in {}'.format(REQUEST_PREFIX, text_channel.mention))
					return
			else:
				if rastabot.check_dab_timer():
					await message.channel.send('Can\'t right now {}, I\'m cleaning my rig'.format(message.author.mention))
					print('{}'.format(rastabot.check_dab_timer()))
					return
				else:
					in_channel = False
					for member in voice_channel.members:
						if member is message.author:
							in_channel = True
					if not in_channel:
						await message.channel.send('You have to be in {} in order to spam it with {}dab'.format(voice_channel.mention, REQUEST_PREFIX))
						return
					await message.channel.send('Not a bad idea {}...'.format(message.author.mention))

				print('{}dab issued by {}'.format(REQUEST_PREFIX, message.author))


				#global vc 
				try:
					if(pc_vc.is_playing() or pc_vc.is_connected()):
						return
				except:
					print('No other VoiceClients active.')
				try:
					vc = await voice_channel.connect()
				except:
					await vc.disconnect()
				print('Connecting to {}...'.format(voice_channel.name))
				connect_time = 0.0
				while(vc.average_latency == float('inf')):
					connect_time += 0.5
					await asyncio.sleep(0.5)
				print('Connected to {} after {}sec with latency of {}'.format(voice_channel.name, connect_time, vc.average_latency))
				try:
					vc.play(discord.FFmpegPCMAudio('dabtime.mp3'))
					print('Playing dabtime.mp3 with latency of {}'.format(vc.average_latency))
					vc.source = discord.PCMVolumeTransformer(vc.source, volume=0.35)
					while(vc.is_playing()):
						await asyncio.sleep(0.5)
						continue
					print('Done playing dabtime.mp3 with latency of {}'.format(vc.average_latency))
					await vc.disconnect()
					rastabot.start_dab_timer()
				except:
					await vc.disconnect()
					rastabot.start_dab_timer()


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

			if message.content.startswith('{}db_update'.format(COMMAND_PREFIX)):
				split_message = message.content.split()
				db_key = split_message[1]
				db_value = message.content[12 + len(db_key):]
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

			if message.content.startswith('{}add_blacklist_word'.format(COMMAND_PREFIX)):
				blacklist_list = db["blacklist_list"]
				blacklist_list.append(message.clean_content[20:])
				db["blacklist_list"] = blacklist_list
				await channel.send('Added {} to blacklist_list'.format(blacklist_list[-1]))

			if message.content.startswith('{}list_blacklist_words'.format(COMMAND_PREFIX)):
				blacklist_list = list(db["blacklist_list"])
				reply = blacklist_list
				await channel.send(reply)

			if message.content.startswith('{}delete_blacklist_word'.format(COMMAND_PREFIX)):
				to_delete = message.clean_content[23:]
				blacklist_list = list(db["blacklist_list"])
				blacklist_list.remove(to_delete)
				db["blacklist_list"] = blacklist_list
				await channel.send('Deleted {} from the blacklist list'.format(to_delete))
				await channel.send(blacklist_list)

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
			
			if message.content.startswith('{}new_status'.format(COMMAND_PREFIX)):
				if message.content[12:15].isdigit():
					number = message.content[12:15]
					new_url = message.content[16:]
					db["podcast status"] = 1
					db["gfyh number"] = number
					db["gfyh url"] = new_url
					await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name='GFYH Podcast #{}'.format(number), url=new_url))
					await channel.send('Updated status for podcast {} at {}'.format(number, new_url))
				elif message.content[12:].startswith('clear'):
					print('CLEAR COMMAND')
					await client.change_presence(status=None)
					db["auto status"] = 0
					db["podcast status"] = 0
					db["gfyh number"] = 0
					db["gfyh url"] = ''
					await channel.send('Status cleared, auto status disabled.')

			if message.content.startswith('{}auto_status'.format(COMMAND_PREFIX)):
				db["auto status"] = 1
				await channel.send('Auto status enabled - waiting for new podcasts.')

				name, url = podcast.check_new()
				if name is not None:
					await channel.send('Found a new podcast. Updating')
					db["podcast status"] = 1
					db["gfyh number"] = name[1:4]
					db["gfyh url"] = url
					await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name='GFYH Podcast #{}'.format(name[1:4]), url=url))
					print('New podcast found: {} at {}'.format(name[1:4], url))

			if message.content.startswith('{}clear_testers'.format(COMMAND_PREFIX)):
				tester.list_testers()
				tester.clear_testers()
				tester.list_testers()	
				await channel.send('Tester list cleared')

			if message.content.startswith('{}tester_message'.format(COMMAND_PREFIX)):
				tester_message = message.content[16:]
				db["tester_message"] = tester_message
				await channel.send('Tester message updated to: {}'.format(tester_message))

			if message.content.startswith('{}check_dab_timer'.format(COMMAND_PREFIX)):
				remaining = rastabot.check_dab_timer()

				if remaining:
					await message.channel.send('{} seconds remaining'.format(remaining))
				else:
					await message.channel.send('No active timer')
					
			if message.content.startswith('{}clear_dab_timer'.format(COMMAND_PREFIX)):	
				remaining = await rastabot.clear_dab_timer()

				if remaining == 0:
					await message.channel.send('Timer cleared')
				else:
					await message.channel.send('Issue clearing timer')

			if message.content.startswith('{}start_dab_timer'.format(COMMAND_PREFIX)):	
				rastabot.start_dab_timer()
				remaining = rastabot.check_dab_timer()
				await message.channel.send('Started. {} seconds remaining'.format(remaining))
					
client.run(DISCORD_TOKEN)