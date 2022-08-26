from rastadb import config_db


def add_tester(tester_id):
	tester_members = config_db.get_tester_members()
	if tester_id not in tester_members:
		config_db.add_tester(tester_id)
	return


def check_if_notified(tester_id):
	tester_members = config_db.get_tester_members()
	return tester_id if tester_id not in tester_members else None


async def clear_testers(channel = None):
	config_db.clear_tester()
	await channel.send('Tester list cleared')


async def process_incoming_message(irie_guild, message):
	
	if message.channel.id == config_db.tester_channel_id:
		lower_message = message.clean_content.lower()
		articles = 0
		tester_id = int(message.author.id)
		if check_if_notified(tester_id):
			tester_obj = irie_guild.get_member(tester_id)
			for article in ('i', "i'", "i’", "ready", 'be', 'to', 'do', 'can', 'how', '?'):
				if lower_message.find(article) != -1:
					articles += 1
				
			if articles > 2 and lower_message.find('test') != -1:
				await message.channel.send(config_db.get_tester_message().format(tester_obj.mention))
				add_tester(tester_id)	


async def tester_request(irie_guild, message, channel):
	try:
		tester_id = int(message.content[10:-1])
	except:
		tester_id = None
	if tester_id is None:
		await channel.send(config_db.get_tester_message().format(message.author.mention))
	else:
		tester_obj = irie_guild.get_member(tester_id)
		await channel.send(config_db.get_tester_message().format(tester_obj.mention))
		add_tester(tester_id)


print('Loaded tester.py')
