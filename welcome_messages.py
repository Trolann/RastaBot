from replit import db

#*****************************************************#
#  Function Group: Welcome messages                   #
#  Description: Functions related to setting          #
#               getting or deleting welcome messages  #
#               rules messages and dm's and the       #
#               associated season                     #
#  Contains: set_welcome_message_season(season)       #
#            new_welcome_message(season)              #
#            get_welcome_message_season()             #
#         new_welcome_message(season, welcome_message)#
#            get_welcome_message(season)              #
#            update_rules_message(rules_message)      #
#            update_rules_dm(rules_dm)                #
#*****************************************************#

def set_season(season):
	"""Sets the season for the welcome message service"""
	db["season"] = season
	print('Season updated to {}'.format(season))
	reply = 'Season updated to {}'.format(season)
	return reply

def new_season(season):
	"""Created a new season to add welcome messages to"""
	available_welcome_messages = db["welcome_message"]
	if season in available_welcome_messages:
		return '{} is already available'.format(season)
	
	available_welcome_messages[season] = ''
	db["welcome_message"] = available_welcome_messages

	return '{} added successfully'.format(season) 
	
def get_season():
	"""Returns the current season from the replit db"""
	print('get_welcome_message_season(): {}'.format(db["season"]))
	return db["season"]

def new_message(season, welcome_message):
	"""Loads a new welcome message to the season list"""
	available_welcome_messages = db["welcome_message"]
	if season not in available_welcome_messages: # See if it has been added
		print('{} must be added as a season first.'.format(season))
		return '{} must be added as a season first.'.format(season)

	if available_welcome_messages[season] is None: # If empty season, add it as first value
		available_welcome_messages[season] = [welcome_message]
		db["welcome_message"] = available_welcome_messages
		print('{} created in {}'.format(welcome_message, season)) # Show it was created
		return '{} created in {}'.format(welcome_message, season)

	available_welcome_messages[season].append(welcome_message) # Append to current season
	db["welcome_message"] = available_welcome_messages
	print('{} added to {}'.format(welcome_message, season))
	return '{} added to {}'.format(welcome_message, season)

def get_message(season):
	"""Returns a random welcome message from the current season"""
	seasonal_welcome_messages = db["welcome_message"][season]
	size = len(seasonal_welcome_messages)
	random_index = db["welcome_message_index"] # "Random" is cycling through each one
	                                           # Appears more random
	if random_index != size - 1: # If not at the end
		random_index += 1 # Move to next welcome message
		db["welcome_message_index"] = random_index
	else:
		random_index = 0
		db["welcome_message_index"] = random_index
	reply = seasonal_welcome_messages[random_index] # Send from the seasonal batch
	print(reply)
	return reply
