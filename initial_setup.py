from replit import db

def run():
	print('Entering initial setup...')
	are_you_sure = input('Are you sure you want to start? Type sure')
	
	if are_you_sure != 'sure':
		return
	
	r_p = input('What should we use for the request prefix?')
	db["REQUEST_PREFIX"] = r_p
	if r_p == db["REQUEST_PREFIX"]:
		print('Request prefix set to {r_p}')
	c_p = input('What should we use for the command prefix?')
	db["REQUEST_PREFIX"] = r_p
	if c_p == db["REQUEST_PREFIX"]:
		print('Request prefix set to {c_p}')

	
	db["rules_channel_id"] = ''
	db["actions_rules_channel_id"] = ''
	db["links_channel_id"] = ''
	db["yoga_channel_id"] = ''
	print('Channel ID\'s cleared.')

	db["rules_channel_id"] = int(input('Rules channel id: '))
	db["actions_rules_channel_id"] = int(input('Actions rules channel id: '))
	db["links_channel_id"] = int(input('Links channel id: '))
	db["yoga_channel_id"] = int(input('Yoga channel id'))

	if '' in (db["rules_channel_id"], db["actions_rules_channel_id"], db["links_channel_id"], db["yoga_channel_id"]):
		print('Channel ID\'s not updated properly. Manually set them up with !db_update')


	db["system_killed"] = bool(False)
	db["system_killed_by"] = ''
	print('System killed variables reset')

	welcomed_members = db["welcomed_members"]
	welcomed_members = ['']
	db["welcomed_members"] = welcomed_members
	print('Welcomed members cleared')

	db["rules_dm"] = ''
	print('rules_dm cleared')

	db["season"] = 'general'
	print('Season reset to general')

	db["role_reaction_message_list"] = {'msg_id':''}
	print('Role reaction reset')

	db["bot_manager_id"] = int(input('Bot manager id: '))
	print('Bot manager ID now: {}'.format(db["bot_manager_id"]))

	print('Initial setup done. Remove this from the code, restart and test !help.')
	print('If help is successful, update dm\'s and messages.')

	return True