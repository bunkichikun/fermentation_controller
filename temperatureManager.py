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

# TARGET TEMPERATURE
TARGET_INIT_TEMP = 39
TARGET_INIT_DURATION = 60 * 60 * 4
TARGET_FERMENTATION_TEMP = 39
TARGET_FERMENTATION_DURATION = 60 * 60 * 19
TARGET_COOLING_TEMP = 15
TARGET_COOLING_DURATION = 60 * 60 * 5
TARGET_REST_TEMP = 15

#PID Coefficients
PID_K_P = 1
PID_K_I = 0
PID_K_D = 0


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


def target_temp(t):
    if t<=0:
        raise RuntimeError("No target temperature defined in the past")

    elif t <= TARGET_INIT_DURATION:
        return TARGET_INIT_TEMP

    elif t<= TARGET_FERMENTATION_DURATION:
        return TARGET_FERMENTATION_TEMP

    elif TARGET_COOLING_DURATION:
        return TARGET_COOLING_TEMP

    else:
        return TARGET_REST_TEMP


############ CLASSES


######### TEMPERATURE MANAGER

class TemperatureManager:

    def __init__(self, startTime):

        self.dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True)

        self.startTime = startTime

        # cumulated Integration Error
        self.cumIntErr = 0
        # temp
        self.targetTemperature = target_temp(1)
        self.previousTemp = 0
        self.currentTemp = 0

        fc_settings.FC_LOGGER.info("creating RRD database")
        # RRD DB INIT
        rrdtool.create(
            RRD_DB_NAME,
            "--start","now",
            "--step", str(2 * TMP_CTRL_PERIOD),
            "DS:temp:GAUGE:"+ str(4 * TMP_CTRL_PERIOD) +":0:90",
            "DS:hum:GAUGE:"+ str(4 * TMP_CTRL_PERIOD) +":0:100",
            "RRA:AVERAGE:0.5:1:" + str(RRD_TOTAL_DURATION))


    # PID
    def PID_P(self):
        # diff current temp minux target
        return self.targetTemp - self.currentTemp

    def PID_I(self):
        # cumulative sum temp variation times delta t
        self.cumIntErr = self.cumIntErr + (self.targetTemp - self.currentTemp) * TMP_CTRL_PERIOD
        return self.cumIntErr

    def PID_D(self):
        # old cumsum + temp variation on delta t
        return (self.targetTemp - self.currentTemp) / TMP_CTRL_PERIOD

    def PID_U(self):
        return PID_K_P * self.PID_P() + PID_K_I * self.PID_I() + PID_K_D * self.PID_D()


    async def checkTemperature(self):
        #fc_settings.FC_LOGGER.info("check Temperature")

        for i in [n for n in range(0,DHT_READ_RETRY_NUMBER)]:
            try:

                # get temperature
                (temperature, humidity) = (self.dhtDevice.temperature, self.dhtDevice.humidity)

                # put temperature in DB
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

        self.previousTemp = self.currentTemp
        self.currentTemp = temp
        self.targetTemp = target_temp(time.time() - self.startTime)

        fc_settings.FC_LOGGER.info("Temp: " + str(temp) + " Humidity: "+ str(humid))

        U = self.PID_U()
        fc_settings.FC_LOGGER.debug("U: " + str(U))
        if U > 0:
        #if self.PID_U() > 0:
            # turn heating on
            fc_settings.FC_LOGGER.info("turn heating on")
        else:
            pass
            #fc_settings.FC_LOGGER.info("waiting for temperature to decrease")


    async def loop(self):
        while True:
            await self.temperatureControl()
            await asyncio.sleep(TMP_CTRL_PERIOD)

