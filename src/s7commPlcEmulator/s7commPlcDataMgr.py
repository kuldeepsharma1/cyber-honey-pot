#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        s7commPlcDataMgr.py 
#
# Purpose:     This module is the data management module to init the Modbus-TCP 
#              server, Plc internal registers, coils and the PLC ladder logic diagram.
#              It will handle the Modbus request from the honeypot PLC controller, 
#              read registers state (input), then calculate the ladder logic and 
#              set the plc coils(output) in its every clock cycle.
#  
# Author:      Yuancheng Liu
#
# Created:     2024/11/02
# version:     v0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import random
import threading

import s7commPlcGlobal as gv

import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

from s7LadderLogic import ladderLogic

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ Management module running parallel with the main thread to handle all the 
        PLC request and control functions.
    """
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)

        # Init the plc data handler and permission config

        # Init the s7comm server
        self.server = snap7Comm.s7commServer(snapLibPath=gv.gS7snapDllPath)
        # Init the data reading memory addresses
        self.server.initNewMemoryAddr(1, [0, 2, 4, 6], [BOOL_TYPE, BOOL_TYPE, BOOL_TYPE, BOOL_TYPE])
        self.server.initNewMemoryAddr(2, [0, 2, 4, 6], [BOOL_TYPE, BOOL_TYPE, BOOL_TYPE, BOOL_TYPE])
        # Init the data output memory addresses
        self.server.initNewMemoryAddr(3, [0, 2, 4, 6], [BOOL_TYPE, BOOL_TYPE, BOOL_TYPE, BOOL_TYPE])
        self.server.initNewMemoryAddr(4, [0, 2, 4, 6], [BOOL_TYPE, BOOL_TYPE, BOOL_TYPE, BOOL_TYPE])
        # Init the ladder logic 
        gv.iPlcLadderLogic = ladderLogic(self.server, gv.gLadderID)

        self.terminate = False
        gv.gDebugPrint("PLC data manager init finished.", logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function call by start(). """
        def handlerS7request(parmList):
            """ ladder logic simulation function: when the user set the address Idx=2
                and dataIdx = 4 value, the ladder logic will change the address Idx=2
                dataIdx = 0 's value to the same value.
            """
            gv.iPlcLadderLogic.runLadderLogic(inputData=parmList)
        gv.gDebugPrint('PLC S7Comm server started.', logType=gv.LOG_INFO)
        self.server.startService(eventHandlerFun=handlerS7request)
        gv.gDebugPrint('PLC S7Comm server terminated.', logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def getPlcStateDict(self):
        """ Return the PLC current input voltage, register value, coil value and 
            output voltage as a dictionary.
        """
        stateDict = {
            'inputVol':[],
            'registerVal':[],
            'coilVal':[],
            'outputVol':[]
        }
        for val in self.getAllRegistersVal():
            stateDict['registerVal'].append(val)
            voltage = round(5 + random.uniform(-0.05, 0.05),2) if val else 0 
            stateDict['inputVol'].append(voltage)
        for val in self.getAllCoilsVal():
            stateDict['coilVal'].append(val)
            voltage = 5 if val else 0
            stateDict['outputVol'].append(voltage)
        return stateDict