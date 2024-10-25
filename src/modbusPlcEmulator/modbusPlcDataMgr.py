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

import time
import threading

import modbusPlcGlobal as gv
import modbusTcpCom

#-----------------------------------------------------------------------------
class testLadderLogic(modbusTcpCom.ladderLogic):
    """ A test ladder logic program with 8 holding register and 2 level ladder
        logic to set the output coils.
    """
    def __init__(self, parent) -> None:
        super().__init__(parent)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 8
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 4

    def runLadderLogic(self, regsList, coilList=None):
        # coils will be set ast the reverse state of the input registers' state. 
        result = []
        if len(regsList) != 8: return None
        #run lvl1 logic
        r_1_1 = regsList[0] and regsList[2]
        r_1_2 = regsList[1] or regsList[3]
        r_1_3 = regsList[4] or regsList[5]
        r_1_4 = regsList[6] and regsList[7]
        # run lvl2 logic
        c_2_1 = not r_1_4
        c_2_2 = not r_1_2
        c_2_3 = r_1_1 and r_1_3
        c_2_4 = r_1_2 or r_1_4
        result = [c_2_1, c_2_2, c_2_3, c_2_4]
        return result

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ Management module running parallel with the main thread to handle all the 
        PLC functions.
    """
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        # Init the ladder logic 
        self.ladder = testLadderLogic(None)
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

    #-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function call by start(). """
        time.sleep(1)  # sleep 1 second to wait socketIO start to run.
        while not self.terminate:
            gv.gDebugPrint('PLC Modbus-TCP server started', logType=gv.LOG_INFO)
            self.server.startServer()
            time.sleep(gv.UPDATE_PERIODIC)

        gv.gDebugPrint('PLC Modbus-TCP server terminated', logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def resetAllowRipList(self):
        return self.dataMgr.setAllowReadIpaddresses(list(gv.ALLOW_R_L).copy())

    def resetAllowWipList(self):
        return self.dataMgr.setAllowWriteIpaddresses(list(gv.ALLOW_W_L).copy())
