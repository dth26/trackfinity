from flask import request, jsonify, send_from_directory, redirect, url_for, render_template, Response, stream_with_context
from myflaskapp import app, connection
import time
import logging
from models.userModel import createUserTable, createUser, getUser
from models.trackModel import createNewPlaylist, saveTrack, getPlaylistTracks, getTrackName, generatePlaylistURL, deleteTrack



@app.route("/deleteTrack", methods=['POST'])
def deleteTrackHandler():
	track_id = request.args.get('track_id')
	deleteTrack(track_id)
	return jsonify({'message':'success'})



@app.route("/playlist/<user>/<playlist_id>", methods=['GET'])
def getPlaylist(user, playlist_id):
	playlist_data = getPlaylistTracks(user, playlist_id)

	if len(playlist_data.keys()) == 0:
		message = "Playlist has expired or has been downloaded already!"
		return render_template('failure.html', message=message)
	else:
		tracks = playlist_data['tracks']
		owner = playlist_data['owner']
		message = playlist_data['message']
		playlist_name = playlist_data['playlist_name']
		return render_template('playlist.html', playlist=tracks, owner=owner, message=message, playlist_name=playlist_name)


@app.route("/music/<user>", methods=['GET'])
def music(user=''):
	message = 'Logged in as ' + user
	return render_template('music.html', rt_message=message, user=user)



@app.route("/streamPlaylistDownload")
def streamPlaylistDownload():
	print request.data
	playlist = request.args.get('playlist')
	print playlist


	return

	tracks = playlist['tracks']
	playlist_name = playlist['name']
	message = playlist['message']
	owner = playlist['user']
	playlist_id = int(time.time())

	# create playlist
	createNewPlaylist(playlist_id, playlist_name, message, owner)

	def generate():
		for song in tracks:
			result_dict = download(song['url'], song['artist'], song['track'])
			print 'successfully downloaded ' 
			print result_dict

			saveTrack(playlist_id, song['track'], song['artist'], owner)
			yield 'data:' + song['artist'] + ' - ' + song['track'] + '\n\n'

		print 'here handlePlaylistDownload'
		playlistURL = generatePlaylistURL(owner, playlist_id)
		yield 'data:' + playlistURL

	return Response(stream_with_context(generate()))


@app.route("/downloadPlaylist", methods=['POST'])
def handlePlaylistDownload():
	playlist = request.get_json()
	tracks = playlist['tracks']
	playlist_name = playlist['name'].replace("'",'')
	message = playlist['message'].replace("'",'')
	owner = playlist['user']

	playlist_id = int(time.time())

	# create playlist
	createNewPlaylist(playlist_id, playlist_name, message, owner)

	for song in tracks:
		saveTrack(song['url'], playlist_id, song['track'], song['artist'])


	playlistURL = generatePlaylistURL(owner, playlist_id)

	return jsonify({'playlistURL':playlistURL})



@app.route('/playlistSuccess', methods=['GET'])
def playlistSuccess(playlistURL=''):
	return render_template('success.html', playlistURL=playlistURL)



@app.route("/handleNewUser", methods=['POST'])
def handleNewUser():
	# un = request.form['usernameIn']
	# pw = request.form['passwordIn']

	data = request.get_json()
	un =data['un']
	pw = data['pw'] 

	rt_message = ''

	if createUser(un, pw) == 1:
		rt_message = ("Welcome %s, you can now create playlists and send it to a friend " % (un))
		url = ('%s/%s' % ('music', un))
	else:	
		rt_message = 'Username already exists!' 
		url = ('/?rt_message=%s' % (rt_message))
	
	
	return jsonify({'url':url,'un':un})


@app.route("/login", methods=["POST"])
def login():
	data = request.get_json()
	un =data['un']
	pw = data['pw'] 
	url = ''
	

	if getUser(un, pw) > 0:
		rt_message = ("Logged in as %s" % (un)) 
		url = ('%s/%s' % ('music', un))
	else:
		rt_message = ("Login credentials are invalid!")
		url = ('/?rt_message=%s' % (rt_message))

	return jsonify({'url':url,'un':un})


@app.route("/downloadSingleTrack", methods=['POST'])
def handleSingleTrackDownload():	
	youtubeURL = request.args.get('youtubeURL')
	artistName = request.args.get('artistName')
	trackName = request.args.get('trackName')
	playlist_id = ''

	result_dict = saveTrack(youtubeURL, playlist_id, trackName, artistName)
	return jsonify(result_dict)


@app.route('/getTrack', methods=['GET'])
def getTrack():
	artist = request.args.get('artist')
	track_name = request.args.get('track_name')
	filename =  getTrackName(artist, track_name)
	logging.debug('Getting Track ' + filename)
	return send_from_directory(app.config['DEST_DIR'],
                               filename,
                               as_attachment=True
                              )


@app.route('/getTestTrack', methods=['GET'])
def getTestTrack():
	filename = 'track - artist.m4a'
	return send_from_directory(app.config['DEST_DIR'],
                               filename,
                               as_attachment=True
                              )