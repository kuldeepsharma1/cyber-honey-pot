#-----------------------------------------------------------------------------
# Name:        mbPlcControllerApp.py
#
# Purpose:     This module is the controller program start a Modbus-TCP PLC 
#              client to connect to the PLC to set the holding register and 
#              read the coil status. It also provide a UDP service for people 
#              to read the PLC state.
#              
# Author:      Yuancheng Liu
#
# Created:     2024/10/28
# Version:     v_0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License      
#-----------------------------------------------------------------------------

import time
import threading
from random import randint

import s7commPlcControllerGlobal as gv
import snap7Comm
from snap7Comm import BOOL_TYPE

import monitorClient
from s7LadderLogic import ladderLogic

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class plcControllerApp(object):
    """ PLC controller main program. It will generate the PLC control request 
        randomly then check the plc execution result.
    """
    def __init__(self) -> None:

        gv.iMonitorClient = monitorClient.monitorClient(gv.gMonHubIp, gv.gMonHubPort, 
                                                reportInterval=gv.gReportInv)

        gv.iMonitorClient.setParentInfo(gv.gOwnID, gv.gOwnIP, monitorClient.CTRL_TYPE, gv.gProType, 
                                        tgtID=gv.gPlcID, tgtIP=gv.gPlcIP, ladderID=gv.gLadderID)


        self.s7commClient = snap7Comm.s7CommClient(gv.gPlcIP, rtuPort=gv.gPlcPort, snapLibPath=gv.gS7snapDllPath)
        self.ladderLogic = ladderLogic(None, gv.gLadderID)
        self.terminate = False

        gv.iMonitorClient.logintoMonitor()
        gv.iMonitorClient.start()

    #-----------------------------------------------------------------------------
    def startClient(self):
        """ Start the PLC client loop to send the holding register and get the coil 
            states, then compare with the local calculated result. If match, means 
            PLC works normally, else means PLC has some problem or under attack.
        """
        gv.gDebugPrint("PLC controller started", logType=gv.LOG_INFO)

        while not self.terminate:
            time.sleep(gv.gPlcConnInt)
            gv.gDebugPrint("Start to set the registers.", logType=gv.LOG_INFO)
            # generate random register input
            randomVals = [randint(0, 1) for i in range(8)]
            regVals = [i == 1 for i in randomVals]
            gv.gDebugPrint("Random generate input: %s" %str(regVals), logType=gv.LOG_INFO)
            result = self.ladderLogic.runVerifyLadderLogic(regVals)
            resultExp = [i == 1 for i in result]
            gv.gDebugPrint("Calculated output: %s" %str(resultExp), logType=gv.LOG_INFO)
            self.s7commClient.setAddressVal(1, 0, regVals[0], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(1, 2, regVals[1], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(1, 4, regVals[2], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(1, 6, regVals[3], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(2, 0, regVals[4], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(2, 2, regVals[5], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(2, 4, regVals[6], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            self.s7commClient.setAddressVal(2, 6, regVals[7], dataType=snap7Comm.BOOL_TYPE)
            time.sleep(0.1)
            time.sleep(1)

            val1 = self.s7commClient.readAddressVal(3, dataIdxList=(0,2,4,6), 
                                                    dataTypeList=(BOOL_TYPE, BOOL_TYPE, BOOL_TYPE, BOOL_TYPE))
            val2 = self.s7commClient.readAddressVal(4, dataIdxList=(0,2,4,6), 
                                                    dataTypeList=(BOOL_TYPE, BOOL_TYPE, BOOL_TYPE, BOOL_TYPE))
            # set connection state
            connectionRst = False if val1 is None or val2 is None else True
            if not connectionRst:
                gv.iMonitorClient.addReportDict(monitorClient.RPT_ALERT, 
                                                "alert:Lost connection to target PLC")
                gv.gDebugPrint("Lost connection to target PLC", logType=gv.LOG_INFO)
                continue
            resultGet = val1 + val2
            gv.gDebugPrint("Get PLC result: %s" %str(resultGet), logType=gv.LOG_INFO)
            matchRst = resultGet == resultExp
            if not matchRst:
                gv.iMonitorClient.addReportDict(monitorClient.RPT_ALERT, 
                                                "alert:PLC output not match with expected")
                gv.gDebugPrint("PLC output not match with expected")
                continue
            #self.dataManager.setCoilState(matchRst, resultGet)
            gv.iMonitorClient.addReportDict(monitorClient.RPT_NORMAL, "PLC Control Loop Normal")
            print("Finish one PLC check round.")
            
        gv.gDebugPrint("PLC client terminated", logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    client = plcControllerApp()
    client.startClient()

if __name__ == "__main__":
    main()
