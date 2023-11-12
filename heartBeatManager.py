import asyncio
import sdbus

from sdbus_async.networkmanager import (
    NetworkManager,
    NetworkDeviceGeneric,
    DeviceState,
    NetworkManagerState
 )

#CONSTANTS

HEARTBEAT_PERIOD=5
HEARTBEAT_ON=0.5
HEARTBEAT_PATTERN_ONLINE="ONLINE"
HEARTBEAT_PATTERN_OFFLINE="OFFLINE"


############ CLASSES

############# HEARTBEAT MANAGER

class HeartBeatManager:

    def __init__(self):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE
        self.netman = NetworkManager()
        #asyncio.run(self.init_net_status())

    async def init_net_status(self):
        state = await self.netman.state
        self.stateChange(state)

    def setOnline(self):
        self.pattern = HEARTBEAT_PATTERN_ONLINE

    def setOffline(self):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE


    def stateChange(self, new_state):
        print("state changed baby!")
        if new_state == NetworkManagerState.CONNECTED_LOCAL or new_state == NetworkManagerState.CONNECTED_SITE or new_state == NetworkManagerState.GLOBAL:
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
        #await self.blink()


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
        #await self.blink()


    async def stateChangeCatcher(self):
        print("start catcher")

        init_state = await self.netman.state
        self.stateChange(init_state)

        async for new_state in self.netman.state_changed:
            print("toto")
            self.stateChange(new_state)



    async def blink_loop(self):
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

