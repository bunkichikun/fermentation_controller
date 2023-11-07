import sdbus
from sdbus_async.networkmanager import NetworkManager

import asyncio

from sdbus_async.networkmanager import (
    NetworkManager,
    NetworkDeviceGeneric,
    DeviceState
 )


#CONSTANTS
HEARTBEAT_PERIOD=5
HEARTBEAT_ON=0.5
HEARTBEAT_PATTERN_ONLINE="ONLINE"
HEARTBEAT_PATTERN_OFFLINE="OFFLINE"

NET_IFACE_TO_MONITOR="wlp0s20f3"

TMP_CTRL_PERIOD = 7


# CLASSES
class HeartBeatManager:

    def __init__(self,iface):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE
        sdbus.set_default_bus(sdbus.sd_bus_open_system())
        self.netman = NetworkManager()
        self.iface = iface
        
    def setOnline(self):
        self.pattern = HEARTBEAT_PATTERN_ONLINE

        
    def setOffline(self):
        self.pattern = HEARTBEAT_PATTERN_OFFLINE

        
    #def stateChangeHandler(self, nm, interface, signal, state):
    #    print(str(state))
    #    if state ==  NetworkManager.NM_STATE_CONNECTED_LOCAL or state == NetworkManager.NM_STATE_CONNECTED_GLOBAL:
    #        print("connected local or global")
    #        self.setOnline()
    #    else:
    #        print("not connected")
    #        self.setOffline()

    def stateChange(self, new_state, old_state, reason):
        print("state changed baby!")
        print(str((new_state, old_state, reason)))


            
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


    async def init_catcher(self):
        devices_paths = await self.netman.get_devices()
        
        print("Interface         Type     State        Internet Connection")
        for device_path in devices_paths:
            generic = NetworkDeviceGeneric(device_path)
            dev_name = await generic.interface
            print(dev_name)
            if dev_name == self.iface:
                print("found you!")
                return generic



    async def stateChangeCatcher(self):
        print("start catcher")
        dev = await self.init_catcher()
        async for (new_state, old_state, reason) in dev.state_changed:
            print("toto")
            self.stateChange(new_state, old_state, reason)     

            
        
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
    


class TemperatureManager:

    def __init__(self, targetTemp):
        self.targetTemperature = targetTemp

        
    async def checkTemperature(self):
        print("check Temperature")
        #TODO GET READING FROM GPIO
        await asyncio.sleep(1)
        temp=42
        print("temperature is: " +str(temp))
        return temp

    
    async def temperatureControl(self):
        temp = await self.checkTemperature()
        if temp < self.targetTemperature:
            # turn heating on
            print("turn heating on")
        else:
            print("waiting for temperature to decrease")


    async def loop(self):
        while True:
            await self.temperatureControl()
            await asyncio.sleep(TMP_CTRL_PERIOD)
                
            
                
class FermentationController:

    def __init__(self, targetTemp):
        self.tmpCtrl = TemperatureManager(targetTemp)
        self.HeartBeatMgr = HeartBeatManager(NET_IFACE_TO_MONITOR)


        
        
    async def loop(self):
        print("starting FC Main Loop")
        await asyncio.gather(self.tmpCtrl.loop(),
                             self.HeartBeatMgr.blink_loop(),
                             self.HeartBeatMgr.stateChangeCatcher())
            

            

myFC = FermentationController(60)
asyncio.run(myFC.loop())
