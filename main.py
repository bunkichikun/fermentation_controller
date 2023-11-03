
# workaround to let NetworkManager minimal example work
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import NetworkManager
import asyncio

#CONSTANTS
HEARTBEAT_PERIOD=5
HEARTBEAT_ON=0.5
HEARTBEAT_PATTERN_ONLINE="ONLINE"
HEARTBEAT_PATTERN_OFFLINE="OFFLINE"


# is everything allright with NetworkManager?
NetworkManager.NetworkManager.Version


# CLASSES
class HeartBeatManager:

    

    def __init__(self, netMgr):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE
        self.netman = netMgr
        self.netman.onStateChanged = self.stateChangeHandler
        self.stateChangeHandler(self.netman.State)

        
    def setOnline(self):
        self.pattern = HEARTBEAT_PATTERN_ONLINE
  
    def setOffline(self):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE
 
    def stateChangeHandler(self, state):
        print(str(state))
        if state ==  NetworkManager.NM_STATE_CONNECTED_LOCAL or state == NetworkManager.NM_STATE_CONNECTED_GLOBAL:
            print("connected local or global")
            self.setOnline()
        else:
            print("not connected")
            self.setOffline()

    async def pulseOffline(self):
        print("light on :" + str(HEARTBEAT_ON))
        #TODO GPIO ON
        await asyncio.sleep(HEARTBEAT_ON)
        
        print("light off :" + str(HEARTBEAT_PERIOD - HEARTBEAT_ON))
        #TODO GPIO OFF
        await asyncio.sleep(HEARTBEAT_PERIOD - HEARTBEAT_ON)

    async def pulseOnline(self):
        print("light on :" + str(HEARTBEAT_ON/2))
        #TODO GPIO ON
        await asyncio.sleep(HEARTBEAT_ON/2)
        
        print("light off :" + str(HEARTBEAT_ON/2))
        #TODO GPIO OFF
        await asyncio.sleep(HEARTBEAT_ON/2)
        
        print("light on :" + str(HEARTBEAT_ON/2))
        #TODO GPIO ON
        await asyncio.sleep(HEARTBEAT_ON/2)

        print("light off :" + str(HEARTBEAT_PERIOD - 3/2*HEARTBEAT_ON))
        #TODO GPIO OFF
        await asyncio.sleep(HEARTBEAT_PERIOD - 3/2*HEARTBEAT_ON)
        
        
    async def blink(self):
        print("start blinking")

        while True:
            
            if self.pattern == HEARTBEAT_PATTERN_ONLINE:
                print("pulse online")
                await self.pulseOnline()
            elif self.pattern == HEARTBEAT_PATTERN_OFFLINE:
                print("pulse offline")
                await self.pulseOffline()
            else:
                print("not supported pattern")
    



myHBM = HeartBeatManager(NetworkManager.NetworkManager)
#NetworkManager.NetworkManager.OnStateChanged(myHBM.stateChangeHandler)

asyncio.run(myHBM.blink())
