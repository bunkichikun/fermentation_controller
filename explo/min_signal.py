
# workaround to let NetworkManager minimal example work
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
# to catch dbus signals
from gi.repository import GLib

import NetworkManager
import time


# is everything allright with NetworkManager?
print(str(NetworkManager.NetworkManager.Version))


def stateChangeHandler(self, state):
    print(str(state))
    if state ==  NetworkManager.NM_STATE_CONNECTED_LOCAL or state == NetworkManager.NM_STATE_CONNECTED_GLOBAL:
        print("connected local or global")
        self.setOnline()
    else:
        print("not connected")
        self.setOffline()



#myHBM = HeartBeatManager(NetworkManager.NetworkManager)
NetworkManager.NetworkManager.OnStateChanged(stateChangeHandler)

loop=GLib.MainLoop()
print("starting Loop")
loop.run()
print("started Loop")


    
