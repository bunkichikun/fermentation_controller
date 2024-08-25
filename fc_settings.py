# Copyright (c) 2024 Benoît LIBEAU

import logging

LOG_FILE_PATH = "run/fermentation_controller.log"


#GPIOS

# Product Temperature Probe with DS18B20
# add in /boot/config.txt dtoverlay=w1-gpio,gpiopin=6 for PIN 6
#

# Chamber temp on GPIO 4



def init_fc_logger():
    logging.basicConfig(filename=LOG_FILE_PATH,
                        filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    return logging.getLogger("FC_Logger")


FC_LOGGER = logging.getLogger('FC_Logger')
