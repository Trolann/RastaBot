import discord.errors

from rastadb import config_db
from features.irie_seeds import dealcatcher_db
import certifi
import urllib3
import random
from requests import get, ConnectionError
from discord import Embed


REQUEST_PREFIX = config_db.request_prefix


# TODO: Breakout dealcatcher (and dealcatcher_db) into its own container, see what changes to rastabot are needed (common volume/db folder likely)
# TODO: Dealcatcher interface, google sheets integration
# TODO: load deals on startup then only insert based on local variables -> ConfigDB (rastabot.config)
# TODO: When inserting new deals, change a variable rastabot checks before pulling data
# TODO: Initial DB setup scripts for RastaBot and DealCatcher
# TODO: RastaBot and Dealcatcher will need to share a single DB each in 4 separate containers
# TODO: RB: images -> media, media: dabtime.mp3, bot_images, deal_images (common volume with dealcatcher)
# TODO: DC: images: vendor_a, vendor_b
# TODO: DC: purge deal images on startup
# TODO: DC: Monitoring
# TODO: RB: more IrieDirect deals
# TODO: RB: cached string searches (search with what may be cached)

def _get_site(http, url):
    try:
        return http.request('GET', url)
    except Exception as e:
        _get_site(http, url)


def get_site(url):
    user_agent_list = (
        # Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        # Firefox
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
    )
    user_agent = random.choice(user_agent_list)
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        headers={'User-Agent': user_agent, "Accept-Language": "en-US, en;q=0.5"}
    )
    page = _get_site(http, url)

    return str(page._body)


def get_pages(html, page_str):
    pages = 1
    page_index = 0
    while html.find(page_str.format(pages + 1), page_index) != -1:
        pages += 1
        page_index = html.find(page_str.format(pages), page_index + 1)
    return int(pages)


def get_image(url):
    try:
        return get(url)
    except ConnectionError:
        return get('https://www.dudesworld.ca/wp-content/uploads/2021/06/logo-irie-genetics.png')


async def seed_vendor_request(message, channel):
    if "Trolan" not in str(message.author.name):
        config_db.update_count('seeds', config_db.get_count('seeds') + 1)

    vendors = dealcatcher_db.get_vendors()
    if len(message.content) > 7:

        requested_vendor = message.content[7:]
        requested_vendor = requested_vendor.lower()
        vendor_found = False
        vendor_acronym = vendor_name = vendor_website = vendor_thumbnail = ''

        for _vendor_acronym, _vendor_name, _vendor_website, _vendor_thumbnail in vendors:
            if _vendor_acronym == requested_vendor:
                vendor_found = True
                vendor_acronym = _vendor_acronym
                vendor_name = _vendor_name
                vendor_website = _vendor_website
                vendor_thumbnail = _vendor_thumbnail

        if not vendor_found:
            await channel.send('{} not found in seed vendors. Try $seeds'.format(requested_vendor))
            return

        embed = Embed(title="{} - In Stock".format(vendor_name), url=vendor_website, description="Current list of inventory at {}".format(vendor_name), color=0xff0000)
        embed.set_author(name="{} Current Inventory".format(vendor_name), url=vendor_website)
        embed.set_thumbnail(url=vendor_thumbnail)
        deal_list = dealcatcher_db.get_deals(vendor_acronym)
        for deal in deal_list:
            vendor, name, url, image_url, amount, in_stock, description = deal
            embed.add_field(name="• {}".format(name), value='[Buy here for ${}]({})'.format(round(float(amount)), url), inline=True)
        try:
            await channel.send(embed=embed)
        except discord.errors.HTTPException:  # Message is too big to send and we need to split it.
            await channel.send('Sorry, looks like this is too big to send. <@320988843677581333> needs to look into it.')
        return
    else:
        embed = Embed(title="Irie Genetics Seed List", description="A list of all Irie Genetics seeds RastaBot currently knows about. This doesn't include every vendor and may not perfectly match actual inventories. \n Use {}seeds as shown to see an individual menu and get the URL directly to the vendor.".format(REQUEST_PREFIX))
        for vendor_acronym, vendor_name, vendor_website, vendor_thumbnail in vendors:
            deal_list = dealcatcher_db.get_deals(vendor_acronym)
            if deal_list:
                strain_count = 0
                low_price = float('inf')

                for vendor, name, url, image_url, amount, in_stock, description in deal_list:
                    if float(amount) < float(low_price):
                        low_price = float(amount)
                    strain_count += 1

                embed.add_field(name="{} - {}seeds {}".format(vendor_name, REQUEST_PREFIX, vendor_acronym),
                                value='[{}]({}) has {} different packs of seeds for as low as ${}'.format(vendor_name, vendor_website, strain_count, round(float(low_price))), inline=False)
        embed.set_footer(text="Example: {}seeds mgg".format(REQUEST_PREFIX))
        await channel.send(embed=embed)
        return


async def strain_request(message, channel):
    if "Trolan" not in str(message.author.name):
        config_db.update_count('seeds', config_db.get_count('seeds') + 1)

    if len(message.content) < 8:
        embed = Embed(title="How to use RastaBot search", description="{}strain searchterm")
        embed.set_footer(text="Use 1 unique word for best results. eg: 'jack ripper' will not find 'jack the ripper' however 'ripper' will find jack the ripper and jack tripper")
        await channel.send(embed=embed)
        return

    search_term = message.content[8:].lower()
    embed = Embed(title="Search Results")
    vendors = dealcatcher_db.get_vendors()
    found = False

    for vendor_acronym, vendor_name, vendor_website, vendor_thumbnail in vendors:
        deal_list = dealcatcher_db.get_deals(vendor_acronym)
        vendor_found = False
        deal_string = ''
        for _vendor_acronym, name, url, image_url, amount, in_stock, description in deal_list:
            if search_term in name.lower():
                vendor_found = True
                deal_string += '[{} (${})]({}), '.format(name, round(float(amount)), url)
        if not vendor_found:
            continue
        found = True
        deal_string = deal_string[:-2]
        last_comma = deal_string.rfind(',')
        if last_comma > 1:
            temp = list(deal_string)
            temp[last_comma] = ' and'
            deal_string = "".join(temp)

        embed.add_field(name="{} ({}seeds {})".format(vendor_name, REQUEST_PREFIX, vendor_acronym), value=deal_string, inline=False)

    if not found:
        await channel.send(
            "Sorry {}, I couldn't find {}. You can try a different search, or use {}iriedirect or {}seeds to see what everyone has.".format(message.author.mention, search_term, REQUEST_PREFIX, REQUEST_PREFIX))
        return

    await channel.send(embed=embed)
