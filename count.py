from rastadb import config_db


def message():
	"""Counts total messages processed. Called on every on_message()"""
	messages = int(config_db.get_count('messages'))  # Always get previous value from DB
	messages += 1
	config_db.update_count('messages', messages)  # Store new value
	if messages % 10 == 0:
		print('Messages processed: {}'.format(messages))  # Console log


def members():
	"""Counts total members processed. Called on every on_member_joined()"""
	members_count = int(config_db.get_count('members_count'))  # Always get previous value from DB
	members_count += 1
	config_db.update_count('members', members_count)
	print('Members processed: {}'.format(members))  # Console log


def reactions():
	"""Counts total reactions processed. Called on every on_raw_reaction_*()"""
	reactions = int(config_db.get_count('reactions')) # Always get previous value from DB
	reactions += 1
	config_db.update_count('reactions', reactions)
	if reactions % 10 == 0:
		print('reactions processed: {}'.format(reactions)) # Console log


def iriedirect():
	"""Counts total reactions processed. Called on every on_raw_reaction_*()"""
	iriedirect = int(config_db.get_count('iriedirect')) # Always get previous value from DB
	iriedirect += 1
	config_db.update_count('iriedirect', iriedirect)
	if iriedirect% 10 == 0:
		print('iriedirect requests processed: {}'.format(iriedirect)) # Console log


def seeds():
	"""Counts total reactions processed. Called on every on_raw_reaction_*()"""
	seeds = int(config_db.get_count('seeds')) # Always get previous value from DB
	seeds += 1
	config_db.update_count('seeds', seeds)
	if seeds % 10 == 0:
		print('seeds requests processed: {}'.format(seeds)) # Console log

print('Loaded count.py')