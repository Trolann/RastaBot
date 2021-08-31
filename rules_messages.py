from replit import db

#*****************************************************#
#  Function Group: Rules Messages                     #
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
def update_message(rules_message):
	"""Updates built in rules_message posted in system_channel after welcome_message"""
	db["rules_message"] = rules_message.content
	print('Successfully changed rules message to {}'.format(rules_message.id))
	reply = 'Successfully changed rules message to {}'
	return reply.format(rules_message.id)

def update_dm(rules_dm):
	"""Updates built in rules_dm sent to new users after welcome_message"""
	db["rules_dm"] = rules_dm
	print('length of rules_dm: {}'.format(len(rules_dm)))
	reply = 'Successfully changed rules dm to {}'
	return reply.format(rules_dm)