

intents = discord.Intents.default()
intents.members = True
REQUEST_PREFIX = '$'
COMMAND_PREFIX = '!'
about = 'RastaBot is created by Trolan for use on the Irie Army Discord.\nRastaBot is developed in python using the discord.py library.\nYou can find more information about RastaBot at https://github.com/Trolann/RastaBot\n'
DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets
client = discord.Client(intents = intents)

irie_vet_role = discord.Guild.get_role(role_id = 880475302420152351)

requests = {
	'help':'This request sends a DM containing all possible requests from a user',
	'links':'Sends a user a DM with links to Irie Genetics beans, Grow From Your Heart podcast locations and other important links',
	'rules':'(TODO)DM the user the current rules message',
	'waffle_rules':'(TODO)Sends a user a DM with the rules of waffles',
	'action_rules':'(TODO)Sends a user a DM with the rules of actions',
	'about':'Sends a user a DM with information about RastaBot'
}
