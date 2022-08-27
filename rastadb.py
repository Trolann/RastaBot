import os
import sqlite3
from time import sleep
from os import environ
global dev_instance
try:
    dev_instance = bool(int(environ['DEV_INSTANCE']))
    print('got from environ {}'.format(dev_instance))
except KeyError:
    print('sure didnt')
    dev_instance = True

global path
try:
    path = environ['DIR_PATH']
    print(path)
except KeyError:
    path = ''
    print('no path')

def remove(db, table, option, get_dev = False, commit_to_db=True):
    global dev_instance
    if dev_instance and get_dev:
        option = 'dev_' + option
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = "DELETE FROM {} WHERE option = '{}'".format(table, option)
    else:
        sql = "DELETE FROM {} WHERE option = '{}' AND option NOT LIKE \'dev_%\'".format(table, option)
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError:
        sleep(1)
        cursor.execute(sql)
    if commit_to_db:
        connection.commit()
    cursor.close()


def remove_like_value(db, table, option_like, value_like, get_dev = False,  commit_to_db=True):
    global dev_instance
    if dev_instance and get_dev:
        option_like = 'dev_' + option_like
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = "DELETE FROM {} WHERE option = '{}' AND value LIKE '%{}%'".format(table, option_like, value_like)
    else:
        sql = "DELETE FROM {} WHERE option = '{}' AND option NOT LIKE \'dev_%\' AND value LIKE '%{}%'".format(table, option_like, value_like)
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError:
        sleep(1)
        cursor.execute(sql)
    if commit_to_db:
        connection.commit()
    cursor.close()


def insert(db, table, option, value, get_dev = False, commit_to_db = True):
    global dev_instance
    if dev_instance and get_dev:
        option = 'dev_' + option
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    to_insert = (option, value)
    sql = 'INSERT OR REPLACE INTO {} VALUES {}'.format(table, to_insert)
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError:
        sleep(1)
        cursor.execute(sql)
    if commit_to_db:
        connection.commit()
    cursor.close()
    connection.close()


def get_value(db, table, option, get_dev = False):
    global dev_instance

    if dev_instance and get_dev:
        option = 'dev_' + option

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\''.format(table, option)
    else:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\' AND option NOT LIKE \'%dev_%\''.format(table, option)
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows[0][0] if rows else 0


def select_from_table(db, table, option, get_dev = False):
    global dev_instance

    if dev_instance and get_dev:
        option = 'dev_' + option

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\''.format(table, option)
    else:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\' AND option NOT LIKE \'dev_%\''.format(table, option)
    cursor.execute(sql)
    rows = cursor.fetchall()
    values = []
    for _value in rows:
        values.append(_value[0])
    cursor.close()
    connection.close()
    return values


class ConfigDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'config'
        self.tester_table = 'testers'
        self.request_prefix = get_value(self._rastadb, self.table, 'request_prefix')
        self.command_prefix = get_value(self._rastadb, self.table, 'command_prefix')
        self.bot_manager_id = int(get_value(self._rastadb, self.table, 'bot_manager_id', get_dev = True))
        self.heartbeat_url = self.get_heartbeat('url')
        self.heartbeat_api = self.get_heartbeat('api')

        self.system_killed_by = get_value(self._rastadb, self.table, 'system_killed_by')
        self.system_killed = False if self.system_killed_by == 'None' or '' else True

        self.bot_channel_id = int(get_value(self._rastadb, self.table, 'bot_channel_id', get_dev = True))
        self.tester_channel_id = int(get_value(self._rastadb, self.table, 'tester_channel_id', get_dev = True))

        self.about = get_value(self._rastadb, self.table, 'about', get_dev = True)

    def get_heartbeat(self, value):
        value = 'heartbeat_' + value
        return get_value(self._rastadb, self.table, value, get_dev = True)

    def update_killed(self, by = ''):
        item = 'system_killed_by'
        option = by
        insert(self._rastadb, self.table, item, option)

    def get_tester_message(self):
        return get_value(self._rastadb, self.tester_table, 'tester_message', get_dev = True)

    def get_tester_members(self):
        rows = select_from_table(self._rastadb, self.tester_table, 'member_id')
        return_list = list()
        for value in rows:
            return_list.append(int(value))
        return return_list

    def update_count(self, counter, value):
        item = counter + '_count'
        insert(self._rastadb, self.table, item, value, get_dev = True)

    def add_tester(self, tester_id):
        item = 'member_id'
        insert(self._rastadb, self.tester_table, item, tester_id, get_dev = True)

    def clear_tester(self):
        option = 'dev_member_id' if dev_instance else 'member_id'
        conn = sqlite3.connect(self._rastadb)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM {} WHERE option = '{}'".format(self.tester_table, option))
        conn.commit()
        cursor.close()
        conn.close()
        self.add_tester('1234')
        self.add_tester('4556')

    def update_tester_message(self, tester_message):
        item = 'tester_message'
        remove(self._rastadb, self.tester_table, item, get_dev = True)
        insert(self._rastadb, self.tester_table, item, tester_message, get_dev = True)

    def get_count(self, counter):
        item = counter + '_count'
        return int(get_value(self._rastadb, self.table, item, get_dev = True))


class WelcomeDB:
    def __init__(self):
        global path
        self._rastadb = path + 'welcomed_members.db'
        self.table = 'welcome_messages'
        self.members_table = 'welcomed_members'

    def get_messages(self):
        return select_from_table(self._rastadb, self.table, 'welcome_message', get_dev = True)

    def welcomed_list(self, member_id):
        return select_from_table(self._rastadb, self.table, member_id, get_dev = True)
        
    def new_message(self, new_message):
        item = 'welcome_message'
        insert(self._rastadb, self.table, item, new_message, get_dev = True)

    def add_member(self, member):
        item, option = ('member_id', member)
        insert(self._rastadb, self.members_table, item, option, get_dev = True)

    def clear_welcomed_members(self):
        option = 'dev_member_id' if dev_instance else 'member_id'
        conn = sqlite3.connect(self._rastadb)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM {} WHERE option = '{}'".format(self.members_table, option))
        insert(self.members_table, option, 1234)
        insert(self.members_table, option, 5678)
        conn.commit()
        cursor.close()
        conn.close()


class PodcastDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'podcast'
        self.podcast_channel_id = int(get_value(self._rastadb, self.table, 'irie_podcast_channel_id', get_dev = True))

    def get_auto_status(self):
        return bool(get_value(self._rastadb, self.table, 'auto_status'))

    def get_current(self, value):
        item = 'current_' + value
        row = get_value(self._rastadb, self.table, item, get_dev = True)
        return row if 'num' not in value else int(row)

    def new_podcast(self, num, title, url):
        n = ('current_number', num)
        t = ('current_title', title)
        u = ('current_url', url)
        for item, option in (n, t, u):
            insert(self._rastadb, self.table, item, option, get_dev = True)


class WordFilterDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'word_filter'

    def get_list(self, which_list):
        item = which_list + '_word'
        return select_from_table(self._rastadb, self.table, item)

    def add(self, which_list, bad_word):
        insert(self._rastadb, self.table, which_list + '_word', bad_word)

    def remove(self, which_list, bad_word):
        remove(self._rastadb, self.table, which_list + '_word', bad_word)


class ReactionsDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'reactions'
        self.separator = '||'

    def get_reactions(self, msg_id = None):
        if msg_id is None:
            return list(select_from_table(self._rastadb, self.table, 'reaction_message'))
        rows = select_from_table(self._rastadb, self.table, msg_id)

        if len(rows[0]) > 1:
            reaction_tups = list()
            reaction_messages = list(rows)
            for option in reaction_messages:
                option_split = option.split(self.separator)
                tup = (option_split[0], option_split[1])
                reaction_tups.append(tup)
        else:
            emoji, role_id = rows.split(self.separator)
            reaction_tups = (emoji, role_id)

        return reaction_tups

    # TODO: Implement custom emoji support
    def add_message(self, message_id):
        item = 'reaction_message'
        insert(self._rastadb, self.table, item, message_id)

    def remove_message(self, message_id):
        remove(self._rastadb, self.table, message_id)
        remove_like_value(self._rastadb, self.table, 'reaction_message', message_id)

    def add_reaction(self, message_id, emoji, role_id):
        item = message_id
        option = emoji + self.separator + role_id
        insert(self._rastadb, self.table, item, option)
        option = '1||1'  # Dummy record to ensure list parses correctly. Unique values will be overriden and not stack
        insert(self._rastadb, self.table, item, option)

    def remove_reaction(self, message_id, emoji):
        remove_like_value(self._rastadb, self.table, message_id, emoji)


class SoundsDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'sounds'
        self.dab_cooldown_length = int(get_value(self._rastadb, self.table, 'dab_cooldown_length'))
        self.dab_text_channel_id = int(get_value(self._rastadb, self.table, 'dab_text_channel_id', get_dev = True))
        self.dab_voice_channel_id = int(get_value(self._rastadb, self.table, 'dab_voice_channel_id', get_dev = True))
        self.dab_delay_seconds = int(get_value(self._rastadb, self.table, 'dab_delay_seconds', get_dev = True))

    def check_dab_timer(self):
        return int(round(float(get_value(self._rastadb, self.table, 'dab_timer_expires', get_dev = True))))

    def start_dab_timer(self, time):
        insert(self._rastadb, self.table, 'dab_timer_expires', time, get_dev = True)

    def clear_dab_timer(self):
        insert(self._rastadb, self.table, 'dab_timer_expires', 0, get_dev = True)


class DealCatcherDB:
    def __init__(self):
        global path
        self._rastadb = path + 'dealcatcher.db'
        self.table = 'deals'
        self.expired_table = 'deals_expired'
        self.new_table = 'deals_new'
        self.separator = '||'
        self.dir_path = path
        self.dc_daemon_delay_minutes = int(get_value(self._rastadb, self.table, 'dc_daemon_delay_minutes', get_dev = True))
        self.iriedirect_channel_id = int(get_value(self._rastadb, self.table, 'i_direct_channel_id', get_dev = True))

    def get_vendors(self):
        vendor_list = list(select_from_table(self._rastadb, self.table, 'vendor'))

        vendor_dict = dict()
        for vendor in vendor_list:
            vendor_split = vendor.split(self.separator)
            vendor_dict[vendor_split[0]] = (vendor_split[1], vendor_split[2], vendor_split[3])
            #           vendor_acronym           vendor_name       vendor_website  vendor_thumbnail
        return vendor_dict

    def new_deal(self, vendor_acronym, deal_tuple, first_run = False):
        # If we're adding a deal, it has to be new. On the first run tho, don't put it in the new drops section.
        deal_str = self.separator.join(str(v) for v in deal_tuple)
        insert(self._rastadb, self.table, vendor_acronym, deal_str)  # Insert the permanent record

        if not first_run:
            insert(self._rastadb, self.new_table, vendor_acronym, deal_str)  # Add the expired or new record
            return

    # TODO: MAKE EXPIRED DEALS REMOVE THE PERMANENT RECORD
    def expired_deal(self, vendor_acronym, deal_tuple):
        deal_url = deal_tuple[1]
        remove_like_value(self._rastadb, self.table, vendor_acronym, deal_url)
        deal_str = self.separator.join(str(v) for v in deal_tuple)
        insert(self._rastadb, self.expired_table, vendor_acronym, deal_str)

    def clear_deals(self, table):
        for vendor in self.get_vendors():
            if table == self.expired_table:
                remove(self._rastadb, self.expired_table, vendor)
            if table == self.new_table:
                remove(self._rastadb, self.new_table, vendor)

    def get_deals(self, vendor_acronym = None, table = 'deals', search_term = None):
        if table != self.table:
            rows = list()
            for vendor_acronym in self.get_vendors():
                values = select_from_table(self._rastadb, table, vendor_acronym)
                for value in values:  # If this vendor has something to add, add it
                    rows.append(value)

        elif vendor_acronym:  # This is a call to show all deals for this vendor
            rows = select_from_table(self._rastadb, table, vendor_acronym)

        else:  # This is a search request, return every deal in existence
            rows = list()
            for vendor in self.get_vendors():
                rows.append(select_from_table(self._rastadb, table, vendor))

        return_list = list()
        for row in rows:
            row_split = row.split(self.separator)
            tup = (row_split[0], row_split[1], row_split[2], row_split[3], row_split[4], row_split[5].replace(r'\n', '\n'))
            #           name          url       image_url      amount         in_stock    description
            if search_term and search_term in tup[0]:
                return_list.append(tup)
            if not search_term:
                return_list.append(tup)

        return return_list


config_db = ConfigDB()
dealcatcher_db = DealCatcherDB()
welcome_db = WelcomeDB()
wordfilter_db = WordFilterDB()
podcast_db = PodcastDB()
reactions_db = ReactionsDB()
sounds_db = SoundsDB()
