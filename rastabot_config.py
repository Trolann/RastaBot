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
	db[key] = value
	return ('Added {}:{}'.format(key, value))

def command_db_delete(key):
	"""Manual DB key:value delete processing. Console confirmation """
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
	"""Retrieve all requests and send formatted message to channel"""
	print('Help request from {}'.format(member.name))
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
	print('Commands help request from {}'.format(member.name))
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
	print('TODO: get_about()')
	about_msg = db["about"]
	return about_msg

def update_requests_available():
	requests_avail = {
		'help':'This request sends a DM containing all possible requests from a user',
		'links':'Sends a user a DM with links to Irie Genetics beans, Grow From Your Heart podcast locations and other important links',
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
		'clear_welcomed_members': 'Completely removes every member from a list of known members.',
		'new_rules_message_id [id]': 'Sets which message the bot should copy when sending the rules',
		'new_actions_message_id [id]': 'Sets which message the bot should copy when sending the actions/waffle rules',
		'new_links_message_id [id]': 'Sets which message the bot should copy when sending links.',
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

# async def get_links(channel, member, key): 
# 	print('Links request received from {}'.format(member.name))

# 	if key not in ('all', 'irie', 'irie genetics', 'seeds', 'beans', 'podcast', 'gfyh', 'gfyh podcast'):
# 		reply = "Available categories: 'all', 'irie' or 'irie genetics', 'seeds' or 'beans' and 'podcast', 'gfyh podcast' or 'gfyh'| Your given category: {}"
# 	else:
# 		reply = ''
# 		if key in ('irie', 'irie genetics'):
# 			reply += 'Irie Genetics Links:\n'
# 		if key in ('seeds', 'beans'):
# 			return
# 		if key in ('podcast', 'gfyh', 'gfyh podcast'):
# 			return
# 	await channel.send(reply.format(key))
