from replit import db

#*****************************************************#
#  Function Group: Bad words                          #
#  Description: Functions which process bad words     #
#  Contains: list_bad_words(channel)                  #
#            bad_words_check(message)                 #
#*****************************************************#

def list():
	"""Return a string of formatted bad words from the db"""
	reply = ''
	bad_words_list = db["bad_word_list"]
	bad_words_list.value.sort()
	db["bad_word_list"] = bad_words_list
	bad_words = ''

	for word in bad_words_list:
		bad_words += '{}, '.format(word)
	
	reply = 'Bad words: {}'.format(bad_words[:-2])
	return reply

def check_message(message):
	"""Checks message.clean_content.lower() for a bad word match"""
	#TODO: Alert when 1 character is different
	#TODO: Look at stripping whitespace and alerting off of that (or messaging)
	words_said = '' # Blank reply
	bad_word_check = db["bad_word_list"]
	stripped = message.clean_content.lower().replace(' ', '')
	for word in bad_word_check: # For every bad word we have
		if word in stripped: # See if its in the message
			if words_said == '': # If it's the first word found, add it
				words_said += word
			else:
				words_said += ' or {}'.format(word) # or add to list if its not
	word_count = words_said.count(' or')

	if word_count != 1:
		words_said = words_said.replace(' or', ',', word_count - 1)
	
	return words_said # Send back {}, {} or {} of bad words

print('Loaded bad_words.py')
