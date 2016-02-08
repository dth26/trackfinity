from flask import Flask, render_template, request, jsonify, send_from_directory
from sqlalchemy import *
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys
import atexit
import time
import logging


app = Flask(__name__)
app.config['BINARY'] = '/var/lib/openshift/569c2ca47628e1fb2c000136/app-root/runtime/dependencies/python/virtenv/bin/youtube-dl'
app.config['DEST_DIR'] = '/var/lib/openshift/569c2ca47628e1fb2c000136/app-root/data'
app.config['POSTGRESQL_DB_HOST'] = os.environ['OPENSHIFT_POSTGRESQL_DB_HOST']
app.config['POSTGRESQL_DB_PORT'] = os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']
app.config['DB_URL'] = 'postgresql://%s:%s/trackfinity' % (app.config['POSTGRESQL_DB_HOST'], app.config['POSTGRESQL_DB_PORT'])
app.config['BASE_URL'] = 'http://trackfinity-huideveloper.rhcloud.com/'
app.config['PROPAGATE_EXCEPTIONS'] = True


# setup db engine
engine = create_engine(app.config['DB_URL'])
connection = engine.connect()


from controller import *
from models.trackModel import deleteTrack


#@sched.scheduled_job('cron', day_of_week='sun-mon', hour=24)
# called everytime index is called
def check_playlists():
	qry_str = 'SELECT * FROM playlist'
	
	results = connection.execute(qry_str)
	
	if results:
		for row in results.fetchall():
			time_created = str(row['id'])		# id of playlist is the unix time stampe

			time_interval = int(time.time()) - int(time_created)
			minutes = int(time_interval/60)		# get minutes passed by since time of creation

			if minutes > 1440:					# if playlist exists for more than 24 hours, delete
				print('DELETING PLAYLIST ' + time_created)
				# delete playlist 
				qry_str = ("""DELETE FROM playlist WHERE id='%s'""" % (time_created))
				connection.execute(qry_str)

				# delete songs in the playlist
				qry_str = ("""SELECT * from tracks WHERE playlistid='%s'""" % (time_created))
				results = connection.execute(qry_str)

				for track in results.fetchall():
					deleteTrack(track['trackid'])
	else:
		raise Exception(sys.argv[0:]) 



@app.route("/")
def index():
	check_playlists()
	message = request.args.get('rt_message')
	if message is None:
		message = ''
	return render_template('user.html', rt_message=message)




# Shutdown your cron thread if the web process is stopped
# atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == "__main__":
    app.run()
