from dealcatcher.utils import get_site
from rastadb import dealcatcher_db
from time import sleep

DWCA_WEBSITE = 'https://www.dudesworld.ca/product-category/irie/'
page_str = '' # Unused for DWCA
item_start_str = 'product type-product' # Generates an item's start_index in Deal object
thumbnail = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/255px-Flag_of_Canada_%28Pantone%29.svg.png'
acronym = 'dwca'
expired_table = 'deals_expired'
new_table = 'deals_new'


class DWCADeal:
	def __init__(self, website_html, start_index):
		self.name = self.get_name(website_html, start_index)
		self.url = self.get_url(website_html, start_index)
		self.image_url = self.get_image_url(website_html, start_index)
		self.amount = self.get_amount(website_html, start_index)
		self.description = ''
		self.in_stock = True # Deals are manually updated on DWCA
		self.reference_id = { # deal.reference_id.get(key)
			'discord': -1,
			'sheets' : -1
		}

	def __lt__(self, other):
		if type(other) is type(self):
				return (self.name < other.name)
		else:
			return NotImplemented
	def __le__(self, other):
			return (self.name <= other.name)
	def __gt__(self, other):
		return (self.name > other.name)
	def __ge__(self, other):
			return (self.name >= other.name)
	def __eq__(self, other):
		if type(other) is type(self):
			return (self.name == other.name)
		else:
			return NotImplemented
	def __ne__(self, other):
		if type(other) is type(self):
			return (self.name != other.name)
		else:
			return NotImplemented
	def __hash__(self):
		return hash(str(self))

	def get_name(self, website_html, start_index):
		item = "woocommerce-loop-product__title\">"
		terminal = "</h2>"
		name = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]
		return name

	def get_url(self, website_html, start_index):
		item = '<a href=\"'
		terminal = "\" class="
		url = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]
		return url

	def get_amount(self, website_html, start_index):
		item = '&#36;</span>'
		terminal = "</bdi>"
		amount = website_html[website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]

		return str(amount)

	def get_image_url(self, website_html, start_index):
		item = "src=\""
		terminal = "\" class="
		url = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]
		return url

def get_pages(html):
	pages = 1
	# LEAVING IN IN CASE DUDESWORLD GETS PAGES LATER
	# page_index = 0
	# while html.find('/page/{}'.format(pages + 1), page_index) != -1:
	# 	pages += 1
	# 	page_index = html.find('/page/{}'.format(pages), page_index + 1)
	return int(pages)

def get_all_dwca_deals(website):
	current_deals = []
	# Get a copy of the source
	html = get_site(website)

	# num_pages = get_pages(html)
	# print('num_pages: {}'.format(num_pages))
	# for page in range(1, num_pages + 1):
	# 	if page != 1:
	# 		html = dealcatcher.get_site('{}/page/{}/'.format(website, page))

	# Indent if you remove the above comments
	start_index = html.find(item_start_str)
	while(start_index != -1):
		deal_to_add = DWCADeal(html, start_index)
		#print('found deal {}'.format(deal_to_add.name))

		if deal_to_add.in_stock:
			current_deals.append(deal_to_add)
			start_index = html.find(item_start_str, start_index + 1)
		else:
			start_index = html.find(item_start_str, start_index + 1)

	return current_deals

def process_dwca_deals(old_dwca_deals): # Take old list, get new list, produce print/expired/update the old list
	deals_to_print = []
	expired_deals = []

	active_dwca_deals = get_all_dwca_deals(DWCA_WEBSITE)

	for new_deal in active_dwca_deals:
		if new_deal not in old_dwca_deals:
			deals_to_print.append(new_deal)

	for old_deal in old_dwca_deals:
		if old_deal not in active_dwca_deals:
			expired_deals.append(old_deal)

	old_dwca_deals = active_dwca_deals.copy()

	return (old_dwca_deals, deals_to_print, expired_deals)


def dwca_daemon(sleep_time):
	print('DudesWorld Canada Daemon started')

	old_deals = []
	first_run = True
	run = 0

	while True:
		run += 1

		old_deals, new_deals, expired_deals = process_dwca_deals(old_deals)

		new_deals_list = list()
		for deal in new_deals:
			new_deals_list.append((deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock, deal.description))

		expired_deals_list = list()
		for deal in expired_deals:
			expired_deals_list.append(
				(deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock, deal.description))

		for deal in new_deals_list:
			dealcatcher_db.new_deal(acronym, deal, first_run=first_run)
		for deal in expired_deals_list:
			dealcatcher_db.expired_deal(acronym, deal)

		sleep(sleep_time)
