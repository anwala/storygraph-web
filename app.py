#!/usr/bin/env python

import gzip
import json
import os, sys
import re
import subprocess

from datetime import datetime, timedelta
from flask import Flask
from flask import jsonify
from flask import render_template, redirect
from flask import request
from flask import send_file
from GraphStories import GraphStories
from os.path import dirname, abspath

app = Flask(__name__)

globalConfig = {}
globalHist = 0
globalDebugFlag = False

if( globalDebugFlag ):
	globalPrefix = '/data/anwala/IMLS/StoryGraph/'
else:
	globalPrefix = '/data/'

#copied from genericCommon.py - start
def getDictFromJson(jsonStr):

	try:
		return json.loads(jsonStr)
	except:
		genericErrorInfo()

	return {}

def genericErrorInfo(slug=''):
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	
	errMsg = fname + ', ' + str(exc_tb.tb_lineno)  + ', ' + str(sys.exc_info())
	print(errMsg + slug)

	return errMsg

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
	return redirect('/studies/' + parentFolder + '/' + childFolder + '/', code=301)

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

	menu = {'menu': []}
	singleGraph = {}

	yyyyMMDD = f'{YYYY}/{MM}/{DD}'
	graphPath = f'{globalPrefix}graphs/{storygraph}/{YYYY}/{MM}/{DD}/graphs-{YYYY}-{MM}-{DD}.jsonl.gz'
	cursor = graph.replace('graph', '').replace('.json', '')
	cursor = int(cursor) if cursor.isnumeric() else -1

	if( os.path.exists(graphPath) ):
		try:
			
			with gzip.open(graphPath, 'rb') as f:
				counter = 0
				for graph in f:
					
					singleGraph = getDictFromJson(graph)
					if( cursor == counter ):
						break
					
					counter += 1
					if( 'timestamp' in singleGraph ):
						menu['menu'].append(singleGraph['timestamp'])

			singleGraph['self'] = request.url
			menu['self'] = request.url
		except:
			genericErrorInfo()

	return jsonify(menu) if cursor == -1 else jsonify(singleGraph)

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
	
	nowDate = datetime.utcnow()
	graphIndexDetails = {}

	for i in range(4000):

		yyyyMMDD = nowDate.strftime('%Y/%m/%d')
		graphPath = '{}graphs/{}/{}/graphs-{}.jsonl.gz'.format( globalPrefix, storygraph, yyyyMMDD, yyyyMMDD.replace('/', '-') )
		
		if( os.path.exists(graphPath) ):

			graphIndexDetails = {'cur-path': yyyyMMDD, 'cursor': -1, 'refresh-seconds': 300}
			try:
				with gzip.open(graphPath, 'rb') as f:
					for graph in f:
						graphIndexDetails['cursor'] += 1
			except:
				genericErrorInfo()

			break
		else:
			nowDate = nowDate + timedelta(days=-1)
	
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
