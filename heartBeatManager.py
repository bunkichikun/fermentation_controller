import asyncio
import sdbus

from gpiozero import LED

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

HEART_BEAT_LED_GPIO = 17


############ CLASSES

############# HEARTBEAT MANAGER

class HeartBeatManager:

    def __init__(self):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE
        self.netman = NetworkManager()
        self.led = LED(HEART_BEAT_LED_GPIO)
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
        self.led.on()
        await asyncio.sleep(HEARTBEAT_ON)

        print("light off :" + str(HEARTBEAT_PERIOD - HEARTBEAT_ON))
        self.led.off()
        await asyncio.sleep(HEARTBEAT_PERIOD - HEARTBEAT_ON)


    async def pulseOnline(self):
        print("light on :" + str(HEARTBEAT_ON/2))
        self.led.on()
        await asyncio.sleep(HEARTBEAT_ON/2)

        print("light off :" + str(HEARTBEAT_ON/2))
        self.led.off()
        await asyncio.sleep(HEARTBEAT_ON/2)

        print("light on :" + str(HEARTBEAT_ON/2))
        self.led.on()
        await asyncio.sleep(HEARTBEAT_ON/2)

        print("light off :" + str(HEARTBEAT_PERIOD - 3/2*HEARTBEAT_ON))
        self.led.off()
        await asyncio.sleep(HEARTBEAT_PERIOD - 3/2*HEARTBEAT_ON)



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

