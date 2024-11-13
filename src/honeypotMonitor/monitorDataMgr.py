#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        monitorDataMgr.py [python3]
#
# Purpose:     This module is the data management module of the monitor hub.
#  
# Author:      Yuancheng Liu
#
# Created:     2024/11/03
# version:     v0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import time
import monitorGlobal as gv
# Record number keep by the agent. 
RCD_NUM = 10

RPT_NORMAL = 'normal'
RPT_WARN = 'warning'
RPT_ALERT = 'alert'
RPT_LOGIN = 'login'

PLC_TYPE='plc'
CTRL_TYPE='controller'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class agentDev(object):
    """ Agent class for the monitor hub. """
    def __init__(self, id, ipaddress, protocol, rcdLimit=RCD_NUM):
        self.id = id
        self.ipaddress = ipaddress
        self.protocol = protocol
        self.reportList = []
        self.exceptList = []
        self.rcdLimit = rcdLimit
        self.loginTime = time.time()
        self.lastUpdateTime = self.loginTime
        self.online = True
        self.totalExpCount = 0
        self.totalRptCount = 0

    def getID(self):
        return self.id
    
    def setIP(self, newIp):
        self.ipaddress = newIp
    
    def setProtocol(self, newProtocol):
        self.protocol = newProtocol

    def addOneReport(self, reportDict):
        self.lastUpdateTime = time.time()
        self.totalRptCount += 1
        if len(self.reportList) > self.rcdLimit: self.reportList.pop(0)
        self.reportList.append(reportDict)
        if reportDict['type'] == RPT_ALERT or reportDict['type']==RPT_WARN:
            self.addExcept(reportDict)

    def addExcept(self, exceptDict):
        if len(self.exceptList) > self.rcdLimit: self.exceptList.pop(0)
        self.totalExpCount += 1
        self.exceptList.append(exceptDict)

    def updateOnlineState(self):
        self.online = time.time() - self.lastUpdateTime < gv.gTimeOut

    def getAgentState(self):
        self.updateOnlineState()
        dataDict = {'id':self.id, 
                    'ip':self.ipaddress, 
                    'protocol':self.protocol,
                    'lastUpdateT': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.lastUpdateTime)),
                    'reportT': (self.lastUpdateTime - self.loginTime)//60,
                    'online':self.online, 
                    'exceptCount': self.totalExpCount,
                    'totalRptCount':self.totalRptCount
                    }
        return dataDict

    def getRecordList(self):
        return self.reportList
    
    def getExecptList(self):
        return self.exceptList

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class agentPLC(agentDev):
    """ Agent PLC class for the monitor hub. """   

    def __init__(self, id, ipaddress, protocol, ladderInfo=None):
        super().__init__(id, ipaddress, protocol)
        self.ladderInfo = ladderInfo

    def setLadderInfo(self, ladderInfo):
        self.ladderInfo = ladderInfo

    def getPLCState(self):
        dataDict = self.getAgentState()
        dataDict['ladderInfo'] = self.ladderInfo
        return dataDict

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class agentController(agentDev):

    """ Agent controller class for the monitor hub. """

    def __init__(self, id, ipaddress, protocol, plcID, plcIP):
        super().__init__(id, ipaddress, protocol)
        self.tgtPlcID = plcID
        self.tgtPlcIP = plcIP

    def setTargetPLCInfo(self, plcID, plcIP):
        self.tgtPlcID = plcID
        self.tgtPlcIP = plcIP

    def getControllerState(self):
        dataDict = self.getAgentState()
        dataDict['TargetID'] = self.tgtPlcID
        dataDict['TargetIP'] = self.tgtPlcIP
        return dataDict

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManger(object):

    """ Data manager class for the monitor hub. """
    def __init__(self):
        self.plcDict = {}
        self.controllerDict = {}
    
    def handleRequest(self, requestDict):
        reqDict = dict(requestDict)
        action = str(reqDict['Action']).lower()
        data = reqDict['Data']
        if action == RPT_LOGIN:
            if str(data['Type']).lower() == PLC_TYPE:
                self.addPlc(data['ID'], data['IP'], data['Protocol'], ladderInfo=data['LadderID'])
                gv.gDebugPrint("PLC Emulator: %s login." % data['ID'], logType=gv.LOG_INFO)
            elif str(data['Type']).lower() == 'controller':
                self.addController(data['ID'], data['IP'], data['Protocol'], data['TargetID'], data['TargetIP'])
                gv.gDebugPrint("PLC Controller: %s login." % data['ID'], logType=gv.LOG_INFO)
        elif action == RPT_NORMAL or action == RPT_WARN or action == RPT_ALERT:
            if reqDict['ID'] in self.plcDict.keys(): 
                self.plcDict[reqDict['ID']].addOneReport(data)
            elif reqDict['ID'] in self.controllerDict.keys(): 
                self.controllerDict[reqDict['ID']].addOneReport(data)
            else:
                gv.gDebugPrint("ID: %s not login before.", logType=gv.LOG_WARN)
        return {"ok": True}

    def addPlc(self, plcID, plcIP, protocol, ladderInfo=None):
        if plcID not in self.plcDict.keys():
            self.plcDict[plcID] = agentPLC(plcID, plcIP, protocol, ladderInfo=ladderInfo)
        else:
            self.plcDict[plcID].setIP(plcIP)
            self.plcDict[plcID].setProtocol(protocol)
            self.plcDict[plcID].setLadderInfo(ladderInfo)
    
    def getPlcState(self, plcID):
        if plcID in self.plcDict.keys():
            return self.plcDict[plcID].getPLCState()
        else:
            return None

    def getPlcReport(self, plcID):
        if plcID in self.plcDict.keys():
            result = {
                'report': self.plcDict[plcID].getRecordList(), 
                'alert': self.plcDict[plcID].getExecptList()
            }
            return result
        else:
            return None

    def getAllPlcState(self):
        return [self.plcDict[plcID].getPLCState() for plcID in self.plcDict.keys()]
    
    def addController(self, controllerID, controllerIP, protocol, plcID, plcIP):
        if controllerID not in self.controllerDict.keys():
            self.controllerDict[controllerID] = agentController(controllerID, controllerIP, protocol, plcID, plcIP)
        else:
            self.controllerDict[controllerID].setIP(controllerIP)
            self.controllerDict[controllerID].setProtocol(protocol)
            self.controllerDict[controllerID].setTargetPLCInfo(plcID, plcIP)

    def getControllerState(self, controllerID):
        if controllerID in self.controllerDict.keys():
            return self.controllerDict[controllerID].getControllerState()
        else:
            return None
        
    def getAllControllerState(self):
        return [self.controllerDict[controllerID].getControllerState() for controllerID in self.controllerDict.keys()]
    
    def getControllerReport(self, controllerID):
        if controllerID in self.controllerDict.keys():
            result = {
                'report': self.controllerDict[controllerID].getRecordList(), 
                'alert': self.controllerDict[controllerID].getExecptList()
            }
            return result
        else:
            return None
