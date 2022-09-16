from rastadb import config_db, podcast_db
import os
import requests
import re
from discord import Streaming, Status
global first_call
first_call = True

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
		return None, None, None
	url = 'https://www.youtube.com/watch?v={}'.format(html[index:index + 11])
	number = int(title[1:4])
	new = True if number > podcast_db.get_current('number') else False
	if new:
		podcast_db.new_podcast(number, title, url)

	return title, url, number, new


async def auto_status(client, irie_guild):
	global first_call
	if podcast_db.get_auto_status():
		name, url, num, new = check_new()
		if new and not first_call:
			podcast_db.new_podcast(num, name, url)
			print('bot_channel_id {}'.format(config_db.bot_channel_id))
			bot_channel = irie_guild.get_channel(config_db.bot_channel_id)
			print('bot_channel {}'.format(bot_channel))
			gfyh_podcast_channel = irie_guild.get_channel(podcast_db.podcast_channel_id)
			await bot_channel.send('Found a new podcast. Updating')
			await gfyh_podcast_channel.send("Episode {} of the Grow From Your Heart ({}) podcast has been posted! \n {}".format(num, name, url))
			print('New podcast found: {} at {}'.format(num, url))
		first_call = False
		stream = Streaming(url = url, name = 'GFYH Podcast #{}'.format(num), platform = 'YouTube')
		await client.change_presence(status=Status.online, activity=stream)

print('Loaded podcast.py')
