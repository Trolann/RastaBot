import discord
import os

DISCORD_TOKEN = os.environ['DISCORD_TOKEN'] # Stored in secrets

client = discord.Client()

@client.event
async def on_ready(): # When ready
		print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): # On every message
		if message.author == client.user: # Ignore if it's a bot message
			return

		if message.content.startswith('$hello'):
			await message.channel.send('Hello!')

client.run(DISCORD_TOKEN)
