import asyncio
import sdbus

from heartBeatManager import  HeartBeatManager
from temperatureManager import TemperatureManager

#CONSTANTS

TARGET_TEMP = 60



############ CLASSES


############ FERMENTATION CONTROLLER


class FermentationController:

    def __init__(self, targetTemp):
        self.tmpCtrl = TemperatureManager(targetTemp)
        self.HeartBeatMgr = HeartBeatManager()


    async def loop(self):
        print("starting FC Main Loop")
        await asyncio.gather(self.tmpCtrl.loop(),
                             self.HeartBeatMgr.blink_loop(),
                             self.HeartBeatMgr.stateChangeCatcher())



######### END OF CLASSES


sdbus.set_default_bus(sdbus.sd_bus_open_system())

myFC = FermentationController(TARGET_TEMP)
asyncio.run(myFC.loop())




