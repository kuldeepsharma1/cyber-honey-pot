#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        modbusPlcApp.py [python3]
#
# Purpose:     This module is the main execution file of the modbus-TCP PLC emulator
#              of the honeypot project. It provide the modbus-TCP interface for 
#              handling the OT control requesnt and a web interface for PLC 
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
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_required

import modbusPlcGlobal as gv
import plcServerAuth
import plcDataMgr

#-----------------------------------------------------------------------------
# Init the flask web app program.
def createApp():
    """ Create the flask App."""
    # init the web host
    app = Flask(__name__)
    app.config['SECRET_KEY'] = gv.APP_SEC_KEY
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=gv.COOKIE_TIME)
    from plcServerAuth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    # Create the user login manager
    loginMgr = LoginManager()
    loginMgr.loginview = 'auth.login'
    loginMgr.init_app(app)
    @loginMgr.user_loader
    def loadUser(userID):
        return plcServerAuth.User(userID)
    return app

# Init the PLC function thread.
gv.iPlcDataMgr = plcDataMgr.DataManager(None)
gv.iPlcDataMgr.start()
# Init the Web UI thread.
app = createApp()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# web request handling functions.
@app.route('/')
@app.route('/index')
def index():
    """ route to introduction index page."""
    posts = {'page':
             0}  # page index is used to highlight the left page slide bar.
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/userlogin/<string:username>/<string:password>')
def userlogin(username, password):
    """ Add CGI for participants to brute force break the login credential."""
    username = str(username)
    password = str(password)
    if username == gv.gUser and password == gv.gPassword:
        return "You got correct credential!"
    return "User name or password incorrect!"
    
#-----------------------------------------------------------------------------
@app.route('/ladderlogic')
@login_required
def ladderlogic():
    """ route to the ladder logic page."""
    posts = {
                'page': 1,
                'flag': str(gv.gFlagStr)
            }
    return render_template('ladderlogic.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/configuration')
@login_required
def configuration():
    """ route to the configuration page."""
    posts = {
                'defaultRip': gv.ALLOW_R_L,
                'defaultWip': gv.ALLOW_W_L,
                'currentRip': gv.iPlcDataMgr.getAllowRipList(),
                'currentWip': gv.iPlcDataMgr.getAllowWipList(),
                'page': 2
            }
    return render_template('configuration.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/resetAllowReadIp', methods = ['POST', 'GET'])
@login_required
def resetAllowReadIp():
    """"Rest all allow read IPs to config file setting from the web UI"""
    rst = gv.iPlcDataMgr.resetAllowRipList()
    if rst:
        flash("Rest the allow read IP list success!")
    else: 
        flash("Rest the allow read IP list failed!")
    return redirect(url_for('configuration'))

#-----------------------------------------------------------------------------
@app.route('/addAllowReadIp', methods = ['POST', 'GET'])
@login_required
def addAllowReadIp():
    """Add one allow read IP from the web UI"""
    if request.method == 'POST':
        ipstr = str(request.form['newIp'])
        rst = gv.iPlcDataMgr.addAllowReadIp(ipstr)
        if rst:
            flash("New ip %s is added in the all read ip address list" %str(ipstr))
        else: 
            flash("Input IP format incorrect.")
    return redirect(url_for('configuration'))

#-----------------------------------------------------------------------------
@app.route('/resetAllowWriteIp', methods = ['POST', 'GET'])
@login_required
def resetAllowWriteIp():
    """"Rest all allow write IPs to config file setting from the web UI"""
    rst = gv.iPlcDataMgr.resetAllowWipList()
    if rst:
        flash("Rest the allow write IP list success!")
    else: 
        flash("Rest the allow write IP list failed!")
    return redirect(url_for('configuration'))

#-----------------------------------------------------------------------------
@app.route('/addAllowWriteIp', methods = ['POST', 'GET'])
@login_required
def addAllowWriteIp():
    """Add one allow write IP from the web UI"""
    if request.method == 'POST':
        ipstr = str(request.form['newIp'])
        rst = gv.iPlcDataMgr.addAllowWriteIp(ipstr)
        if rst:
            flash("New ip %s is added in the all write ip address list" %str(ipstr))
        else: 
            flash("Input IP format incorrect.")
    return redirect(url_for('configuration'))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
    app.run(host=gv.gflaskHost,
        port=gv.gflaskPort,
        debug=gv.gflaskDebug,
        threaded=gv.gflaskMultiTH)
