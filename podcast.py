from replit import db
import os
import requests
import re

def get_image(url):
	img_data = requests.get(url).content

	return img_data

def download_image(url, name):
	os.chdir('/home/runner/RastaBot/all_images/')
	img_data = get_image(url)
	print('Downloaded {}'.format(name))
	with open(name, 'wb') as handler:
		handler.write(img_data)
		print('Wrote {}'.format(name))
	return img_data
	
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
print('Loaded podcast.py')