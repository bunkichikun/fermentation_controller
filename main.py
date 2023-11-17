import asyncio
import sdbus
import time

from argparse import ArgumentParser
import os
from pathlib import Path
import sys
import signal

from heartBeatManager import  HeartBeatManager
from temperatureManager import TemperatureManager


#CONSTANTS

TARGET_TEMP = 60

LOCK_FILE_PATH = "toto"


############ CLASSES


############ FERMENTATION CONTROLLER


class FermentationController:

    def __init__(self, targetTemp):
        if self.checkLock():
            print("Lock is taken... a fermentation_controller instance is already running\nTerminating...")
            sys.exit()
        self.takeLock()
        self.tmpCtrl = TemperatureManager(targetTemp)
        self.HeartBeatMgr = HeartBeatManager()


    async def loop(self):
        print("starting FC Main Loop")
        await asyncio.gather(self.tmpCtrl.loop(),
                             self.HeartBeatMgr.blink_loop(),
                             self.HeartBeatMgr.stateChangeCatcher())
                             # TODO add signal handler


    def checkLock(self):
        lock_file = Path(LOCK_FILE_PATH)
        return lock_file.is_file()


    def takeLock(self):
        try:
            with open(LOCK_FILE_PATH, 'x') as f:
                f.write('%s %s\n' % (int(time.time()), os.getpid()))
        except FileNotFoundError:
            print("The Lock file directory does not exist")
        except FileExistsError:
            print("The Lock file already exist")


    def freeLock(self):
        p=Path(LOCK_FILE_PATH)
        p.unlink(False)


    def singalHandler(self):
        pass


    def die(self):
        self.freeLock()
        # TODO call die of other members of FC


######### END OF CLASSES


def main_loop():
    sdbus.set_default_bus(sdbus.sd_bus_open_system())

    myFC = FermentationController(TARGET_TEMP)
    asyncio.run(myFC.loop())
    myFC.die()


def kill_and_rm_lock_file():
    try:
        with open(LOCK_FILE_PATH, 'r') as f:
            content = f.readlines()
    except FileNotFoundError:
        print("The Lock file directory does not exist")

    for line in content:
        [timestamp, pid] = line.split(" ")
        try:
            os.kill(int(pid), signal.SIGHUP)
        except ProcessLookupError:
            print("no such process...")

        p=Path(LOCK_FILE_PATH)
        p.unlink(False)



######## MAIN()
if __name__ == "__main__":

    parser = ArgumentParser(
        prog="fermentation_controller",
        description="Benoit's famous fully-python3-asyncio controller of a thermostated chamber",
    )
    parser.add_argument("-k", "--kill",
                        help="gracefully kill any running instance",
                        action='store_true')
    #parser.add_argument("-c", "--clean",
    #                    help="remove lock file",
    #                    action="store_true")

    args = parser.parse_args()

    print(args.kill)

    if args.kill:
        kill_and_rm_lock_file()
        pass
    else:
        main_loop()


