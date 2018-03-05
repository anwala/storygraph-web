#!/usr/bin/env python

import re
import json
import subprocess
import os, sys

from flask import Flask
from flask import jsonify
from flask import request
from GraphStories import GraphStories

from os.path import dirname, abspath
from flask import render_template, redirect, url_for

app = Flask(__name__)

globalConfig = {}
globalHist = 0

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
		print('\tFile open error.')

	return returnValue
#copied from genericCommon.py - end

@app.route('/unlisted/', methods=['GET'])
def index():
	return render_template('index.html')

@app.errorhandler(404)
def pageNotFound(e):
	return render_template('404.html'), 404



@app.route('/graphs/<storygraph>/', methods=['GET'])
def storyGraph(storygraph):
	return render_template('story-graph.html')

@app.route('/graphs/dev/<storygraph>/', methods=['GET'])
def storyGraphDev(storygraph):
	return render_template('story-graph-dev.html')

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



@app.route('/tweet-studies/users/', methods=['GET'])
def tweetStudyUsers():
	return render_template( 'tweet-study-users.html' )

@app.route('/tweet-studies/users-stories/', methods=['GET'])
def tweetStudyUsersStories():
	return render_template( 'tweet-study-users-stories.html' )

@app.route('/tweet-studies/hashtag-sim/', methods=['GET'])
def tweetStudyHashtagSim():
	return render_template( 'tweet-study-hashtag-sim.html' )

@app.route('/tweet-studies/tweet-sim/', methods=['GET'])
def tweetStudyTweetSim():
	return render_template( 'tweet-study-tweet-sim.html' )



@app.route('/graphs/pointers/<storygraph>/', methods=['GET'])
def storyGraphDetails(storygraph):

	graphIndexDetails = getConfigParameters( workingFolder() + 'graphs/' + storygraph + '/' + 'graphIndex.json' )	
	
	if( 'cursor' in graphIndexDetails ):
		cursor = graphIndexDetails['cursor']
		path = graphIndexDetails['cur-path']
	else:
		cursor = 0
		path = ''

	graphIndexDetails['hist'] = globalHist
	return jsonify( graphIndexDetails )

@app.after_request
def add_header(response):

	contentType = response.headers['Content-Type'].lower()
	#response.headers['X-Debug'] = request.url

	if( contentType.find('json') != -1 ):
		
		if( request.url.endswith('.json.gz') ):
			response.headers['Content-Encoding'] = 'gzip'		

		response.cache_control.max_age = 0

	if( contentType.find('javascript') != -1 ):
		response.cache_control.max_age = 0


	return response

def workingFolder():
	return dirname(abspath(__file__)) + '/'

if __name__ == '__main__':
	
	'''
	#run on a local machine
	proc = ''
	try:
		proc = subprocess.Popen('./serviceClusterStories.py')
	except:
		proc.kill()
		genericErrorInfo()
	'''


	globalConfig = getConfigParameters( workingFolder() + 'generic/serviceClusterStories.config.json', 'default-config' )
	globalHist = globalConfig['history-count']
	app.run(host='0.0.0.0', threaded=True)