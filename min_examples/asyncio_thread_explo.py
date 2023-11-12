import asyncio
import time
import NetworkManager


from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
# to catch dbus signals
from gi.repository import GLib


def blocking_io_1():
    print(f"start blocking_io_1 at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    #while True:
    for i in [1,2,3,4]:

        time.sleep(1)
        print(f"blocking_io_1 complete at {time.strftime('%X')}")


async def non_blocking_io_1():
    print(f"start non_blocking_io_1 at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    #while True:
    for i in [1,2,3,4]:
        await asyncio.sleep(1)
        print(f"non_blocking_io_1 complete at {time.strftime('%X')}")


def blocking_io_2():
    print(f"start blocking_io_2 at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    while True:
        time.sleep(2)
        print(f"blocking_io_2 complete at {time.strftime('%X')}")

async def non_blocking_io_2():
    print(f"start non_blocking_io_2 at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    while True:
        await asyncio.sleep(2)
        print(f"non_blocking_io_2 complete at {time.strftime('%X')}")



def stateChangeHandler(nm, interface, signal, state):
    print(str(state))
    if state ==  NetworkManager.NM_STATE_CONNECTED_LOCAL or state == NetworkManager.NM_STATE_CONNECTED_GLOBAL:
        print("connected local or global")
        #self.setOnline()
    else:
        print("not connected")
        #self.setOffline()


        
async def main():

    loop=GLib.MainLoop()

    print(f"started main at {time.strftime('%X')}")

    await asyncio.gather(
        #asyncio.to_thread(loop.run()),
        asyncio.to_thread(blocking_io_1()),
        asyncio.to_thread(blocking_io_2())
        #non_blocking_io_1(),
        #non_blocking_io_2()
    )

    print(f"finished main at {time.strftime('%X')}")



netM = NetworkManager.NetworkManager
netM.OnStateChanged(stateChangeHandler)

#loop=GLib.MainLoop()
#print("starting")
#loop.run()

asyncio.run(main())
