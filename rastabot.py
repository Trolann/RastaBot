from rastadb import config_db, dealcatcher_db
import os
from time import sleep

# DealCatcher/Irie Genetics daemons
from threading import Thread
import dealcatcher.iriedirect as iriedirect
import dealcatcher.shnirie as shnirie
import dealcatcher.dwcairie as dwcairie
import dealcatcher.ctsirie as ctsirie
import dealcatcher.hsbirie as hsbirie
import dealcatcher.efsirie as efsirie
import dealcatcher.hysirie as hysirie
import dealcatcher.mggirie as mggirie
import dealcatcher.ssbirie as ssbirie
import dealcatcher.lbsirie as lbsirie
import dealcatcher.dssirie as dssirie
from dealcatcher.utils import get_site as get_site

REQUEST_PREFIX = config_db.request_prefix  # Prefix for users to interact with bot
COMMAND_PREFIX = config_db.command_prefix  # Prefix for managers to command the bot


def heartbeat_daemon(delay, loop):
    # TODO: Add environment variable to RastaBot (Replit)
    get_site(config_db.heartbeat_url)
    while loop:
        get_site(config_db.heartbeat_url)
        sleep(delay)


# *****************************************************#
#  Function Group: Database Update Functions          #
#  Description: Functions to manually add keys and    #
#               values to the database. Used for      #
#               intiial setup on a new sever          #
#       Contains: command_db_update(key, value)       #
#                 command_db_delete(key)              #
# *****************************************************#


async def get_about(member, channel):
    """Return about information"""
    print('{}about request received from {}'.format(REQUEST_PREFIX, member))
    about_msg = [config_db.about,
                 'RastaBot has processed {} users, {} messages, {} reactions and helped {} + {} people find beans.'.format(
                     config_db.get_count('members'), config_db.get_count('messages'), config_db.get_count('reactions'),
                     config_db.get_count('iriedirect'), config_db.get_count('seeds')),
                 'Use {}help to see all commands available for RastaBot'.format(REQUEST_PREFIX)]

    for i in range(len(about_msg)):
        if about_msg[i] is not None:
            await channel.send(about_msg[i])
    return

def start_seed_daemons():

    iriedirect_daemon = Thread(target=iriedirect.iriedirect_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    shn_daemon = Thread(target=shnirie.shn_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    dwca_daemon = Thread(target=dwcairie.dwca_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    cts_daemon = Thread(target=ctsirie.cts_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    hsb_daemon = Thread(target=hsbirie.hsb_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    efs_daemon = Thread(target=efsirie.efs_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    hys_daemon = Thread(target=hysirie.hys_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    mgg_daemon = Thread(target=mggirie.mgg_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    ssb_daemon = Thread(target=ssbirie.ssb_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    lbs_daemon = Thread(target=lbsirie.lbs_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    dss_daemon = Thread(target=dssirie.dss_daemon, args=(dealcatcher_db.dc_daemon_delay_minutes,), daemon=True)
    iriedirect_daemon.start()
    shn_daemon.start()
    dwca_daemon.start()
    cts_daemon.start()
    hsb_daemon.start()
    efs_daemon.start()
    hys_daemon.start()
    mgg_daemon.start()
    ssb_daemon.start()
    lbs_daemon.start()
    dss_daemon.start()


def start_daemons():
    heartbeat = Thread(target=heartbeat_daemon, args=(10, True,), daemon=True)
    heartbeat.start()
    start_seed_daemons()


def check_bot_manager(member, bot_manager_role):
    bot_manager = False
    for role in member.roles:
        if role == bot_manager_role:
            bot_manager = True
    return bot_manager


async def process_incoming_message(irie_guild, message):
    # Pull member for private messages, send things back to the member privately
    if str(message.channel.type) == 'private':
        member = irie_guild.get_member(message.author.id)
        channel = member

        # Alert everyone someone has DM'd the bot
        bot_channel = irie_guild.get_channel(config_db.bot_channel_id)
        await bot_channel.send('DM from: {}'.format(member))
        await bot_channel.send('Message: {}'.format(message.content))
        return member, channel

    # Catchall for User type bots (RastaBot) defaults to Bot ID
    if 'bot' in str(message.author).lower():
        member = irie_guild.get_member_named('RastaBot')
        channel = message.channel
        return member, channel

    # Base case, assign from the given message
    member = message.author
    channel = message.channel
    return member, channel
