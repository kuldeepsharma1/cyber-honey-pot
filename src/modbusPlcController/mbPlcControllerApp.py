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

import mbPlcControllerGlobal as gv
import modbusTcpCom

import monitorClient
from mbLadderLogic import ladderLogic

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

        self.modbusClient = modbusTcpCom.modbusTcpClient(gv.gPlcIP, tgtPort=gv.gPlcPort)
        self.ladderLogic = ladderLogic(None)
        self.terminate = False
        # Test connection
        while not self.modbusClient.checkConn():
            gv.gDebugPrint('Try connect to the PLC', logType=gv.LOG_INFO)
            gv.gDebugPrint("Read coil state: %s" %str(self.modbusClient.getCoilsBits(0, 8)), 
                           logType=gv.LOG_INFO)
            time.sleep(0.5)
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
            regVals = [randint(0, 1) for i in range(8)]
            gv.gDebugPrint("Random generate input: %s" %str(regVals), logType=gv.LOG_INFO)
            result = self.ladderLogic.runLadderLogic(regVals)
            resultExp = [i == 1 for i in result]
            gv.gDebugPrint("Calculated output: %s" %str(resultExp), logType=gv.LOG_INFO)
            for i in range(8):
                self.modbusClient.setHoldingRegs(i, regVals[i])
                time.sleep(0.1)
            time.sleep(1)
            resultGet = self.modbusClient.getCoilsBits(0, 8)
            gv.gDebugPrint("Get PLC result: %s" %str(resultGet), logType=gv.LOG_INFO)
            # set connection state
            connectionRst = False if resultGet is None else True
            if not connectionRst:
                gv.iMonitorClient.addReportDict(monitorClient.RPT_ALERT, 
                                                "alert:Lost connection to target PLC")
                gv.gDebugPrint("Lost connection to target PLC", logType=gv.LOG_INFO)
                continue
            matchRst = resultGet == resultExp
            if not matchRst:
                gv.iMonitorClient.addReportDict(monitorClient.RPT_ALERT, 
                                                "alert:PLC output not match with expected")
                gv.gDebugPrint("PLC output not match with expected")
                continue
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
