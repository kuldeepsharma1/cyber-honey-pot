#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        mbLadderLogic.py [python3]
#
# Purpose:     This module is the ladder logic to get the input contact(holding 
#              register) state then execute the ladder logic and set the output.
#              It inheritets the modbusPlcDataMgr class to get the data from the
#  
# Author:      Yuancheng Liu
#
# Created:     2024/11/01
# version:     v0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import mbPlcControllerGlobal as gv # Change this line to use the controller's global if you copy in the controller side
import modbusTcpCom

#-----------------------------------------------------------------------------
class ladderLogic(modbusTcpCom.ladderLogic):
    """ A test ladder logic program with 8 holding register and 2 level ladder
        logic to set the output coils.
    """
    def __init__(self, parent) -> None:
        super().__init__(parent)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 8
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 8

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