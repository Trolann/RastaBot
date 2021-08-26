from replit import db

def message():
	"""Counts total messages processed. Called on every on_message()"""
	messages = db["messages"] # Always get previous value from DB
	messages += 1
	db["messages"] = messages # Store new value
	print('Messages processed: {}'.format(messages)) # Console log

def members():
	"""Counts total members processed. Called on every on_member_joined()"""
	members = db["members"] # Always get previous value from DB
	members += 1
	db["members"] = members # Store new value
	print('Members processed: {}'.format(members)) # Console log

def reactions():
	"""Counts total reactions processed. Called on every on_raw_reaction_*()"""
	reactions = db["reactions"] # Always get previous value from DB
	reactions += 1
	db["reactions"] = reactions # Store new value
	print('reactions processed: {}'.format(reactions)) # Console log