from replit import db

REQUEST_PREFIX = db["REQUEST_PREFIX"]
COMMAND_PREFIX = db["COMMAND_PREFIX"]

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
	print('command_db_update(key, value) called')
	db[key] = value
	return ('Added {}:{}'.format(key, value))

def command_db_delete(key):
	"""Manual DB key:value delete processing. Console confirmation """
	print('command_db_delete(key) called')
	response = input('Are you sure you want to delete {}?'.format(key)).lower()
	# This response/input is required in the console, an extra layer of security
	if response in ('yes', 'y'):
		del db[key]
		print('Delete {}'.format(key))
		return 'Deleted {}'.format(key)
	else:
		print('Negative response received. Did not delete {}'.format(key))
		return 'Negative response received. Did not delete {}'.format(key)

def help_request(member):
	print('help_request(member) called')
	"""Retrieve all requests and send formatted message to channel"""
	print('Help request from {}'.format(member.mention))
	msg_contents = ''
	msg_contents += 'Hi {}, I\'m RastaBot. How can I help?\n'.format(member.mention)
	requests_list = db["requests_list"] # Get loaded requests from db
	
	for req in requests_list: # read every key
		# TODO: enumerate()
		desc = requests_list[req] # read every value
		msg_contents += '{rp}{r}: {d}\n'.format(rp = REQUEST_PREFIX, r = req, d = desc)
	return msg_contents

def help_commands(member):
	"""Retrieve all commands and send formatted message to channel"""
	print('help_commands(member) called')
	msg_contents = ''
	msg_contents = 'RastaBot commands available for {}'.format(member.mention)
	commands_list = db["commands_list"]
	for cmd in commands_list: # read every key
		# TODO: enumerate()
		desc = commands_list[cmd] # read every value
		msg_contents += '{cp}{c}: {d}\n'.format(cp = COMMAND_PREFIX, c = cmd, d = desc)
	return msg_contents

def get_about():
	"""Return about information (TODO)"""
	print('get_about() called')
	about_msg = []
	about_msg.append(db["about"])
	about_msg.append('RastaBot has processed {} users, {} messages and {} reactions.'.format(db["members"], db["messages"], db["reactions"]))
	return about_msg

def update_requests_available():
	requests_avail = {
		'help':'This request sends a DM containing all possible requests from a user',
		'links':'Sends a user a DM with links to Irie Genetics beans, Grow From Your Heart podcast locations and other important links',
		'yoga':'DM the user information and rules about Stoner Yoga',
		'rules':'DM the user the current rules message',
		'waffle_rules/waffles_rules':'Sends a user a DM with the rules of waffles',
		'action_rules/actions_rules':'Sends a user a DM with the rules of actions',
		'about':'Shows information about RastaBot wherever the request is issued'
	}

	db["requests_list"] = requests_avail
	return requests_avail

def update_commands_available():
	commands_avail = {
		'kill': 'Kills bot\'s container using os.system(\'kill 1\') and prints a statement upon restart. Use when bot is not responding',
		'get_season': 'Shows the current welcome message season',
		'set_season [season_name]': 'Sets the current season to a known season (prevents typos)',
		'new_season [season_name]': 'Creates a new season',
		'new_welcome_message [season_name] [welcome message formatted]': 'Creates a new welcome message in season_name with formatting. Use {} to indicate the user\'s name, mentioned. ',
		'list_welcome_messages': 'Lists welcome messages in the current season. To see other seasons, !set_season and !list_welcome_messages',
		'delete_welcome_message [index]': 'Deletes welcome message from current season at index',
		'new_rules_message_id [id]': 'Sets which message the bot should copy when sending the rules',
		'new_actions_message_id [id]': 'Sets which message the bot should copy when sending the actions/waffle rules',
		'new_links_message_id [id]': 'Sets which message the bot should copy when sending links.',
		'new_yoga_message_id [id]': 'Sets which message the bot should copy when sending yoga rules.',
		'add_bad_word [bad word or phrase]': 'Adds a new bad word or phrase to the list',
		'list_bad_words': 'Lists all current bad words',
		'delete_bad_word [bad word or phrase]': 'Deletes a bad word or phrase from the list',
		'new_reaction_message [msg_id]': 'Tells the bot to start watching this message for reactions',
		'delete_reaction_message [msg_id]': 'Tells the bot to no longer watch this message AND DELETES ALL ASSOCIATED EMOJIS AND ROLES',
		'new_role_reaction [msg_id] [emoji] [role_id]': 'Tells the bot to assign/remove role_id when the emoji reaction is a added/removed from msg_id',
		'delete_role_reaction [msg_id] [emoji]': 'Deletes the emoji:role_id pairing from the msg_id - the bot no longer assigns that role for that emoji',
		'list_role_reaction [msg_id]': 'Lists all available reactions for the given msg_id'
	}

	db["commands_list"] = commands_avail
	return commands_avail

def update_links_available():
	irie_genetics_links = {
		'Irie Genetics Website':'https://www.iriegenetics.com/',
		'Irie Genetics Grow Questions':'https://www.iriegenetics.com/grow-questions/'
	}

	seed_vendors = {
		'Seeds Here Now':'https://seedsherenow.com/breeders/irie-genetics/',
		'Chi Town Seeds':'https://chitownseeds.com/vendor/irie-genetics/'
	}

	gfyh_podcast_links = {
		'YouTube':'https://www.youtube.com/c/TheGrowFromYourHeartPodcast',
		'iTunes Store':'https://podcasts.apple.com/us/podcast/grow-from-your-heart-podcast-hosted-by-rasta-jeff-irie/id850999151?mt=2',
		'Stitcher':'https://www.stitcher.com/show/the-grow-from-your-heart-podcast-hosted-by-rasta-jeff-of-irie/'
	}


	links_avail = {
		'Irie Genetics': irie_genetics_links,
		'Seed Vendors': seed_vendors,
		'Grow From Your Heart Podcast': gfyh_podcast_links
	}

	return links_avail

def update_all():
	update_requests_available()
	update_commands_available()
	update_links_available()
	return 'Loaded rastabot_config.py'

def process_message(trigger, member, content, clean_content):
	print('(DEBUG) process_message(trigger, member, content, clean_content) called')
	# This isn't needed after debug because every command below will print the response.
	reply = None
	rigger = trigger[1:]
	if rigger == 'help':
		if trigger[0] == REQUEST_PREFIX:
			print('Received {}help request from {}'.format(REQUEST_PREFIX, member))
			reply = help_request(member)
		else:
			print('Received {}help request from {}'.format(COMMAND_PREFIX, member))
			reply = help_commands(member)
		return reply

	if rigger == 'about':
		print('Received {}about request from {}'.format(REQUEST_PREFIX, member))
		reply = get_about()
		
		return reply
	
	if rigger == 'rules':
		print('Received {}rules request from {}'.format(REQUEST_PREFIX, member))
		#clean_content is rules_

		return reply
	if rigger == 'action_rules/actions_rules':
		print('Received {}action_rules/actions_rules request from {}'.format(REQUEST_PREFIX, member))

		return reply
	if rigger == 'links':
		print('Received {}links request from {}'.format(REQUEST_PREFIX, member))

		return reply
	if rigger == 'get_season':
		print('Received {}get_season command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'set_season':
		print('Received {}set_season command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'new_season':
		print('Received {}new_season command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'new_welcome_message':
		print('Received {}new_welcome_message command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'list_welcome_messages':
		print('Received {}list_welcome_messages command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'delete_welcome_messages':
		print('Received {}delete_welcome_messages command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'update_rules_message':
		print('Received {}update_rules_message command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'update_rules_dm':
		print('Received {}update_rules_dm command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'clear_welcomed_members':
		print('Received {}clear_welcomed_members command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'new_action_message_id':
		print('Received {}new_action_message_id command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'new_rules_message_id':
		print('Received {}new_rules_message_id command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'new_actions_rules_message_id':
		print('Received {}new_actions_rules_message_id command from {}'.format(COMMAND_PREFIX, member))

		return reply

	if rigger == 'new_links_message_id':
		print('Received {}new_links_message_id command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'db_update':
		print('Received {}db_update command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'db_delete':
		print('Received {}db_delete command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'add_bad_word':
		print('Received {}add_bad_word command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'list_bad_words':
		print('Received {}list_bad_words command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'delete_bad_word':
		print('Received {}delete_bad_word command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'new_reaction_message':
		print('Received {}new_reaction_message command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'delete_reaction_message':
		print('Received {}delete_reaction_message command from {}'.format(COMMAND_PREFIX, member))

		return reply
	if rigger == 'list_role_reaction':
		print('Received {}list_role_reaction command from {}'.format(COMMAND_PREFIX, member))

		return reply
	return

# async def get_links(channel, member, key): 
# 	print('Links request received from {}'.format(member.name))

# 	if key not in ('all', 'irie', 'irie genetics', 'seeds', 'beans', 'podcast', 'gfyh', 'gfyh podcast'):
# 		reply = "Available categories: 'all', 'irie' or 'irie genetics', 'seeds' or 'beans' and 'podcast', 'gfyh podcast' or 'gfyh'| Your given category: {}"
# 	else:
# 		
# 		if key in ('irie', 'irie genetics'):
# 			reply += 'Irie Genetics Links:\n'
# 		if key in ('seeds', 'beans'):
# 			return
# 		if key in ('podcast', 'gfyh', 'gfyh podcast'):
# 			return
# 	await channel.send(reply.format(key))
