#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        modbusPlcApp.py [python3]
#
# Purpose:     This module is the main App execution file of the modbus-TCP PLC 
#              emulator of the honeypot project. It provide the modbus-TCP interface 
#              for handling the OT control request and a web interface for PLC 
#              configuration change.
#
# Author:      Yuancheng Liu
#
# Created:     2024/10/21
# version:     v0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

from datetime import timedelta 
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request

import monitorGlobal as gv
import monitorDataMgr as dataMgr

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Init the flask web app program.
def createApp():
    """ Create the flask App and init the app config parameters."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = gv.APP_SEC_KEY
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=gv.COOKIE_TIME)
    return app

gv.iDataMgr = dataMgr.DataManger()
app = createApp()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# web request handling functions.
@app.route('/')
@app.route('/index')
def index():
    """ route to introduction index page."""
    posts = {'page': 0}  # page index is used to highlight the left page slide bar.
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/controllerview')
def controllerview():
    """ route to the ladder logic page."""
    posts = {'page': 1}
    return render_template('controllerview.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/plcemuview')
def plcemuview():
    """ route to the ladder logic page."""
    posts = {'page': 2}
    return render_template('plcemuview.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/dataPost/<string:devID>', methods=('POST',))
def dataPost(devID):
    """ Handle program data submittion request.
        API call example:
        requests.post(http://%s:%s/dataPost/<devID>, json={})
    """
    content = request.json
    gv.gDebugPrint("Get raw data from %s " %str(devID), logType=gv.LOG_INFO)
    gv.gDebugPrint("Raw Data: %s" % str(content),prt=True, logType=gv.LOG_INFO)
    result = gv.iDataMgr.handleRequest(content) if gv.iDataMgr else {"ok": True}
    return jsonify(result)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
    app.run(host=gv.gflaskHost,
        port=gv.gflaskPort,
        debug=gv.gflaskDebug,
        threaded=gv.gflaskMultiTH)
