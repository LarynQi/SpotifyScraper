import sys
import spotipy
import spotipy.util as util
import json
import os

from spotipy.oauth2 import SpotifyClientCredentials

import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
AUTH_TOKEN = client_credentials_manager.get_access_token(as_dict=False)
print(AUTH_TOKEN)

def show_tracks(tracks, sp):
	for i, item in enumerate(tracks['items']):
		track = item['track']
		# print('   %d %32.32s %s %s' % (i + 1, track['artists'][0]['name'], track['name'], sp.audio_features(track['id'])))
		# print('   %d %32.32s %s %s' % (i + 1, track['artists'][0]['name'], track['name'], sp.currently_playing()))
		print('   %d %32.32s %s' % (i + 1, track['artists'][0]['name'], track['name']))



def main():
	import os
	path = os.path.dirname(os.path.abspath(__file__))
	scope = 'playlist-read-private, user-read-playback-state'
	if len(sys.argv) > 1:
		username = sys.argv[1]
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
		for playlist in playlists['items']:
			# Can only access others' public playlists
			print(playlist['name'])
			if playlist['owner']['id'] == username:
				try:
					tracks = sp.playlist(playlist['id'], fields='tracks, next')['tracks']
				except Exception as e:
					print(e)
					continue
				result += add_genres(tracks, sp)
				while tracks['next']:
					tracks = sp.next(tracks)
					result += add_genres(tracks, sp)
		visualize(result, username)
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

def add_genres(tracks, sp):
	result = ''
	for i, item in enumerate(tracks['items']):
		track = item['track']
		# print('   %d %32.32s %s %s' % (i + 1, track['artists'][0]['name'], track['name'], sp.audio_features(track['id'])))
		# print('   %d %32.32s %s %s' % (i + 1, track['artists'][0]['name'], track['name'], sp.currently_playing()))
		# print('   %d %32.32s %s' % (i + 1, track['artists'][0]['name'], track['name']))
		# print(track['name'], sp.audio_features(track['id']))
		# print(sp.currently_playing())
		for artist in track['artists']:
			artist_id = artist['id']
			# print(artist_id, artist['name'])
			# print(artist_id)

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


			add = artist['name']
			if 'The' in add:
				add = add[:add.index('The')] + add[add.index('The') + 4:]
			# result += f'{artist["name"]} '
			result += f'{add} '



	# result = filter()
	return result

def visualize(genres, username):
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
	wc.to_file('./assets/' + check)

	colors = ImageColorGenerator(mask)
	plt.figure(figsize=[12.5, 5])
	# plt.imshow(wc, interpolation='bilinear')
	plt.title(username)
	plt.imshow(wc.recolor(color_func=colors), interpolation='bilinear')
	plt.axis('off')
	plt.savefig(f'./assets/{username}-{count}-plot.png')
	plt.show()

# def reformat(val):
# 	if val == 0:
# 		return 255
# 	else:
# 		return val
if __name__ == '__main__':
	main()