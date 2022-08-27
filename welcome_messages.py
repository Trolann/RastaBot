from rastadb import config_db, welcome_db
from datetime import datetime
from random import choice as random
from threading import Thread

global first_run
first_run = True

REQUEST_PREFIX = config_db.request_prefix

# *****************************************************#
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
# *****************************************************#


def new_message(welcome_message):
	"""Loads a new welcome message to the season list"""
	if welcome_message not in welcome_db.get_messages():
		welcome_db.new_message(welcome_message)
	return 'ADDED: {}'.format(welcome_message)

async def welcome_member(irie_guild, member):
	channel = irie_guild.system_channel
	print(random(welcome_db.get_messages()).format(member.mention, REQUEST_PREFIX))
	await channel.send(random(welcome_db.get_messages()).format(member.mention, REQUEST_PREFIX))  # Send it

print('Loaded welcome_messages.py')
