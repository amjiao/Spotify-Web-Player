from flask import Flask, request, redirect, jsonify, session, url_for, render_template
import requests
import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = os.getenv('SPOTIFY_CLIENT')
client_secret = os.getenv('SPOTIFY_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
scope = 'playlist-read-private user-modify-playback-state user-read-playback-state'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
  client_id=client_id,
  client_secret=client_secret,
  redirect_uri=redirect_uri,
  scope=scope,
  cache_handler=cache_handler,
  show_dialog=True
)
sp=Spotify(auth_manager=sp_oauth)

@app.route('/')
@app.route('/login')
def login():
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
  return render_template('search.html')

@app.route('/callback')
def callback():
  sp_oauth.get_access_token(request.args['code'])
  return render_template('search.html')

@app.route('/search/')
def search():
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
  
  query=request.args.get('spsearch')

  if query == None:
    return 'please enter a search value'
  
  searchResults = sp.search(query, limit=10, offset=0, type='track', market=None)
  tracks_info = [(track['name'], track['artists'][0]['name'], track['album']['name']) for track in searchResults['tracks']['items']]
  search_html = [(f'{name} by {artist} from {album}') for name, artist, album in tracks_info]
  tracks_uri = [track['uri'] for track in searchResults['tracks']['items']]
  

  return render_template(
    'searchResults.html',
    r1=search_html[0],
    uri1=tracks_uri[0],
    r2=search_html[1],
    uri2=tracks_uri[1],
    r3=search_html[2],
    uri3=tracks_uri[2],
    r4=search_html[3],
    uri4=tracks_uri[3],
    r5=search_html[4],
    uri5=tracks_uri[4],
    r6=search_html[5],
    uri6=tracks_uri[5],
    r7=search_html[6],
    uri7=tracks_uri[6],
    r8=search_html[7],
    uri8=tracks_uri[7]
  )

@app.route('/webplayer', methods=['POST'])
def webplayer():
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
  
  track_uri=request.form.get('track')
  track_info=sp.track(track_uri)
  preview_url = track_info['preview_url']

  ### for playing track in webplayer
  # track=(track_info['name'], track_info['artists'][0]['name'], track_info['album']['name'])
  # track_html = [(f'{name} by {artist} from {album}') for name, artist, album in track]

  # devices = sp.devices()
  # active_device = None
  # for device in devices['devices']:
  #   if device['is_active']:
  #     active_device = device
  #     break

  # if request.method == 'POST':
  #   if active_device:
  #     sp.start_playback(device_id=active_device['id'], uris=[track_uri])
  #   else:
  #     return "No active device found. Please start Spotify on one of your devices."

  return render_template('webplayer.html', preview_url=preview_url)

if __name__ == '__main__':
  app.run(debug=True)