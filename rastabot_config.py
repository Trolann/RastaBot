intents = discord.Intents.default()
intents.members = True
REQUEST_PREFIX = '$'
COMMAND_PREFIX = '!'
about = 'RastaBot is created by Trolan for use on the Irie Army Discord.\nRastaBot is developed in python using the discord.py library.\nYou can find more information about RastaBot at https://github.com/Trolann/RastaBot\n'
DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets
client = discord.Client(intents = intents)

irie_vet_role = discord.Guild.get_role(role_id = 880475302420152351)

requests_avail = {
	'help':'This request sends a DM containing all possible requests from a user',
	'links':'Sends a user a DM with links to Irie Genetics beans, Grow From Your Heart podcast locations and other important links',
	'rules':'DM the user the current rules message',
	'waffle_rules/waffles_rules':'Sends a user a DM with the rules of waffles',
	'action_rules/actions_rules':'Sends a user a DM with the rules of actions',
	'about':'Shows information about RastaBot wherever the request is issued'
}

db["requests_list"] = requests_avail

commands_avail = {
	'get_season': 'Shows the current welcome message season',
	'set_season [season_name]': 'Sets the current season to a known season (prevents typos)',
	'new_season [season_name]': 'Creates a new season',
	'new_welcome_message [season_name] [welcome message formatted]': 'Creates a new welcome message in season_name with formatting. Use {} to indicate the user\'s name, mentioned. ',
	'list_welcome_messages': 'Lists welcome messages in the current season. To see other seasons, !set_season and !list_welcome_messages',
	'delete_welcome_message [index]': 'Deletes welcome message from current season at index',
	'clear_welcomed_members': 'Completely removes every member from a list of known members.',
	'new_role_message_id [id]': 'Sets which message the bot should monitor for the @Irie Army role reaction',
	'new_rules_message_id [id]': 'Sets which message the bot should copy when sending the rules',
	'new_actions_message_id [id]': 'Sets which message the bot should copy when sending the actions/waffle rules',
	'new_links_message_id [id]': 'Sets which message the bot should copy when sending links.',
	'db_update [db_key] [db_value]': 'Put a key:value pair in the db manually',
	'db_delete [db_ley]': 'Delete a key entirely from the db. Requires confirmation in the console (Trolan)',
	'add_bad_word [bad word or phrase]': 'Adds a new bad word or phrase to the list',
	'list_bad_words': 'Lists all current bad words',
	'delete_bad_word [bad word or phrase]': 'Deletes a bad word or phrase from the list'
}

db["commands_list"] = commands_avail

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

async def get_links(channel, member, key):
	print('Links request received from {}'.format(member.name))

	if key not in ('all', 'irie', 'irie genetics', 'seeds', 'beans', 'podcast', 'gfyh', 'gfyh podcast'):
		reply = "Available categories: 'all', 'irie' or 'irie genetics', 'seeds' or 'beans' and 'podcast', 'gfyh podcast' or 'gfyh'| Your given category: {}"
	else:
		reply = ''
		if key in ('irie', 'irie genetics'):
			reply += 'Irie Genetics Links:\n'
		if key in ('seeds', 'beans'):
			return
		if key in ('podcast', 'gfyh', 'gfyh podcast'):
			return
	await channel.send(reply.format(key))
