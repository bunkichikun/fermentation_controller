import asyncio


#CONSTANTS

TMP_CTRL_PERIOD = 7



############ CLASSES


######### TEMPERATURE MANAGER

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

