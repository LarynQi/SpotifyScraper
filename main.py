import sys
import spotipy
import spotipy.util as util
import json
import os
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import requests

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
AUTH_TOKEN = client_credentials_manager.get_access_token(as_dict=False)

def show_tracks(tracks, sp):
	for i, item in enumerate(tracks['items']):
		track = item['track']
		# print('   %d %32.32s %s %s' % (i + 1, track['artists'][0]['name'], track['name'], sp.audio_features(track['id'])))
		# print('   %d %32.32s %s %s' % (i + 1, track['artists'][0]['name'], track['name'], sp.currently_playing()))
		print('   %d %32.32s %s' % (i + 1, track['artists'][0]['name'], track['name']))



def main():
	import os
	path = os.path.dirname(os.path.abspath(__file__))
	scope = 'playlist-read-private user-read-playback-state'
	setting = None
	if len(sys.argv) > 1:
		username = sys.argv[1]
		if len(sys.argv) > 2:
			setting = sys.argv[2]
	else:
		print('Usage: %s username' % (sys.argv[0],))
		sys.exit()
	try:
		token = util.prompt_for_user_token(username, scope)
	except Exception as e:
		print(e)
		sys.exit()

	if token:
		sp = spotipy.Spotify(auth=token)
		playlists = sp.user_playlists(username)
		result = ''
		options = {
			'1.': 'artists',
			'1' : 'artists',
			'Artists': 'artists',
			'artists': 'artists',
			'2.': 'genres',
			'2': 'genres',
			'Genres': 'genres',
			'genres': 'genres'
		}
		print('Select what you would like to see visualized:')
		print('1. Artists')
		print('2. Genres')
		content = input()
		while content not in options:
			if content == 'q' or content == 'quit' or content == 'exit':
				sys.exit()
			print('Invalid Option')
			content = input()
		content = options[content]
		print('Scraping...')
		for playlist in playlists['items']:
			# Can only access others' public playlists
			# print(playlist['name'])
			if playlist['owner']['id'] == username:
				try:
					tracks = sp.playlist(playlist['id'], fields='tracks, next')['tracks']
				except Exception as e:
					print(e)
					continue
				result += collect_data(tracks, sp, content)
				while tracks['next']:
					tracks = sp.next(tracks)
					result += collect_data(tracks, sp, content)
		print('Done!')
		if setting == 'ds':
			visualize(result, username, content, False)
		else:
			visualize(result, username, content)
				# print()
				# print(playlist['name'])
				# print('   total tracks', playlist['tracks']['total'])
				# results = sp.playlist(playlist['id'], fields='tracks,next')
				# tracks = results['tracks']
				# show_tracks(tracks, sp)
				# while tracks['next']:
				# 	tracks = sp.next(tracks)
				# 	show_tracks(tracks, sp)

		# artist_id = sp.currently_playing()['item']['artists'][0]['id']

		# os.system(f'curl -X "GET" "https://api.spotify.com/v1/artists/{artist_id}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {os.environ.get("AUTH_TOKEN")}" > data/data.json')
		# with open('./data/data.json', 'r') as f:
		# 	artist = json.load(f)
		# print(artist['genres'])


		# print(sp.recommendation_genre_seeds())
		# results = sp.current_user_saved_tracks()
		# for item in results['items']:
		# 	track = item['track']
		# 	print(track['name'] + ' - ' + track['artists'][0]['name'])
	else:
		print('Cannot get token for', username)

def collect_data(tracks, sp, content):
	result = ''
	if content == 'artists':
		collect = add_artist
	elif content == 'genres':
		collect = add_genre
	for i, item in enumerate(tracks['items']):
		track = item['track']
		for artist in track['artists']:
			result += collect(artist)
	return result

def add_genre(artist):
	### UNCOMMENT
	# try:
	# 	print(artist['name'])
	# 	os.system(f'curl --max-time 30 -X "GET" "https://api.spotify.com/v1/artists/{artist_id}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {AUTH_TOKEN}" > data/data.json')
	# 	# os.system(f'curl -X "GET" "https://api.spotify.com/v1/artists/{artist_id}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {os.environ.get("AUTH_TOKEN")}" > data/data.json')
	# 	with open('./data/data.json', 'r') as f:
	# 		artist_data = json.load(f)
	# 	for genre in artist_data['genres']:
	# 		result += f'{genre} '
	# except Exception as e:
	# 	print(e)
	# 	pass
	artist_id = artist['id']
	result = ''
	# https://curl.trillworks.com/
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {AUTH_TOKEN}'
	}
	url = f'https://api.spotify.com/v1/artists/{artist_id}'
	r = requests.get(url, headers=headers)
	artist_data = r.json()
	try:
		for genre in artist_data['genres']:
			result += f'{genre} '
	except Exception as e:
		print(f'No artist data found for {artist["name"]}')
	return result

def add_artist(artist):
	artist_id = artist['id']
	result = ''
	add = artist['name']
	if 'The' in add:
		add = add[:add.index('The')] + add[add.index('The') + 4:]
	result += f'{add} '
	return result

def visualize(genres, username, content, save=True):
	mask = np.array(Image.open('assets/mask3.jpg'))
	# t_mask = np.ndarray((mask.shape[0], mask.shape[1]), np.int32)
	# for i in range(len(mask)):
	# 	t_mask[i] = list(map(reformat, mask[i]))
	stopwords = set(STOPWORDS)
	stopwords.add('The')

	wc = WordCloud(stopwords=stopwords, background_color='white', mode='RGBA', max_words=100, mask=mask)
	# wc = WordCloud(stopwords=STOPWORDS, background_color='white', max_words=100)
	wc.generate(genres)
	count = 0
	check = f'{username}-{count}.png'
	while check in os.listdir('./assets'):
		count += 1
		check = f'{username}-{count}.png'
	if save:
		wc.to_file('./assets/' + check)

	colors = ImageColorGenerator(mask)
	plt.figure(figsize=[12.5, 5])
	# plt.imshow(wc, interpolation='bilinear')
	plt.title(f'{username}\'s {content}', fontsize=18)
	plt.imshow(wc.recolor(color_func=colors), interpolation='bilinear')
	plt.axis('off')
	if save:
		plt.savefig(f'./assets/{username}-{count}-plot.png')
	plt.show()

# def reformat(val):
# 	if val == 0:
# 		return 255
# 	else:
# 		return val

if __name__ == '__main__':
	main()