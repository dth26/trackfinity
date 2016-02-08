from myflaskapp import app, connection
from flask import jsonify
import time
import os
import logging
import subprocess

# command to access db: psql trackfinity adminvjvhien

def createTrackTable():
	connection.execute(    
		"""
	    CREATE TABLE tracks (
	        playlistid,
	        trackid,
	        artist,
	        track_name
	    );
	    """
    )

def createPlaylistTable():
	connection.execute(
		"""
		CREATE TABLE playlist(
			id VARCHAR PRIMARY KEY,
			name VARCHAR NOT NULL,
			owner VARCHAR NOT NULL
		);
		"""
	)

def saveTrack(youtubeURL, playlist_id, trackName, artistName):
	result_dict = dict()

	trackName = trackName.replace("'",'').replace('"','')
	artistName = artistName.replace("'",'').replace('"','')


	track_id = int(time.time())

	query_str = ("""INSERT INTO tracks (trackid, playlistid, artist, track_name) VALUES ('%s', '%s','%s','%s'); """ % (track_id, playlist_id, artistName, trackName))
	if connection.execute(query_str):

		# only download if song does not already exist in $OPENSHIFT_DATA_LOG
		query_str = ("""SELECT * FROM tracks WHERE track_name='%s' AND artist='%s'""" % (trackName, artistName))
		result = connection.execute(query_str)

		result_dict['artist'] = artistName
		result_dict['track_name'] = trackName
		result_dict['track_id'] = track_id

		if result.rowcount <= 1:						# only need to save one copy of track
			download(youtubeURL, artistName, trackName, track_id)
		else:
			time.sleep(1)		# must sleep in case track is already downloaded, then track_id may yield duplicates if data is processed to quickly


	return result_dict


def deleteTrack(track_id):
	query_str = ("""SELECT * FROM tracks WHERE trackid='%s'""" % (track_id))
	result = connection.execute(query_str).fetchall()[0]
	artistName = result['artist']	
	trackName = result['track_name']

	time.sleep(1)	# make sure user gets track before it is deleted

	query_str = ("""DELETE FROM tracks WHERE trackid='%s'""" % (track_id))
	if connection.execute(query_str):
		# only delete file if track no longer exists in tracks table
		query_str = ("""SELECT * FROM tracks WHERE track_name='%s' AND artist='%s'""" % (trackName, artistName))
		result = connection.execute(query_str)

		if result.rowcount == 0:
			filename = getTrackName(artistName, trackName)
			path_to_track = ('"%s/%s"' % (app.config['DEST_DIR'], filename))
			cmd = ("""rm %s""" % (path_to_track))
			os.popen(cmd)
		rt_val = 1
	return rt_val



def createNewPlaylist(playlist_id, playlist_name, message, user):
	print ('Creating playlist %s' % (playlist_id))
	rt_val = 0
	query_str = ("""INSERT INTO playlist (owner, message, id, name) VALUES ('%s', '%s','%s','%s'); """ % (user, message, playlist_id, playlist_name))
	if connection.execute(query_str):
		rt_val = 1

	return rt_val



def getPlaylistTracks(user, playlist_id):
	query_str = ("""SELECT artist, track_name, trackid FROM playlist INNER JOIN tracks ON tracks.playlistID=playlist.id WHERE playlist.id='%s' AND playlist.owner='%s' """ % (playlist_id,user))
	#result = connection.execute(query_str).fetchall()

	result_dict = dict()
	result_list= list()

	result = connection.execute(query_str)

	if result.rowcount != 0:
		for row in result.fetchall():
			row_dict = dict(row)
			result_list.append(row_dict)

		query_str = ("""SELECT name,owner,message FROM playlist WHERE id='%s' AND owner='%s' """ % (playlist_id, user))
		playlist_results = connection.execute(query_str).fetchall()[0]

		result_dict['tracks'] = result_list
		result_dict['owner'] = playlist_results['owner']
		result_dict['message'] = playlist_results['message']
		result_dict['playlist_name'] = playlist_results['name']
	
	return result_dict



# create a url for a client to send friend a playlist
def generatePlaylistURL(user_name, playlist_id):
	return ('%splaylist/%s/%s' % (app.config['BASE_URL'], user_name, playlist_id))


# this is the name of the mp3 saved on disk located at $OPENSHIFT_DATA_DIR
def getTrackName(artistName, trackName):
	return  ('%s - %s.mp3' % (trackName, artistName))



def download(youtubeURL, artistName, trackName, track_id):
	# name of file being saved on disk
	filename = getTrackName(artistName, trackName)
	outputTemplate = ('%s/%s' % (app.config['DEST_DIR'] , filename))

	print('downloading ' + filename + ' to ' + outputTemplate)

	try:
		if 'soundcloud' in youtubeURL:
			p = subprocess.Popen([app.config['BINARY'],'--audio-format','mp3', '-o', outputTemplate, '-q', youtubeURL])
		else:
			print 'youtube'
			p = subprocess.Popen([app.config['BINARY'],'-v','--extract-audio', '--audio-format','mp3', '-o', outputTemplate, '-q', youtubeURL])
			#p = subprocess.Popen([app.config['BINARY'],'-v','--extract-audio', '-o', outputTemplate, '-q', youtubeURL])
			# youtube-dl -v --extract-audio  --audio-format mp3 -o '/var/lib/openshift/569c2ca47628e1fb2c000136/app-root/data/track - artist.%(ext)s' https://www.youtube.com/watch?v=UKp2CrfmVfw
			# youtube-dl -v --extract-audio -o '/Users/hui/Documents/youtubedl/track - artist.%(ext)s' https://www.youtube.com/watch?v=UKp2CrfmVfw
			# youtube-dl -v --extract-audio --audio-format mp3 -o '/Users/hui/Documents/youtubedl/track3.mp3' https://www.youtube.com/watch?v=UKp2CrfmVfw
			# youtube-dl -v --extract-audio --audio-format mp3  https://www.youtube.com/watch?v=UKp2CrfmVfw
		p.communicate()
		print 'after communication'
	except:
		print 'exception'
		pass

	result_dict = dict()
	result_dict['artistName'] = artistName
	result_dict['trackName'] = trackName
	result_dict['filename'] = filename

	return jsonify(result_dict)




	