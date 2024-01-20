# Copyright (c) 2024 Benoît LIBEAU

import asyncio
import time

import board
import adafruit_dht

from w1thermsensor import AsyncW1ThermSensor

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

#import rrdtool
from prometheus_client import Gauge, Summary
from prometheus_async.aio.web import start_http_server

import fc_settings

#CONSTANTS

TMP_CTRL_PERIOD = 15

DHT_READ_RETRY_NUMBER=15

RRD_DB_NAME = "run/temp_ctrl.rrd"
RRD_TOTAL_DURATION = 60 * 24 * 3   # 3 days

RELAY_COOLING_GPIO = 20 # black
RELAY_STIRRING_GPIO = 7 # brown
RELAY_HEATING_GPIO = 11 # purple

# TARGET TEMPERATURE
TARGET_INIT_TEMP = 30
TARGET_INIT_DURATION = 60*60*0.5 #60 * 60 * 4
TARGET_FERMENTATION_TEMP = 39
TARGET_FERMENTATION_DURATION = 60*60*1 #60 * 60 * 19
TARGET_COOLING_TEMP = 15
TARGET_COOLING_DURATION = 60*60*1 #60 * 60 * 5
TARGET_REST_TEMP = 15

#PID Coefficients
PID_K_P = 1
PID_K_I = 0
PID_K_D = 0

PROMETHEUS_EXPOSED_PORT = 8000

# Metrics
FC_PROCESSING_TIME = Summary('f_loop_time', "Time spent in the temperature control of the llop")


# functions

#def generate_graph(t):
#    rrdtool.graph("/home/benoit/public_html/temp.png",
#                  "--start", str(t),
#                  "--end", "now",
#                  "--height", "700",
#                  "--width", "2400",
#                  "DEF:mytemp="+RRD_DB_NAME+":temp:AVERAGE",
#                  "DEF:myhum="+RRD_DB_NAME+":hum:AVERAGE",
#                  "LINE2:mytemp#FF0000",
#                  "LINE3:myhum#00FF00")


def target_temp(t):
    if t<=0:
        raise RuntimeError("No target temperature defined in the past")

    elif t <= TARGET_INIT_DURATION:
        return TARGET_INIT_TEMP

    elif t<= TARGET_INIT_DURATION + TARGET_FERMENTATION_DURATION:
        return TARGET_FERMENTATION_TEMP

    elif t<= TARGET_INIT_DURATION + TARGET_FERMENTATION_DURATION + TARGET_COOLING_DURATION:
        # linear decrease of target temperature from TARGET_FERMENTATION to TARGET_COOLING
        cooling_factor = (t - TARGET_INIT_DURATION - TARGET_FERMENTATION_DURATION) / TARGET_COOLING_DURATION
        return TARGET_FERMENTATION_TEMP + (t - TARGET_INIT_DURATION - TARGET_FERMENTATION_DURATION) * (TARGET_COOLING_TEMP - TARGET_FERMENTATION_TEMP) / TARGET_COOLING_DURATION
    else:
        return TARGET_REST_TEMP


############ CLASSES


######### TEMPERATURE MANAGER

class TemperatureManager:

    def __init__(self, startTime):

        # intialize devices
        self.dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True) # for Chamber temp & humidity
        self.dsSensor = AsyncW1ThermSensor()   #DS18B20 for Product Temp
        self.stirring = GPIO.setup(RELAY_STIRRING_GPIO, GPIO.OUT)
        self.heating = GPIO.setup(RELAY_HEATING_GPIO, GPIO.OUT)
        self.cooling = GPIO.setup(RELAY_COOLING_GPIO, GPIO.OUT)

        self.startTime = startTime

        # cumulated Integration Error
        self.cumIntErr = 0

        # temps for PID control
        self.targetTemperature = target_temp(1)
        self.previousTemp = 0
        self.currentTemp = 0

        #Prometheus Gauges
        self.productTemp = Gauge("fc_product_temp", "Temperature of the Product")
        self.chamberTemp = Gauge("fc_chamber_temp", "Temperature of the Frementation Chamber")
        self.chamberHum = Gauge("fc_chamber_hum", "Humidity of the Fermentation Chamber")
        self.targetTemp_g = Gauge("fc_target_temp", "Humidity of the Fermentation Chamber")
        self.PIDFunc_g = Gauge("fc_pid_function","Value of the PID control function")
        self.heating_g = Gauge("fc_heating_cooling", "Heating or Cooling Activated")


        fc_settings.FC_LOGGER.info("creating RRD database")
        # RRD DB INIT
 #       rrdtool.create(
 #           RRD_DB_NAME,
 #           "--start","now",
 #           "--step", str(2 * TMP_CTRL_PERIOD),
 #           "DS:temp:GAUGE:"+ str(4 * TMP_CTRL_PERIOD) +":0:90",
 #           "DS:hum:GAUGE:"+ str(4 * TMP_CTRL_PERIOD) +":0:100",
 #           "RRA:AVERAGE:0.5:1:" + str(RRD_TOTAL_DURATION))


    async def start_prometheus(self):
        fc_settings.FC_LOGGER.info("Starting Prometheus HTTP Server to expose metrics")
        self.prom_http_server = await start_http_server(port=PROMETHEUS_EXPOSED_PORT)
        fc_settings.FC_LOGGER.info("Prometheus HTTP Server started")

    def stirring_on(self):
        GPIO.output(RELAY_STIRRING_GPIO, GPIO.HIGH)

    def stirring_stop(self):
        GPIO.output(RELAY_STIRRING_GPIO, GPIO.LOW)

    def heating_on(self):
        self.heating_g.set(1.0)
        GPIO.output(RELAY_HEATING_GPIO, GPIO.HIGH)

    def heating_stop(self):
        GPIO.output(RELAY_HEATING_GPIO, GPIO.LOW)

    def cooling_on(self):
        self.heating_g.set(-1.0)
        GPIO.output(RELAY_HEATING_GPIO, GPIO.HIGH)

    def cooling_stop(self):
        GPIO.output(RELAY_COOLING_GPIO, GPIO.LOW)


    def die(self):
        self.cooling_stop()
        self.heating_stop()
        self.stirring_stop()


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

    @FC_PROCESSING_TIME.time()
    async def checkTemperature(self):
        #fc_settings.FC_LOGGER.info("check Temperature")

        # Product temperature
        productTemp = await self.dsSensor.get_temperature()
        fc_settings.FC_LOGGER.info("Product Temperature: " + str(productTemp))

        # room temp and humidity
        for i in [n for n in range(0,DHT_READ_RETRY_NUMBER)]:
            try:

                # get temperature
                (chamberTemp, humidity) = (self.dhtDevice.temperature, self.dhtDevice.humidity)

                # put temperature in DB
                #rrdtool.update(RRD_DB_NAME,'N:%s:%s'% (temperature, humidity))
                return (productTemp, chamberTemp, humidity)

            except RuntimeError as error:
                fc_settings.FC_LOGGER.error("TmpCtrl Read Exception: " + error.args[0])
                continue
            except Exception as error:
                self.dhtDevice.exit()
                raise error

    async def temperatureControl(self):
        (productTemp, chamberTemp, humid) = await self.checkTemperature()

        # PID Time step update
        self.previousTemp = self.currentTemp
        self.currentTemp = productTemp
        self.targetTemp = target_temp(time.time() - self.startTime)

        # Gauges update
        self.targetTemp_g.set(self.targetTemp)
        self.chamberTemp.set(chamberTemp)
        self.productTemp.set(productTemp)
        self.chamberHum.set(humid)

        #fc_settings.FC_LOGGER.debug("Time: " + str(time.time() - self.startTime))
        fc_settings.FC_LOGGER.info("Product Temp: " + str(productTemp) + " Chamber Temp: " + str(chamberTemp)  + " Humidity: "+ str(humid))

        U = self.PID_U()
        fc_settings.FC_LOGGER.debug("U: " + str(U))
        self.PIDFunc_g.set(U)

        if U > 0:
        #if self.PID_U() > 0:
            # turn heating on
            self.cooling_stop()
            self.heating_on()
            fc_settings.FC_LOGGER.info("turn heating on")
        else:
            self.heating_stop()
            self.cooling_on()
            pass
            fc_settings.FC_LOGGER.info("turn cooling on")


    async def loop(self):

        self.stirring_on()

        while True:
            await self.temperatureControl()
            await asyncio.sleep(TMP_CTRL_PERIOD)

