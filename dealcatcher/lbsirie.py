from dealcatcher.utils import get_site
from dealcatcher.utils import get_pages
from rastadb import dealcatcher_db
from time import sleep

LBS_WEBSITE = 'https://www.lbseedco.com/collections/irie-genetics'
page_str = '?page={}' # Page not tested, assume 1 page
item_start_str = "<li class=\"grid__item\">" # Generates an item's start_index in Deal object
thumbnail = 'https://cdn.shopify.com/s/files/1/0601/7761/3055/products/LBS-LOGO.jpg?v=1655414326'
acronym = 'lbs'
expired_table = 'deals_expired'
new_table = 'deals_new'


class LBSDeal:
	def __init__(self, website_html, start_index):
		self.name = self.get_name(website_html, start_index)
		self.url = self.get_url(website_html, start_index)
		self.image_url = self.get_image_url(website_html, start_index)
		self.amount = self.get_amount(website_html, start_index)
		self.in_stock = self.check_stock(website_html, start_index)
		self.description = ''
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
		item = "full-unstyled-link\">"
		terminal = "</a>"
		name = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]
		
		for i in range(0,len(name)):
			if name[i].isupper():
				name = name[i:name.find('\\', i)]
				break
		
		if name.startswith("Saka") or name.startswith("SAKA"):
			name = "Saka Soufflé"
		return name

	def get_url(self, website_html, start_index):
		item = "<a href=\""
		terminal = "\" class="
		url = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]	
		return LBS_WEBSITE + url

	def get_amount(self, website_html, start_index):
		# Pull out normal price
		item = '$'
		terminal = "<"
		amount = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]	

		# If there's a sale, pull out sale amount
		if website_html.find("Sale!", start_index, website_html.find("</li>", start_index)) > 0:
			start_index = website_html.find(item, start_index) + 1 # Start at the normal price
			amount = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]	
			
		return float(amount[:4])

	def get_image_url(self, website_html, start_index):
		item = "srcset=\""
		terminal = "?"
		url = website_html[ website_html.find(item, start_index) + len(item) : website_html.find(terminal, website_html.find(item, start_index) + len(item)) ]
		if url.find('irie-logo') > 0:
			first_location = website_html.find(item, start_index) + len(item)
			url = website_html[ website_html.find(item, first_location) + len(item) : website_html.find(terminal, website_html.find(item, first_location) + len(item)) ]
		return url

	def check_stock(self, website_html, start_index):
		item = "Out of stock"
		terminal = '</li>'
		end_index = website_html.find('{}'.format(terminal), start_index + 1)
		stock_start_index = website_html.find("{}".format(item), start_index, end_index)
		if stock_start_index > 0:
			return False
		else:
			return True	

def get_pages(html):
	pages = 1
	# All pages are returned in the metadata on the first page.
	return int(pages)

def get_all_lbs_deals(website):
	current_deals = []
	# Get a copy of the source
	html = get_site(website)

	num_pages = get_pages(html)
	for page in range(1, num_pages + 1):
		if page != 1:
			html = get_site('{}{}'.format(website, page_str.format(page)))

		start_index = html.find(item_start_str)
		while(start_index != -1):
			deal_to_add = LBSDeal(html, start_index)

			if deal_to_add.in_stock:
				current_deals.append(deal_to_add)
				start_index = html.find(item_start_str, start_index + 1)
			else:
				start_index = html.find(item_start_str, start_index + 1)

	return current_deals

def process_lbs_deals(old_lbs_deals): # Take old list, get new list, produce print/expired/update the old list
	deals_to_print = []
	expired_deals = []

	active_lbs_deals = get_all_lbs_deals(LBS_WEBSITE)

	for new_deal in active_lbs_deals:
		if new_deal not in old_lbs_deals:
			deals_to_print.append(new_deal)

	for old_deal in old_lbs_deals:
		if old_deal not in active_lbs_deals:
			expired_deals.append(old_deal)

	old_lbs_deals = active_lbs_deals.copy()

	return (old_lbs_deals, deals_to_print, expired_deals)

def lbs_daemon(sleep_time):
	print('LB Seeds Daemon started')
	
	old_deals = []
	first_run = True
	run = 0

	while True:
		run += 1

		old_deals, new_deals, expired_deals = process_lbs_deals(old_deals)

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