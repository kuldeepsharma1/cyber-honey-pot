#-----------------------------------------------------------------------------
# Name:        s7commPlcGlobal.py
#
# Purpose:     This module is used as a project global config file to set the 
#              constants, parameters and instances which will be used in the 
#              other modules in the project.
#              
# Author:      Yuancheng Liu
#
# Created:     2024/10/21
# Version:     v_0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
"""
For good coding practice, follow the below naming convention:
    1) Global variables should be defined with initial character 'g'.
    2) Global instances should be defined with initial character 'i'.
    3) Global CONSTANTS should be defined with UPPER_CASE letters.
"""

import os
import sys
import platform

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : %s" % dirpath)
APP_NAME = ('s7commPlc', 'emulator')

TOPDIR = 'src'
LIBDIR = 'lib'

#-----------------------------------------------------------------------------
# find the lib folder for importing the library modules
idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

#-----------------------------------------------------------------------------
# load the config file.
import ConfigLoader
CONFIG_FILE_NAME = 'config.txt'
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

#-----------------------------------------------------------------------------
# Init the logger
import Log
Log.initLogger(gTopDir, 'Logs', APP_NAME[0], APP_NAME[1], 
               historyCnt=100, fPutLogsUnderDate=True)

# Set the S7comm dll lib
gS7snapDllPath = os.path.join(dirpath, 'snap7.dll') if platform.system() == 'Windows' else None 

# Init the log type parameters.
DEBUG_FLG   = False
LOG_INFO    = 0
LOG_WARN    = 1
LOG_ERR     = 2
LOG_EXCEPT  = 3

def gDebugPrint(msg, prt=True, logType=None):
    if prt: print(msg)
    if logType == LOG_WARN:
        Log.warning(msg)
    elif logType == LOG_ERR:
        Log.error(msg)
    elif logType == LOG_EXCEPT:
        Log.exception(msg)
    elif logType == LOG_INFO or DEBUG_FLG:
        Log.info(msg)

APP_SEC_KEY = 'secrete-key-goes-here'
UPDATE_PERIODIC = 15
COOKIE_TIME = 30

#-----------------------------------------------------------------------------
# Init the global value

# Modbus server config 
gPlcHostIp = '0.0.0.0'
gHostPort = 502
gLadderID = CONFIG_DICT['LADDER_ID']

# Own Information
gOwnID = CONFIG_DICT['Own_ID']
gOwnIP = CONFIG_DICT['Own_IP']
gProType = CONFIG_DICT['PRO_TYPE']

# Honeypot monitor server config
gMonHubIp = CONFIG_DICT['MON_IP']
gMonHubPort = int(CONFIG_DICT['MON_PORT'])
gReportInv = int(CONFIG_DICT['RPT_INTERVAL'])

# PLC user credential:
gUsersRcd = os.path.join(dirpath, CONFIG_DICT['USERS_RCD'])

# Flask App parameters : 
gflaskHost = '0.0.0.0'
gflaskPort = int(CONFIG_DICT['FLASK_SER_PORT']) if 'FLASK_SER_PORT' in CONFIG_DICT.keys() else 5000
gflaskDebug = CONFIG_DICT['FLASK_DEBUG_MD']
gflaskMultiTH =  CONFIG_DICT['FLASK_MULTI_TH']

#-----------------------------------------------------------------------------
# Init the global instances
iPlcLadderLogic = None
iPlcDataMgr = None
iUserMgr = None
iMonitorClient = None