# For not hammering requests
from time import sleep
from rastadb import dealcatcher_db
from pathlib import Path

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


class IrieDirectDeal:
    def __init__(self, website_html, start_index):
        self.url = self.get_url(website_html, start_index)
        self.name = self.get_name(website_html, start_index)
        self.product_html = get_site(self.url)
        self.image_url = self.get_image_url(website_html, start_index)
        self.amount = self.get_amount(website_html, start_index)
        self.description = self.get_description()
        self.in_stock = self.check_stock()

    def __lt__(self, other):
        if type(other) is type(self):
            return self.name < other.name
        else:
            return NotImplemented

    def __le__(self, other):
        return self.name <= other.name

    def __gt__(self, other):
        return self.name > other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name
        else:
            return NotImplemented

    def __ne__(self, other):
        if type(other) is type(self):
            return self.name != other.name
        else:
            return NotImplemented

    def __hash__(self):
        return hash(str(self))

    def get_name(self, website_html, start_index):
        item = "<h3><a href=\"" + self.url + "\">"
        terminal = "</a></h3>"
        name = website_html[website_html.find(item, start_index) + len(item): website_html.find(terminal, website_html.find(item, start_index) + len(item))]
        name = name.replace('&#8217;', '\'')
        name = name.replace('\\xc3\\xa9', 'é')
        return name

    def get_url(self, website_html, start_index):
        item = "<a href=\""
        terminal = "\"><"
        url = website_html[website_html.find(item, start_index) + len(item): website_html.find(terminal, website_html.find(item, start_index) + len(item))]
        return url

    def get_amount(self, website_html, start_index):
        # For now, if there's a sale just run the price search again and get the sale amount.
        # Pull out normal price
        item = '&#36;</span>'
        terminal = "</bdi>"
        amount = website_html[website_html.find(item, start_index - 1) + len(item): website_html.find(terminal, website_html.find(item, start_index - 1) + len(item))]

        # If there's a sale, pull out sale amount
        if website_html.find("Sale!", start_index, website_html.find("</li>", start_index)) > 0:
            start_index = website_html.find(item, start_index) + 1  # Start at the normal price
            amount = website_html[website_html.find(item, start_index) + len(item): website_html.find(terminal, website_html.find(item, start_index) + len(item))]

        return str('{}0'.format(amount))

    def get_image_url(self, website_html, start_index):
        item = "src=\""
        terminal = "\""
        url = website_html[website_html.find(item, start_index) + len(item): website_html.find(terminal, website_html.find(item, start_index) + len(item))]
        ftype = url.split('/')[-1].lower()
        ftype = ftype[:ftype.find('?')]
        if not Path(f'{dealcatcher_db.dir_path}/{ftype}').is_file():
            myfile = get_image(url)
            open('{}images/{}'.format(dealcatcher_db.dir_path, ftype), 'wb').write(myfile.content)
        return '{}images/{}'.format(dealcatcher_db.dir_path, ftype)

    def check_stock(self):
        if "out-of-stock" in self.product_html:
            return False
        return True

    def get_description(self):
        description = ''
        raw_description = self.product_html[self.product_html.find(
            "woocommerce-product-details__short-description"): self.product_html.find("---<br>")]
        index = raw_description.find("<p>")
        while index > 0:
            end_index = raw_description.find("</p", index)
            line = str(raw_description[index + 3: end_index])
            new_line = line.replace("Pre-&#8217;98", "Pre-'98")
            line = new_line
            new_line_i = line.find("Saka")
            while new_line_i > 0:
                temp = line[:new_line_i + 4] + " Soufflé " + line[new_line_i + 20:]
                line = temp
                new_line_i = line.find("Saka", new_line_i + 1)

            if line != '&nbsp;':
                if line.startswith('Check out the podcast on The Machine '):
                    description += "Check out the podcast on The Machine: https://youtu.be/PssnmZdozr4"
                else:
                    description += "{}\n".format(line)
            index = raw_description.find("<p>", index + 1)

        if len(description) > 700:
            description = description[:700]

        return description


def get_all_deals(website):
    current_deals = []
    # Get a copy of the source
    html = get_site(website)

    num_pages = get_pages(html, page_str)
    for page in range(1, num_pages + 1):
        if page != 1:
            html = get_site('{}{}'.format(website, page_str.format(page)))

        start_index = html.find(item_start_str)
        while start_index != -1:
            deal_to_add = IrieDirectDeal(html, start_index)

            if deal_to_add.in_stock:
                current_deals.append(deal_to_add)
                start_index = html.find(item_start_str, start_index + 1)
            else:
                start_index = html.find(item_start_str, start_index + 1)

    return current_deals


def process_deals(old_deals):  # Take old list, get new list, produce print/expired/update the old list
    new_deals = []
    expired_deals = []

    active_deals = get_all_deals(website)

    for deal in active_deals:
        if deal not in old_deals:
            new_deals.append(deal)

    for old_deal in old_deals:
        if old_deal not in active_deals:
            expired_deals.append(old_deal)

    old_deals = active_deals.copy()
    return old_deals, new_deals, expired_deals


def iriedirect_daemon(sleep_time):
    print('IrieDirect Daemon started')

    old_deals = list()

    first_run = True  # False = will populate deals table with all values

    while True:
        old_deals, new_deals, expired_deals = process_deals(old_deals)

        new_deals_list = list()
        for deal in new_deals:
            new_deals_list.append((deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock, deal.description))

        expired_deals_list = list()
        for deal in expired_deals:
            expired_deals_list.append((deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock, deal.description))

        for deal in new_deals_list:
            dealcatcher_db.new_deal(acronym, deal, first_run = first_run)
        for deal in expired_deals_list:
            dealcatcher_db.expired_deal(acronym, deal)

        first_run = False
        sleep(sleep_time)


async def iriedirect_check_for_drop(irie_guild):
    new_deals_list = dealcatcher_db.get_deals(acronym, new_table)
    if new_deals_list:
        print(dealcatcher_db.iriedirect_channel_id)
        irie_direct_channel = irie_guild.get_channel(int(dealcatcher_db.iriedirect_channel_id))
        print(irie_direct_channel)
        for name, url, image_url, amount, in_stock, description in new_deals_list:
            embed = Embed(color=0xfd0808, title=name, url=url, description="On sale for ${}".format(round(float(amount))))
            file = File(image_url, filename="image.png")
            embed.set_image(url="attachment://{}".format(image_url))
            embed.add_field(name="Description:", value=str(description), inline=False)
            try:
                await irie_direct_channel.send(embed=embed, file=file)
            except HTTPException as e:
                f = open(acronym + '_error_log.txt', 'a')
                f.write(str(e))
                f.close()
        dealcatcher_db.clear_deals(new_table)

    #expired_deals_list = dealcatcher_db.get_deals(acronym, expired_table)
    expired_deals_list = list()
    if expired_deals_list:
        irie_direct_channel = irie_guild.get_channel(dealcatcher_db.iriedirect_channel_id)
        for name, url, image_url, amount, in_stock, description in expired_deals_list:
            embed = Embed(title=name, url=url,
                          description="IS NOW SOLD OUT! Follow this channel for notifications on the next drop".format(
                              amount))
            await irie_direct_channel.send(embed=embed)
        dealcatcher_db.clear_deals(expired_table)


async def irie_direct_request(irie_guild, message, channel):
    if "Trolan" not in message.author.name:
        count_iriedirect()

    deal_list = dealcatcher_db.get_deals(acronym)
    if 'list' in message.content:
        deal_string = ''
        for name, url, image_url, amount, in_stock, description in deal_list:
            deal_string += '{} (${}), '.format(name, round(float(amount)))
        deal_string = deal_string[:-2]
        last_comma = deal_string.rfind(',')
        if last_comma > 1:
            temp = list(deal_string)
            temp[last_comma] = ' and'
            deal_string = "".join(temp)
        await channel.send("Irie-Direct (https://www.iriegenetics.com/irie-direct/) currently has {} in stock. Get them before they're gone!".format(deal_string))
        return

    embed = Embed(title="Irie Direct - In Stock", url="https://www.iriegenetics.com/irie-direct/",
                  description="Current list of inventory at IrieGenetics.com", color=0x00ff00)
    embed.set_author(name="Irie Direct Current Inventory", url="https://www.iriegenetics.com/irie-direct/")
    embed.set_thumbnail(url="https://secureservercdn.net/45.40.150.47/wb1.a3e.myftpupload.com/wp-content/uploads/2020/11/irie-logo.png")

    send2 = False
    if len(deal_list) > 24:
        send2 = True
        embed2 = Embed(description="Continued list of inventory at IrieGenetics.com", color=0x00ff00)
        embed2.set_author(name="Inventory continued from above", url="https://www.iriegenetics.com/irie-direct/")
        embed2.set_thumbnail(url="https://secureservercdn.net/45.40.150.47/wb1.a3e.myftpupload.com/wp-content/uploads/2020/11/irie-logo.png")
    i = 0
    for deal in deal_list:
        name, url, image_url, amount, in_stock, description = deal
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
