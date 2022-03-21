from replit import db
import requests
import re

def check_new():
	channel = "https://www.youtube.com/c/TheGrowFromYourHeartPodcast"

	html = requests.get(channel + "/videos").text
	index = html.find("{\"videoId\":\"") + 12
	try:
		title = re.search('(?<={"text":").*?(?="})', html).group()
	except:
		return (None, None)
	url = 'https://www.youtube.com/watch?v={}'.format(html[index:index + 11])

	try:
		if db["podcast_title"] == title:
			return (None, None)
		else:
			db["podcast_title"] = title
			return (title, url)
	except:
		db["podcast_title"] = ''
		if db["podcast_title"] == title:
			return (None, None)
		else:
			db["podcast_title"] = title
			return (title, url)