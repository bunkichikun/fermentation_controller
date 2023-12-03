import asyncio
import time
import signal

from argparse import ArgumentParser
import os
from pathlib import Path
import sys

from heartBeatManager import  HeartBeatManager
from temperatureManager import TemperatureManager
import fc_settings

#CONSTANTS

LOCK_FILE_PATH = "run/LOCK"


############ CLASSES


############ FERMENTATION CONTROLLER


class FermentationController:

    def __init__(self):


        self.startTime = time.time()
        #logging
        fc_settings.init_fc_logger()

        #LOCK
        if self.checkLock():
            print("Lock is taken... a fermentation_controller instance is already running\nTerminating...")
            sys.exit()
        self.takeLock()

        # Prepare signal handler
        self.loop = asyncio.new_event_loop()
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            self.loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self.signalHandler(s, self.loop)))
        # TODO set this loop as system current loop https://www.slingacademy.com/article/python-asyncio-what-are-coroutines-and-event-loops/
        asyncio.set_event_loop(self.loop)

        # init members
        self.tmpCtrl = TemperatureManager(self.startTime)
        self.HeartBeatMgr = HeartBeatManager()


    def main_loop(self):
        # MAIN LOOP
        fc_settings.FC_LOGGER.info("starting FC Main Loop")

        try:
            self.loop.run_until_complete( asyncio.gather(
                self.tmpCtrl.start_prometheus(),
                self.tmpCtrl.loop(),
                self.HeartBeatMgr.blink_loop(),
                self.HeartBeatMgr.stateChangeCatcher()))

        except asyncio.CancelledError:
            fc_settings.FC_LOGGER.error("CancelledError in main_loop")

        self.loop.close()
        fc_settings.FC_LOGGER.info("finished main loop")
        self.die()


    def checkLock(self):
        lock_file = Path(LOCK_FILE_PATH)
        return lock_file.is_file()


    def takeLock(self):
        try:
            fc_settings.FC_LOGGER.info("taking Lock file")
            with open(LOCK_FILE_PATH, 'x') as f:
                f.write('%s %s\n' % (int(time.time()), os.getpid()))
        except FileNotFoundError:
            fc_settings.FC_LOGGER.error("The Lock file directory does not exist")
        except FileExistsError:
            fc_settings.FC_LOGGER.error("The Lock file already exist")


    def freeLock(self):
        fc_settings.FC_LOGGER.info("removing Lock file")
        p=Path(LOCK_FILE_PATH)
        p.unlink(False)


    async def signalHandler(self, sig, loop):

        fc_settings.FC_LOGGER.info(" received signal: " + str(sig))
        tasks = asyncio.all_tasks() - {asyncio.current_task()}
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


    def die(self):
        fc_settings.FC_LOGGER.info("die die die!")
        self.freeLock()
        sys.exit()


######### END OF CLASSES


def do_main():
    myFC = FermentationController()
    myFC.main_loop()
    myFC.die()


def kill_and_rm_lock_file():
    try:
        with open(LOCK_FILE_PATH, 'r') as f:
            content = f.readlines()

            line=content[0]
            [timestamp, pid] = line.split(" ")
            try:
                os.kill(int(pid), signal.SIGHUP)
            except ProcessLookupError:
                print("no such process...")
            except TabError:
                print("LOCK File seems to be empty")

            p=Path(LOCK_FILE_PATH)
            p.unlink(False)

    except FileNotFoundError:
        print("The Lock file directory does not exist")

    sys.exit()


#def gen_rrdtool_graph():
#    try:
#        with open(LOCK_FILE_PATH, 'r') as f:
#            content = f.readlines()
#
#            line=content[0]
#            [timestamp, pid] = line.split(" ")
#            print("lets' graph baby! time is:" + str(timestamp))
#            generate_graph(timestamp)
#    except FileNotFoundError:
#        print("The Lock file directory does not exist")
#
#    sys.exit()



######## MAIN()
if __name__ == "__main__":

    parser = ArgumentParser(
        prog="fermentation_controller",
        description="Benoit's famous fully-python3-asyncio controller of a thermostated chamber",
    )
    parser.add_argument("-k", "--kill",
                        help="gracefully kill any running instance",
                        action='store_true')
    parser.add_argument("-g", "--graph",
                        help="generate new image in public_html",
                        action="store_true")

    args = parser.parse_args()

    if args.kill:
        print("Let's kill the running instance and remove the lock file")
        kill_and_rm_lock_file()
#    elif args.graph:
#        print("let's generate a new graph and copy it to public_html")
#        gen_rrdtool_graph()
    else:
        do_main()


