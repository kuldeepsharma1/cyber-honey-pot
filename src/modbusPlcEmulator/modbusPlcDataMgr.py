#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcDataMgr.py [python3]
#
# Purpose:     This module is the data management module to init the Modbus-TCP 
#              server, Plc internal registers, coils and the PLC ladder logic diagram.
#              Then read registers state (input), calculate the ladder logic and 
#              set the plc coils(output).
#  
# Author:      Yuancheng Liu
#
# Created:     2024/06/02
# version:     v0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import random
import threading

import modbusPlcGlobal as gv
import modbusTcpCom
from mbLadderLogic import ladderLogic

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ Management module running parallel with the main thread to handle all the 
        PLC functions.
    """
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        # Init the ladder logic 
        self.ladder = ladderLogic(None)
        # Init the plc data handler and permission config
        self.dataMgr = modbusTcpCom.plcDataHandler(allowRipList=list(gv.ALLOW_R_L).copy(), 
                                              allowWipList=list(gv.ALLOW_W_L).copy())
        # Init the modbus server
        self.server = modbusTcpCom.modbusTcpServer(hostIp=gv.gPlcHostIp, 
                                                 hostPort=gv.gHostPort, 
                                                 dataHandler=self.dataMgr)
        serverInfo = self.server.getServerInfo()
        self.dataMgr.initServerInfo(serverInfo)
        self.dataMgr.addLadderLogic('testLogic', self.ladder)
        self.dataMgr.setAutoUpdate(True)
        self.terminate = False
        gv.gDebugPrint("PLC data manager init", logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def addAllowReadIp(self, ipaddress):
        return self.dataMgr.addAllowReadIp(str(ipaddress))

    def addAllowWriteIp(self, ipaddress):
        return self.dataMgr.addAllowWriteIp(str(ipaddress))

    #-----------------------------------------------------------------------------
    def getAllowRipList(self):
        return self.dataMgr.getAllowReadIpaddresses()

    def getAllowWipList(self):
        return self.dataMgr.getAllowWriteIpaddresses()

    def getAllRegistersVal(self):
        return self.dataMgr.getHoldingRegState(0, 8)

    def getAllCoilsVal(self):
        return self.dataMgr.getCoilState(0, 8)

    #-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function call by start(). """
        gv.gDebugPrint('PLC Modbus-TCP server started', logType=gv.LOG_INFO)
        self.server.startServer()
        gv.gDebugPrint('PLC Modbus-TCP server terminated', logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def resetAllowRipList(self):
        return self.dataMgr.setAllowReadIpaddresses(list(gv.ALLOW_R_L).copy())

    def resetAllowWipList(self):
        return self.dataMgr.setAllowWriteIpaddresses(list(gv.ALLOW_W_L).copy())

    def getPlcStateDict(self):
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

