"""
Listen to some available signals from NetworkManager
"""

from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop


import NetworkManager
import time

def out(msg):
    print("%s %s" % (time.strftime('%H:%M:%S'), msg))

def statechange(nm, interface, signal, state):
    out("State changed to %s" % NetworkManager.const('STATE', state))

def adddevice(nm, interface, signal, device_path):
    try:
        out("Device %s added" % device_path.IpInterface)
    except NetworkManager.ObjectVanished:
        # Sometimes this signal is sent for *removed* devices. Ignore.
        pass

def main():
    DBusGMainLoop(set_as_default=True)
    NetworkManager.NetworkManager.OnStateChanged(statechange)
    NetworkManager.NetworkManager.OnDeviceAdded(adddevice)

    out("Waiting for signals")
    print("let's start signal loop")

    loop = GLib.MainLoop()
    print("starting")

    loop.run()
    print("started")

if __name__ == '__main__':
    main()
