from rastabot import get_site
from rastabot import get_pages
from replit import db
from time import sleep

def shn_daemon(sleep_time):
	print('SeedsHereNow Daemon started')
	
	old_deals = []
	first_run = True
	run = 0

	
	while True:
		run += 1
		if run % 10 == 0:
			print('SHN run: {}'.format(run))
		old_deals, deals_to_print, expired_deals = process_shn_deals(old_deals)

		all_deals_list = []
		for deal in old_deals:
			all_deals_list.append((deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock))

		try:
			new_deals_list = list(db["new_shn_deals_list"])
		except:
			new_deals_list = list()
		if not new_deals_list:
			new_deals_list = []
		if not first_run:
			for deal in deals_to_print:
				new_deals_list.append((deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock))

		try:
			expired_deals_list = db["expired_shn_deals_list"]
		except:
			expired_deals_list = list()
		
		if not expired_deals_list:
			expired_deals_list = []
		for deal in expired_deals:
			expired_deals_list.append((deal.name, deal.url, deal.image_url, deal.amount, deal.in_stock))

		db["all_shn_deals_list"] = all_deals_list
		db["new_shn_deals_list"] = new_deals_list
		db["expired_shn_deals_list"] = list(expired_deals_list)
		first_run = False
		sleep(sleep_time)