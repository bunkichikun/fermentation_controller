import asyncio
import time
import board
import adafruit_dht

#CONSTANTS

TMP_CTRL_PERIOD = 10

DHT_READ_RETRY_NUMBER=15


############ CLASSES


######### TEMPERATURE MANAGER

class TemperatureManager:

    def __init__(self, targetTemp):
        self.targetTemperature = targetTemp
        self.dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True)


    async def checkTemperature(self):
        print("check Temperature")

        for i in [n for n in range(0,DHT_READ_RETRY_NUMBER)]:
            try:

                (temperature, humidity) = (self.dhtDevice.temperature, self.dhtDevice.humidity)
                return (temperature, humidity)

            except RuntimeError as error:
                print("TmpCtrl Read Exception: " + error.args[0])
                continue
            except Exception as error:
                self.dhtDevice.exit()
                raise error

        #temp=42
        #print("temperature is: " +str(temp))
        #return temp


    async def temperatureControl(self):
        (temp, humid) = await self.checkTemperature()
        print ("Temp: " + str(temp) + " Humidity: "+ str(humid))
        if temp < self.targetTemperature:
            # turn heating on
            print("turn heating on")
        else:
            print("waiting for temperature to decrease")


    async def loop(self):
        while True:
            await self.temperatureControl()
            await asyncio.sleep(TMP_CTRL_PERIOD)

