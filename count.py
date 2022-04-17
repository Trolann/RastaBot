from replit import db

def message():
	"""Counts total messages processed. Called on every on_message()"""
	messages = int(db["messages"]) # Always get previous value from DB
	messages += 1
	db["messages"] = messages # Store new value
	if messages % 10 == 0:
		print('Messages processed: {}'.format(messages)) # Console log

def members():
	"""Counts total members processed. Called on every on_member_joined()"""
	members = int(db["members"]) # Always get previous value from DB
	members += 1
	db["members"] = members # Store new value
	print('Members processed: {}'.format(members)) # Console log

def reactions():
	"""Counts total reactions processed. Called on every on_raw_reaction_*()"""
	reactions = int(db["reactions"]) # Always get previous value from DB
	reactions += 1
	db["reactions"] = reactions # Store new value
	if reactions % 10 == 0:
		print('reactions processed: {}'.format(reactions)) # Console log

print('Loaded count.py')
