#!/usr/bin/env python

import re
import json
import gzip
import subprocess
import os, sys

from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file
from GraphStories import GraphStories

from os.path import dirname, abspath
from flask import render_template, redirect

app = Flask(__name__)

globalConfig = {}
globalHist = 0
globalDebugFlag = False

if( globalDebugFlag ):
	globalPrefix = '/data/anwala/IMLS/StoryGraph/'
else:
	globalPrefix = '/data/'

#copied from genericCommon.py - start
def getConfigParameters(configPathFilename, keyValue=''):

	keyValue = keyValue.strip()
	configPathFilename = configPathFilename.strip()
	if( len(configPathFilename) == 0 ):
		return ''

	returnValue = ''

	try:
		configFile = open(configPathFilename, 'r')
		config = configFile.read()
		configFile.close()

		jsonFile = json.loads(config)

		if( len(keyValue) == 0 ):
			returnValue = jsonFile
		else:
			returnValue = jsonFile[keyValue]
	except:
		print('\tFile open error:', configPathFilename)

	return returnValue

def getTextFromGZ(path):
	try:
		infile = gzip.open(path, 'rb')
		txt = infile.read()
		infile.close()

		return txt
	except:
		genericErrorInfo()

	return ''
#copied from genericCommon.py - end

def getDictFromGZPath(path):
	try:
		return json.loads(getTextFromGZ(path))
	except:
		print('\tFile open error:', path)
		return {}

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/stats/', methods=['GET'])
def statsIndex():
	return render_template('stats/index.html')

@app.route('/studies/', methods=['GET'])
def studiesIndex():
	return render_template('studies/index.html')

	

@app.route('/graphs/<storygraph>/', methods=['GET'])
def storyGraph(storygraph):
	return render_template('story-graph.html')

@app.route('/graphs/dev/<storygraph>/', methods=['GET'])
def storyGraphDev(storygraph):
	return render_template('story-graph-dev.html')
'''
@app.route('/stats/<parentFolder>/<childFolder>/', methods=['GET'])
def storyGraphStats(parentFolder, childFolder):
	return render_template('stats/' + parentFolder + '/' + childFolder + '/' + 'index.html')
'''

@app.route('/stats/<parentFolder>/<childFolder>/', methods=['GET'])
def storyGraphStats(parentFolder, childFolder):
	return redirect('studies/' + parentFolder + '/' + childFolder + '/', code=301)

@app.route('/studies/<date>/<study>/', methods=['GET'])
def genericStudiesRoute(date, study):
	return render_template('studies/' + date + '/' + study + '/index.html')

@app.route('/graphs/ops/sim/', methods=['POST'])
def graphsOpsSim():
	
	userQuery = request.get_json(silent=True)

	if( 'A' in userQuery and 'B' in userQuery ):

		dist, det = GraphStories.calculateSingleDistance(
			clusterA=userQuery['A'], 
			clusterB=userQuery['B'], 
			extractionKey='entity', 
			simDict=globalConfig['graph-parameters']['graph-building-thresholds']
		)
		
		return jsonify({'dist': dist})
	return jsonify({'dist': 1})



@app.route('/unlisted/', methods=['GET'])
def unlistedIndex():
	return render_template('media-manip/index.html')

@app.errorhandler(404)
def pageNotFound(e):
	return render_template('404.html'), 404

@app.route('/tweet-studies/users/', methods=['GET'])
def tweetStudyUsers():
	return render_template( 'media-manip/tweet-study-users.html' )

@app.route('/tweet-studies/users-stories/', methods=['GET'])
def tweetStudyUsersStories():
	return render_template( 'media-manip/tweet-study-users-stories.html' )

@app.route('/tweet-studies/hashtag-sim/', methods=['GET'])
def tweetStudyHashtagSim():
	return render_template( 'media-manip/tweet-study-hashtag-sim.html' )

@app.route('/tweet-studies/tweet-sim/', methods=['GET'])
def tweetStudyTweetSim():
	return render_template( 'media-manip/tweet-study-tweet-sim.html' )

@app.route('/tweet-studies/tweet-ira/', methods=['GET'])
def tweetStudyTweetTrolls():
	return render_template( 'media-manip/tweet-study-ira.html' )


@app.route('/graphs/<storygraph>/<YYYY>/<MM>/<DD>/<graph>', methods=['GET'])
def storyGraphGetGraph(storygraph, YYYY, MM, DD, graph):
	#http://localhost:11111/graphs/polar-media-consensus-graph/2018/03/05/graph99.json

	#handle generic/non-generic requests - start
	if( YYYY == '0' ):
		YYYY = ''
	else:
		YYYY = YYYY + '/'

	if( MM == '0' ):
		MM = ''
	else:
		MM = MM + '/'

	if( DD == '0' ):
		DD = ''
	else:
		DD = DD + '/'
	#handle generic/non-generic requests - end


	filename = globalPrefix + 'graphs/' + storygraph + '/' + YYYY + MM + DD + graph
	graphFlag = False
	if( graph.lower().find('graph') != -1 ):
		#graphs are compressed
		filename = filename + '.gz'
		graphFlag = True
		
	if( os.path.exists(filename) == False ):
		return jsonify( {} )

	if( graphFlag ):
		f = getDictFromGZPath( filename )
	else:
		f = getConfigParameters( filename )

	if( graph.lower().find('menu') != -1 ):
		#menu file requires special packaging
		f = {'menu': f, 'self': request.url}
	else:
		f['self'] = request.url

	return jsonify( f )
	#return send_file(filename, mimetype='application/json')

@app.route('/files/<filetype>/<storygraph>/<filename>/', methods=['GET'])
def storyGraphFiles(filetype, storygraph, filename):

	f = {}
	
	filetype = filetype.strip()
	storygraph = storygraph.strip()
	filename = filename.strip()

	if( filetype == 'config' ):
		config = globalPrefix + 'generic/config-versions/' + filename + '.json'
		print('try:', config)
		if( os.path.exists(config) ):
			f = getConfigParameters( config )

	return jsonify( f )

@app.route('/graphs/pointers/<storygraph>/', methods=['GET'])
def storyGraphDetails(storygraph):

	graphIndexDetails = getConfigParameters( globalPrefix + 'graph-cursors/' + storygraph + '/' + 'graphIndex.json' )	
	
	if( 'cursor' in graphIndexDetails ):
		cursor = graphIndexDetails['cursor']
		path = graphIndexDetails['cur-path']
	else:
		cursor = 0
		path = ''
		graphIndexDetails = {}

	graphIndexDetails['hist'] = globalHist
	return jsonify( graphIndexDetails )

@app.after_request
def add_header(response):

	contentType = response.headers['Content-Type'].lower()
	response.headers['X-Self'] = request.url

	if( contentType.find('json') != -1 ):
		
		#if( request.url.endswith('.json.gz') ):
		#	response.headers['Content-Encoding'] = 'gzip'		

		response.cache_control.max_age = 0

	if( contentType.find('javascript') != -1 ):
		response.cache_control.max_age = 0


	return response

def workingFolder():
	return dirname(abspath(__file__)) + '/'

if __name__ == '__main__':
	
	globalConfig = getConfigParameters( globalPrefix + 'generic/serviceClusterStories.config.json', 'default-config' )
	globalHist = globalConfig['history-count']
	app.run(host='0.0.0.0', threaded=True, debug=globalDebugFlag)
