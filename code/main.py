import time
import os

import logging
import logging.config

import configparser

from flask import Flask
from flask import request
from flask import json
from flask import jsonify
from flask import abort
from functools import wraps

import autobell
import epalspeech
import epalaudio

from pprint import pprint

from werkzeug.utils import secure_filename

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.get('flask', 'upload_dir')


USER_DATA = {
    "admin": "12345678"
}

       
def verifyUser(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        result = None
        
        if (not 'Auth-Username' in request.headers) or (not 'Auth-Password' in request.headers):
           logging.debug('Missing auth fields from request headers')
           #return jsonify({'error': 'missing user auth fields'}), 400
           abort(400)
        
        username = request.headers.get('Auth-Username')        
        password = request.headers.get('Auth-Password')        
         
        if not verifyUser(username, password):
           #logging.debug('Access denied. Invalid username or password.')
           #return jsonify({'error': 'access denied - invalid username or password'}), 401
           abort(401)
        
        #logging.debug('Valid user auth with username [' + username + ']')

        return f(*args, **kwargs)
    return decorated_function        
    
    
    


@app.route("/", methods=['GET', 'POST'])
def status():

    data = {
        'status' : 'ok',
        'cmdSetTime': time.strftime("%m/%d/%Y %H:%M:%S"),
        'cmdSetBellAutoMode': autobell.getBellAutoMode(),
        'cmdSetPlayMusicAtBreakMode': autobell.getPlayMusicAtBreak()
    }
    
    return jsonify(data)


@app.route("/ping", methods=['POST'])
@login_required
def ping():

    data = {
        'status' : 'ok',
        'cmdSetTime': time.strftime("%m/%d/%Y %H:%M:%S"),
        'cmdSetBellAutoMode': autobell.getBellAutoMode(),        
        'cmdSetPlayMusicAtBreakMode': autobell.getPlayMusicAtBreak()
    }
    
    return jsonify(data)


    
@app.route("/bell/ringnow", methods=['POST'])
@login_required
def bellringnow():
    autobell.bellRingNow()
    
    data = {
        'status' : 'ok'
    }
    return jsonify(data)

    
@app.route("/radiostation/play/withid/<int:stationId>", methods=['POST'])
@login_required
def playWebRadio(stationId):

    if stationId == 1:
        epalaudio.addToPlayQueue(src='http://kissfm.live24.gr/kiss2111', volume=80)        
        epalaudio.playQueue()
    elif stationId == 2:
        epalaudio.addToPlayQueue(src='http://galaxy.live24.gr:80/galaxy9292', volume=80)
        epalaudio.playQueue()
    elif stationId == 3:
        epalaudio.addToPlayQueue(src='http://109.123.116.202:8020/stream', volume=80)
        epalaudio.playQueue()

    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/system/killall/mpg321", methods=['POST'])
@login_required
def stopAllAudio():
    epalaudio.stopAllAudio()
    
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)


    
@app.route("/bell/automode/on", methods=['POST'])
@login_required
def setBellAutoModeStatusOn():
    autobell.setBellAutoMode(True)
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/bell/automode/off", methods=['POST'])
@login_required
def setBellAutoModeStatusOff():
    autobell.setBellAutoMode(False)
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)


    
@app.route("/bell/playmusicatbreak/on", methods=['POST'])
@login_required
def setPlayMusicAtBreakOn():
    autobell.setPlayMusicAtBreak(True)
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/bell/playmusicatbreak/off", methods=['POST'])
@login_required
def setPlayMusicAtBreakOff():
    autobell.setPlayMusicAtBreak(False)
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/system/volume/set/up", methods=['POST'])
@login_required
def systemvolumesetup():
    epalaudio.stepIncreaseVolume()
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/system/volume/set/down", methods=['POST'])
@login_required
def systemvolumesetdown():
    epalaudio.stepDecreaseVolume()
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/audio/queue/clear", methods=['POST'])
@login_required
def audioqueueclear():
    epalaudio.audioQueueClear()
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)

    
@app.route("/audio/queue/playnext", methods=['POST'])
@login_required
def audioqueueplaynext():
    epalaudio.audioQueuePlayNext()
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)
 
    
@app.route("/speech/<string:language>/<string:textmsg>", methods=['GET'])
@login_required
def speechText(language, textmsg):

    filename = epalspeech.createAudioFileFromText(language, textmsg)
    
    epalaudio.addToPlayQueue(src=filename, volume=60)
    epalaudio.playQueue()

        
    data = {
        'status' : 'ok'
    }
    
    return jsonify(data)



@app.route("/saytime", methods=['POST'])
@login_required
def sayTime():

    language = 'el'
    textmsg = "Η ώρα είναι " + time.strftime("%I:%M")

    filename = epalspeech.createAudioFileFromText(language, textmsg)

    epalaudio.addToPlayQueue(src=filename, volume=100)
    epalaudio.playQueue()

    data = {
        'status' : 'ok'
    }

    return jsonify(data)



    
 
if __name__ == "__main__":
    logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True,})

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("devel.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.DEBUG)

    #logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("vlc").setLevel(logging.WARNING)
    
    epalaudio.startAudioThread()
	
    autobell.startAutoBellThread()
        
    cfgHttpdPort = config.getint('httpd', 'port')

    app.run(host='0.0.0.0', port=cfgHttpdPort, debug = False)

