#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        s7LadderLogic.py
#
# Purpose:     This module is the PLC ladder logic simulation module example for 
#              the PLC emulator. Both the PLC emulator and controller will run the 
#              same ladder logic at the same time. This module inherits from the 
#              <lib/modbusTcpCom.py>'s ladderLogic class. If you want to build your 
#              own ladder logic, you can copy this module and modify it.
#  
# Author:      Yuancheng Liu
#
# Created:     2024/11/01
# version:     v0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

# Change below line to use the controller's global if you copy in the controller side
import s7commPlcGlobal as gv 
import snap7Comm


class ladderLogic(snap7Comm.rtuLadderLogic):

    def __init__(self, parent, nameStr):
        super().__init__(parent, ladderName=nameStr)

    def initLadderInfo(self):
        self.srcAddrValInfo = {'addressIdx': (1, 2), 'dataIdx': (0, 2, 4, 6)}
        self.destAddrValInfo = {'addressIdx': (3, 4), 'dataIdx': (0, 2, 4, 6)}

    def runLadderLogic(self, inputData=None):
        print(" - runLadderLogic")
        addr, dataIdx, datalen = inputData
        print("Received data write request: ")
        print("Address: %s " %str(addr))
        print("dataIdx: %s " %str(dataIdx))
        print("datalen: %s" %str(datalen))
        srcMIdx = self.srcAddrValInfo['addressIdx'] # source memory index
        srcDIdx = self.srcAddrValInfo['dataIdx'] # source data index

        if addr in srcMIdx and dataIdx in srcDIdx:
            # Get all current memory source value 
            ms0 = self.parent.getMemoryVal(srcMIdx[0], srcDIdx[0])
            ms1 = self.parent.getMemoryVal(srcMIdx[0], srcDIdx[1])
            ms2 = self.parent.getMemoryVal(srcMIdx[0], srcDIdx[2])
            ms3 = self.parent.getMemoryVal(srcMIdx[0], srcDIdx[3])
            ms4 = self.parent.getMemoryVal(srcMIdx[1], srcDIdx[0])
            ms5 = self.parent.getMemoryVal(srcMIdx[1], srcDIdx[1])
            ms6 = self.parent.getMemoryVal(srcMIdx[1], srcDIdx[2])
            ms7 = self.parent.getMemoryVal(srcMIdx[1], srcDIdx[3])
            
            # Run the rung and set all the memory destination value
            # rung 0: ms0 and ms1 -> ds0
            c0 = ms0 and ms1
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][0], 
                                    self.destAddrValInfo['dataIdx'][0], c0)
            # rung 1: not ms2 -> ds1
            c1 = not ms2
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][0],
                                    self.destAddrValInfo['dataIdx'][1], c1)
            # rung 2: ms2 and ms3 and ms4 -> ds2
            c2 = ms3
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][0],
                                    self.destAddrValInfo['dataIdx'][2], c2)
            # rung 3: ms0 or ms6-> ds3
            c3 = ms0 or ms6
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][0],
                                    self.destAddrValInfo['dataIdx'][3], c3)
            # rung 4: not(ms4 or ms5) -> ds4
            c4 = not(ms4 or ms5)
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][1],
                                    self.destAddrValInfo['dataIdx'][0], c4)
            # rung 5: not ms0 or ms6 -> ds5
            c5 = ms5 or ms6
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][1],
                                     self.destAddrValInfo['dataIdx'][1], c5)
            # rung 6: ms3 or not ms7 -> ds6
            c6 = ms3 or not ms7
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][1],
                                     self.destAddrValInfo['dataIdx'][2], c6)
            # rung 7: not ms5 -> ds7
            c7 = not ms5
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'][1],
                                     self.destAddrValInfo['dataIdx'][3], c7)
            