#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        monitorClient.py [python3]
#
# Purpose:     Client to report PLC state to the monitor hub. 
#  
# Author:      Yuancheng Liu
#
# Created:     2024/11/02
# version:     v0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import copy
import requests
import threading

class monitorClient(threading.Thread):

    def __init__(self, monIP, monPort, reportInterval=5):
        """ Init the monitor client.
            Args:
                monIP (str): monitor hub IP address.
                monPort (int): monitor hub port.
                reportInterval (int, optional): report interval in seconds. Defaults to 60.
        """
        threading.Thread.__init__(self)
        self.monIP = monIP
        self.monPort = monPort
        self.reportInterval = reportInterval
        self.reportLock = threading.Lock()
        self._postUrl = "https://%s:%s/dataPost/" % (self.monIP, str(self.monPort))
        self.parentInfoDict = None
        self.monConnected = False
        self.terminate = False 
    
    #-----------------------------------------------------------------------------
    def setParentInfo(self, parID, parIP, parType, parPro, tgtID=None, tgtIP=None, ladderID=None):
        """ Set the parent info.
            Args:
                parID (str): parent ID.
                parIP (str): parent IP address.
                parType (str): parent type.
                parPro (str): parent protocol.
                tgtID (str, optional): target ID. Defaults to None.
                tgtIP (str, optional): target IP address. Defaults to None.
        """
        self.parentInfoDict = {
            "ID": parID, 
            "IP": parIP, 
            "Type": parType, 
            "Protocol": parPro,
            "LadderID": ladderID
        }
        if tgtID is not None: self.parentInfoDict["TargetID"] = tgtID
        if tgtIP is not None: self.parentInfoDict["TargetIP"] = tgtIP

    def logtoMonitor(self, logMsg):
        """ Report the log message to monitor hub.
            Args:
                logMsg (str): log message.
        """
        self.report2Monitor("Log", {"Msg": logMsg})

    #-----------------------------------------------------------------------------
    def report2Monitor(self, action, data):
        """ Report the data to monitor hub.
            Args:
                action (str): action name.
                data (dict): data to report.
        """
        if self.parentInfoDict is None: return
        dataDict = copy.deepcopy(self.parentInfoDict)
        dataDict["Action"] = action
        dataDict["Data"] = data
        self._postData(self._postUrl, dataDict)

    #-----------------------------------------------------------------------------
    def _postData(self, postUrl, jsonDict, postfile=False):
        """ Send HTTP POST request to send data.
            Args:
                postUrl (str): url string.
                jsonDict (dict): json data send via POST.
                postfile (bool, optional): True: upload file, False: submit data/message.
                    Defaults to False.
            Returns:
                _type_: Server repsonse or None if post failed / lose connection.
        """
        self.reportLock.acquire()
        try:
            res = requests.post(postUrl, files=jsonDict, verify=False) if postfile else requests.post(postUrl, json=jsonDict, verify=False)
            if res.ok:
                print("http server reply: %s" % str(res.json()))
                self.reportLock.release()
                return res.json()
        except Exception as err:
            print("Error: _postData() > http server not reachable or POST error: %s" % str(err))
            self.monConnected = False
        if self.reportLock.locked(): self.reportLock.release()
        return None

    #-----------------------------------------------------------------------------
    def run(self):
        """ Main state report and task fetch loop called by start(). """
        print("Start the C2 client main loop.")
        while not self.terminate:
            # report the state to C2 1st if there is state in queue.
            if self.submitAllStateToC2():
                print("Reported the current state to C2.")
            else:
                print("Try to get task from C2 Server.")
                self.fetchTaskFromC2()
            time.sleep(self.reportInterval)
        print("C2 client main loop end.")