from rastadb import wordfilter_db, config_db


#  Function Group: Bad words                          #
#  Description: Functions which process bad words     #
#  Contains: list_bad_words(channel)                  #
#            bad_words_check(message)                 #
# *****************************************************#


def list_bad_words():
    """Return a string of formatted bad words from the db"""
    bad_words = ''
    for word in wordfilter_db.get_list('bad'):
        bad_words += '{}, '.format(word)
    reply = 'Bad words: {}'.format(bad_words[:-2])
    return reply


def check_message(message):
    """Checks message.clean_content.lower() for a bad word match"""

    bad_word_check = wordfilter_db.get_list('bad')
    clean_content = message.clean_content.lower()

    for word in bad_word_check:  # For every bad word we have
        if word in clean_content:  # See if it's in the message
            return True

    return False


def banned_check_message(message):
    blacklist_check = wordfilter_db.get_list('banned')
    clean_content = message.clean_content.lower()

    for word in blacklist_check:
        if word in clean_content:
            return True

    return False


async def check(irie_guild, channel, message, member):
    # Process bad words if it's not a command from a BotManager or not a DM
    bad_words_in_message = check_message(message)
    banned_in_message = banned_check_message(message)
    if bad_words_in_message:
        await channel.send('Hey {}, watch your mouth. We don\'t mention that around here.'.format(member.mention,
                                                                                                  bad_words_in_message))
        return

    if banned_in_message:
        bot_channel = irie_guild.get_channel(int(config_db.bot_channel_id))
        await bot_channel.send(
            '{} said a blacklisted word(s) in {}: {}'.format(message.author, message.channel.mention, message.content))
        return


print('Loaded bad_words.py')
