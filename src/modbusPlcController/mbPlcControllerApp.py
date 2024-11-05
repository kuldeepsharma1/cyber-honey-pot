#-----------------------------------------------------------------------------
# Name:        mbPlcControllerApp.py
#
# Purpose:     This modulde is the controller program start a Modbus-TCP PLC 
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
import udpCom

from mbLadderLogic import ladderLogic

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ Data storage and management module running parallel with the main thread 
        to handle the UDP data fetch request.
    """
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        self.plcConnected = False   # flag to identify whehter PLC is connected.
        self.coilStateList = []     # plc coils state
        self.rstMatchFlg = False    # flag to identify whether the PLC state match the expect result.
        self.udpServer = udpCom.udpServer(None, gv.gUDPPort)

    #-----------------------------------------------------------------------------
    def msgHandler(self, msg):
        """ The request handler method passed into the UDP server to handle the 
            incoming messages.
        """
        if isinstance(msg, bytes): msg = msg.decode('utf-8')
        msg = msg.strip()
        if str(msg).lower() == 'getstate':
            # Return PLC not connected state
            if not self.plcConnected: return 'state: PLC rejected connection.'
            # Return the PLC result compare state
            state = 'normal' if self.rstMatchFlg else 'error'
            val = ';'.join([str(val) for val in self.coilStateList]) if self.rstMatchFlg else gv.gFlgStr
            return 'state:'+str(state)+';'+val
        else:
            return 'Error: Input request invalid: %s' %str(msg)

    def setCoilState(self, match, val):
        """ Set the coil state list and match flag """
        if match:
            self.rstMatchFlg = True
            self.coilStateList = val
        else:
            self.rstMatchFlg = False

    def setPLCconnection(self, state):
        self.plcConnected = state

    def run(self):
        gv.gDebugPrint("UDP server started listening port: %s" %str(gv.gUDPPort), 
                       logType=gv.LOG_INFO)
        self.udpServer.serverStart(handler=self.msgHandler)

    def stop(self):
        self.udpServer.serverStop()
        endClient = udpCom.udpClient(('127.0.0.1', gv.gUDPPort))
        endClient.disconnect()
        endClient = None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class plcControllerApp(object):
    """ PLC controller main program. It will generate the PLC control request 
        randomly then check the plc execution result.
    """
    def __init__(self) -> None:
        self.dataManager = DataManager(None)
        self.dataManager.start()
        self.modbusClient = modbusTcpCom.modbusTcpClient(gv.gPlcIP, tgtPort=gv.gPlcPort)
        self.ladderLogic = ladderLogic(None)
        self.terminate = False
        # Test connection
        while not self.modbusClient.checkConn():
            gv.gDebugPrint('Try connect to the PLC', logType=gv.LOG_INFO)
            gv.gDebugPrint("Read coil state: %s" %str(self.modbusClient.getCoilsBits(0, 8)), 
                           logType=gv.LOG_INFO)
            time.sleep(0.5)

    #-----------------------------------------------------------------------------
    def startClient(self):
        """ Start the PLC client loop to send the holding register and get the coil 
            states, then compare with the local calculated result. If match, means 
            PLC works normally, else means PLC has some problem or under attack.
        """
        gv.gDebugPrint("PLC controller started", logType=gv.LOG_INFO)

        while not self.terminate:
            gv.gDebugPrint("Start to set the registers.", logType=gv.LOG_INFO)
            # generate random register input
            regVals = [randint(0, 1) for i in range(8)]
            gv.gDebugPrint("Random generted input: %s" %str(regVals), logType=gv.LOG_INFO)
            result = self.ladderLogic.runLadderLogic(regVals)
            reusltExp = [i == 1 for i in result]
            gv.gDebugPrint("Calculated output: %s" %str(reusltExp), logType=gv.LOG_INFO)
            for i in range(8):
                self.modbusClient.setHoldingRegs(i, regVals[i])
                time.sleep(0.1)
            time.sleep(1)
            resultGet = self.modbusClient.getCoilsBits(0, 4)
            gv.gDebugPrint("Get PLC reuslt: %s" %str(resultGet), logType=gv.LOG_INFO)
            # set connection state
            connectionRst = False if resultGet is None else True 
            self.dataManager.setPLCconnection(connectionRst)
            # check the result
            matchRst = resultGet == reusltExp
            self.dataManager.setCoilState(matchRst, resultGet)
            time.sleep(gv.gPlcConnInt)
            print("Finish one PLC check round.")

        gv.gDebugPrint("PLC client terminated", logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    client = plcControllerApp()
    client.startClient()

if __name__ == "__main__":
    main()
