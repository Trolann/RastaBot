# For not hammering requests
from time import sleep
from rastadb import config_db
from irie_seeds import dealcatcher_db, rastadeals_db
global new_deals_list
global expired_deals_list

# For requests (needed for ssl)
from dealcatcher.utils import get_site, get_pages, get_image

# For IrieDirect drop alerts
from discord import Embed, File, HTTPException

# Basic counter
from count import iriedirect as count_iriedirect

website = 'https://iriedirect.com/irie-direct/'
page_str = 'page/{}'
item_start_str = 'product type-product'  # Generates an item's start_index in Deal object
acronym = 'iriedirect'
expired_table = 'deals_expired'
new_table = 'deals_new'
thumbnail = 'https://www.dudesworld.ca/wp-content/uploads/2021/06/logo-irie-genetics.png'


def get_image_url(url):
    ftype = url.split('/')[-1].lower()
    ftype = ftype[:ftype.find('?')]
    myfile = get_image(url)
    open('{}images/{}'.format(config_db.environ_path, ftype), 'wb').write(myfile.content)
    return '{}images/{}'.format(config_db.environ_path, ftype)


def iriedirect_drop_daemon():
    print('drop daemon started')
    simmer = 0
    global new_deals_list
    global expired_deals_list
    new_deals_list = list()  # New deals as compared between last known RastaBot deals and most recent known DealCatcher deals
    expired_deals_list = list()  # Same thing as above but different


    _expired_double_check = list()  # Used to only remove expired deals if they have been expired for 2 checks

    while True:

        internal_deals = rastadeals_db.get_deals(acronym)
        internal_deals_list = list()
        # Generate tuples for every deal object
        for vendor, name, url, image_url, amount, in_stock, description in internal_deals:
            deal_tuple = (name, url, image_url, amount, in_stock, description)
            internal_deals_list.append(deal_tuple)

        current_deals = dealcatcher_db.get_deals(acronym)
        current_deals_list = list()

        for vendor, name, url, image_url, amount, in_stock, description in current_deals:
            deal_tuple = (name, url, image_url, amount, in_stock, description)
            current_deals_list.append(deal_tuple)

        for current_deal in current_deals_list:
            current_name, current_url, current_image_url, current_amount, current_in_stock, current_description = current_deal
            deal_internal = False
            for internal_name, internal_url, internal_image_url, internal_amount, internal_in_stock, internal_description in internal_deals_list:
                if current_url == internal_url:
                    deal_internal = True
                    continue
            if not deal_internal:
                print(f'ADDED: {current_name}')
                new_deals_list.append(current_deal)
                rastadeals_db.new_deal(acronym, current_deal)  # Inserts into the DB for next restart

        # First time deal is expired, let it chill
        # Generate a global list of expired deals: these will get posted to the channel
        for internal_deal in internal_deals_list:
            internal_name, internal_url, internal_image_url, internal_amount, internal_in_stock, internal_description = internal_deal
            deal_current = False
            for current_name, current_url, current_image_url, current_amount, current_in_stock, current_description in current_deals_list:
                if internal_url == current_url:
                    deal_current = True
                    continue
            if not deal_current:
                print(f'EXPIRED: {internal_name}')
                if internal_deal in _expired_double_check:
                    expired_deals_list.append(internal_deal)  # For the drop check to see and clear
                    rastadeals_db.expired_deal(acronym, internal_deal)  # Removes from DB for next restart
                    _expired_double_check.remove(internal_deal)  # Removes from being double-checked again
                else:
                    # First time deal is expired, let it chill
                    _expired_double_check.append(internal_deal)

        sleep(10)


async def iriedirect_check_for_drop(irie_guild):
    global new_deals_list
    global expired_deals_list

    if new_deals_list:
        _new_deals_list = new_deals_list
        new_deals_list = list()  # Clear the list as we'll process all of these
        irie_direct_channel = irie_guild.get_channel(int(config_db.irie_direct_channel_id))

        for name, url, image_url, amount, in_stock, description in _new_deals_list:
            name = name.replace('&#8217;', '\'')
            name = name.replace('\\xc3\\xa9', 'é')
            embed = Embed(color=0xfd0808, title=name, url=url, description="On sale for ${}".format(round(float(amount))))
            file = File(get_image_url(image_url), filename="image.png")
            embed.set_image(url="attachment://{}".format(get_image_url(image_url)))
            embed.add_field(name="Description:", value=str(description), inline=False)
            try:
                await irie_direct_channel.send(embed=embed, file=file)
            except HTTPException as e:
                f = open(acronym + '_error_log.txt', 'a')
                f.write(str(e))
                f.close()

    if expired_deals_list:
        _expired_deals_list = expired_deals_list
        expired_deals_list = list()
        irie_direct_channel = irie_guild.get_channel(config_db.irie_direct_channel_id)
        for name, url, image_url, amount, in_stock, description in _expired_deals_list:
            name = name.replace('&#8217;', '\'')
            name = name.replace('\\xc3\\xa9', 'é')
            embed = Embed(title=name, url=url,
                          description="IS NOW SOLD OUT! Follow this channel for notifications on the next drop".format(
                              amount))
            try:
                await irie_direct_channel.send(embed=embed)
                expired_deals_list.remove((name, url, image_url, amount, in_stock, description))
            except HTTPException as e:
                f = open(acronym + '_error_log.txt', 'a')
                f.write(str(e))
                f.close()


async def irie_direct_request(irie_guild, message, channel):
    if "Trolan" not in message.author.name:
        count_iriedirect()

    deal_list = rastadeals_db.get_deals(acronym)
    if 'list' in message.content:
        deal_string = ''
        for name, url, image_url, amount, in_stock, description in deal_list:
            name = name.replace('&#8217;', '\'')
            name = name.replace('\\xc3\\xa9', 'é')
            deal_string += '{} (${}), '.format(name, round(float(amount)))
        deal_string = deal_string[:-2]
        last_comma = deal_string.rfind(',')
        if last_comma > 1:
            temp = list(deal_string)
            temp[last_comma] = ' and'
            deal_string = "".join(temp)
        await channel.send("IrieDirect.com (https://www.iriedirect.com) currently has {} in stock. Get them before they're gone!".format(deal_string))
        return

    embed = Embed(title="Irie Direct - In Stock", url="https://www.iriedirect.com",
                  description="Current list of inventory at IrieDirect.com", color=0x00ff00)
    embed.set_author(name="Irie Direct Current Inventory", url="https://www.iriedirect.com")
    embed.set_thumbnail(url=thumbnail)

    send2 = False
    embed2 = Embed(description="Continued list of inventory at IrieDirect.com", color=0x00ff00)
    if len(deal_list) > 24:
        send2 = True

        embed2.set_author(name="Inventory continued from above", url="https://www.iriedirect.com")
        embed2.set_thumbnail(url=thumbnail)
    i = 0
    for deal in deal_list:
        vendor, name, url, image_url, amount, in_stock, description = deal
        name = name.replace('&#8217;', '\'')
        name = name.replace('\\xc3\\xa9', 'é')
        if i < 24:
            embed.add_field(name="• {}".format(name), value='[Buy here for ${}]({})'.format(round(float(amount)), url),
                            inline=True)
        else:
            embed2.add_field(name="• {}".format(name), value='[Buy here for ${}]({})'.format(round(float(amount)), url),
                             inline=True)
        i += 1
    await channel.send(embed=embed)
    if send2:
        await channel.send(embed=embed2)
