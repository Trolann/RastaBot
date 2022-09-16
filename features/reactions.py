from rastadb import config_db, reactions_db

COMMAND_PREFIX = config_db.command_prefix


async def add(irie_guild, payload):
	reaction_messages = reactions_db.get_reactions()
	message_id = str(payload.message_id)  # Strip message id

	# Custom emoji's get processed as a text string. Basic emoji's are supported as-is.
	if payload.emoji.is_custom_emoji():
		emoji_id = str(payload.emoji.name)
	else:
		emoji_id = payload.emoji.name

	# If the reaction was to a watched message
	if str(message_id) in reaction_messages:
		for key, role_id in reactions_db.get_reactions(message_id):
			# And if the emoji is in the dictionary
			if key == emoji_id:
				role = irie_guild.get_role(int(role_id))
				await payload.member.add_roles(role)
				print('{} reaction received. Added {} to {}'.format(emoji_id, role, payload.member))


async def remove(irie_guild, payload):
	# Member object not passed, so load it based on the message id
	reaction_messages = reactions_db.get_reactions()
	# Reaction removal doesn't provide the member object, so we pull in user_id.

	message_id = str(payload.message_id)
	member = irie_guild.get_member(payload.user_id)

	# Custom emoji's get processed as a text string. Basic emoji's are supported as-is.
	if payload.emoji.is_custom_emoji():
		emoji_id = str(payload.emoji.name)
	else:
		emoji_id = payload.emoji.name

	# If the reaction was to a watched message
	if message_id in reaction_messages:
		for key, role_id in reactions_db.get_reactions(message_id):
			# And if the emoji is in the dictionary
			if key == emoji_id:
				role = irie_guild.get_role(int(role_id))
				await member.remove_roles(role)
				print('{} removal reaction received. Removed {} from {}'.format(emoji_id, role, member))


async def new_reaction_message(message, channel):
		split_message = message.content.split()
		if len(split_message) != 2:
			await channel.send('Usage: {}new_reaction_message [msg_id]'.format(COMMAND_PREFIX))
			return
		msg_id = split_message[1]
		reactions_db.add_message(msg_id)
		await channel.send('Added {} to messages to monitor for'.format(msg_id))


async def delete_reaction_message(message, channel):
	split_message = message.content.split()
	
	if len(split_message) != 2:
		await channel.send('Usage: {}delete_reaction_message [msg_id]'.format(COMMAND_PREFIX))
		return
		
	msg_id = split_message[1]
	reactions_db.remove_message(msg_id)
	await channel.send('Deleted {} from messages to monitor for'.format(msg_id))	

# TODO: Implement custom emoji support
async def new_role_reaction(irie_guild, message, channel):
	split_message = message.content.split()
	
	if len(split_message) != 4:
		await channel.send('Usage: {}new_role_reaction [msg_id] [emoji] [role_id]'.format(COMMAND_PREFIX))
		return
		
	msg_id = split_message[1]
	emoji = split_message[2]
	role_id = split_message[3]

	if emoji.count(':'):
		emoji_id = str(emoji[2:emoji.rfind(':')])
	else:
		emoji_id = emoji

	if str(msg_id) not in reactions_db.get_reactions():
		await channel.send('{} not found, try again'.format(msg_id))
		return

	reactions_db.add_reaction(msg_id, emoji, role_id)
	await channel.send('Added {}:{} to {}'.format(emoji_id, role_id, msg_id))

	await channel.send('Role reactions available for message {}'.format(msg_id))
	for emoji, role_id in reactions_db.get_reactions(msg_id):
		if emoji != '1':
			await channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = irie_guild.get_role(int(role_id)), ri = role_id))


async def delete_role_reaction(irie_guild, message, channel):
	split_message = message.content.split()
	if len(split_message) != 3:
		await channel.send('Usage: {}new_role_reaction [msg_id] [emoji]'.format(COMMAND_PREFIX))
		return

	msg_id = split_message[1]
	emoji_id = split_message[2]

	messages = reactions_db.get_reactions()

	if str(msg_id) not in messages:
		await channel.send('{} not found, try again'.format(msg_id))
		return

	reactions_db.remove_reaction(msg_id, emoji_id)

	await channel.send('{} deleted from {}'.format(emoji_id, msg_id))

	await channel.send('Role reactions available for message {}'.format(msg_id))
	for value in reactions_db.get_reactions(msg_id):
		emoji, role_id = value
		await channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = irie_guild.get_role(int(role_id)), ri = role_id))


async def list_reactions(irie_guild, message, channel):
	split_message = message.content.split()

	if len(split_message) != 2:
		await channel.send('Usage: {}list_role_reaction [msg_id]'.format(COMMAND_PREFIX))
		return
	
	msg_id = split_message[1]

	await channel.send('Role reactions available for message {}'.format(msg_id))
	for value in reactions_db.get_reactions(msg_id):
		emoji, role_id = value
		await channel.send('Emoji {e} gives you the {r} role (Role ID: {ri})'.format(e = emoji, r = irie_guild.get_role(int(role_id)), ri = role_id))
