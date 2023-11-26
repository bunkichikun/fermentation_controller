import asyncio
import time

import board
import adafruit_dht
import rrdtool

import fc_settings

#CONSTANTS

TMP_CTRL_PERIOD = 15

DHT_READ_RETRY_NUMBER=15

RRD_DB_NAME = "run/temp_ctrl.rrd"
RRD_TOTAL_DURATION = 60 * 24 * 3   # 3 days



# functions


def generate_graph(t):
    rrdtool.graph("/home/benoit/public_html/temp.png",
                  "--start", str(t),
                  "--end", "now",
                  "--height", "700",
                  "--width", "2400",
                  "DEF:mytemp="+RRD_DB_NAME+":temp:AVERAGE",
                  "DEF:myhum="+RRD_DB_NAME+":hum:AVERAGE",
                  "LINE2:mytemp#FF0000",
                  "LINE3:myhum#00FF00")




############ CLASSES


######### TEMPERATURE MANAGER

class TemperatureManager:

    def __init__(self, targetTemp):
        self.targetTemperature = targetTemp
        fc_settings.FC_LOGGER.info("creating RRD database")
        self.dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True)
        rrdtool.create(
            RRD_DB_NAME,
            "--start","now",
            "--step", str(2 * TMP_CTRL_PERIOD),
            "DS:temp:GAUGE:"+ str(4 * TMP_CTRL_PERIOD) +":0:90",
            "DS:hum:GAUGE:"+ str(4 * TMP_CTRL_PERIOD) +":0:100",
            "RRA:AVERAGE:0.5:1:" + str(RRD_TOTAL_DURATION))

    async def checkTemperature(self):
        fc_settings.FC_LOGGER.info("check Temperature")

        for i in [n for n in range(0,DHT_READ_RETRY_NUMBER)]:
            try:

                (temperature, humidity) = (self.dhtDevice.temperature, self.dhtDevice.humidity)
                rrdtool.update(RRD_DB_NAME,'N:%s:%s'% (temperature, humidity))
                return (temperature, humidity)

            except RuntimeError as error:
                fc_settings.FC_LOGGER.error("TmpCtrl Read Exception: " + error.args[0])
                continue
            except Exception as error:
                self.dhtDevice.exit()
                raise error


    async def temperatureControl(self):
        (temp, humid) = await self.checkTemperature()
        fc_settings.FC_LOGGER.info("Temp: " + str(temp) + " Humidity: "+ str(humid))
        if temp < self.targetTemperature:
            # turn heating on
            fc_settings.FC_LOGGER.info("turn heating on")
        else:
            pass
            #fc_settings.FC_LOGGER.info("waiting for temperature to decrease")


    async def loop(self):
        while True:
            await self.temperatureControl()
            await asyncio.sleep(TMP_CTRL_PERIOD)

