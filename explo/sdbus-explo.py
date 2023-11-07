import asyncio
import time
import sdbus
from sdbus_async.networkmanager import NetworkManager
from enum import Enum
from sdbus_async.networkmanager import (
    NetworkManager,
    NetworkDeviceGeneric,
    DeviceState,
    DeviceType,
    DeviceCapabilities as Capabilities,
    ActiveConnection,
    ConnectivityState,
)


async def non_blocking_io_1():
    print(f"start non_blocking_io_1 at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    while True:
    #for i in [1,2,3,4]:
        await asyncio.sleep(1)
        print(f"non_blocking_io_1 complete at {time.strftime('%X')}")

async def non_blocking_io_2():
    print(f"start non_blocking_io_2 at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    while True:
        await asyncio.sleep(2)
        print(f"non_blocking_io_2 complete at {time.strftime('%X')}")



        

def title(enum: Enum) -> str:
    """Get the name of an enum: 1st character is uppercase, rest lowercase"""
    return enum.name.title()


async def list_active_hardware_networkdevice_states(only_hw: bool) -> None:
    """Print the list of activated network devices similar to nmcli device"""
    nm = NetworkManager()
    devices_paths = await nm.get_devices()

    print("Interface         Type     State        Internet Connection")
    for device_path in devices_paths:
        generic = NetworkDeviceGeneric(device_path)

        # Demonstrates an enum to match devices using capabilities:
        if only_hw and await generic.capabilities & Capabilities.IS_SOFTWARE:
            continue

        # Create the strings for the columns using the names of the enums:
        dev: str = await generic.interface
        dtype = title(DeviceType(await generic.device_type))
        state = title(DeviceState(await generic.state))
        connectivity = title(ConnectivityState(await generic.ip4_connectivity))

        name: str = ""
        if await generic.active_connection != "/":  # Connection is active
            # ActiveConnection() gets propertites from active connection path:
            active_conn = ActiveConnection(await generic.active_connection)
            name = await active_conn.id
            if await active_conn.default:
                name += " [primary connection]"

        print(f"{dev:<17} {dtype:<8} {state:<12} {connectivity:<8} {name:<14}")


async def init_catcher(iface):
    print("init catcher")
    nm = NetworkManager()
    devices_paths = await nm.get_devices()

    print("Interface         Type     State        Internet Connection")
    for device_path in devices_paths:
        generic = NetworkDeviceGeneric(device_path)
        dev_name = await generic.interface
        print(dev_name)
        if dev_name == iface:
            print("found you!")
            return generic

        
        
async def stateChangeCatcher(iface):
    print("start catcher")
    dev = await init_catcher(iface)
    async for (new_state, old_state, reason) in dev.state_changed:
        print("toto")
        stateChange(new_state, old_state, reason)



def stateChange(new_state, old_state, reason):
    print("state changed baby!")
    print(str((new_state, old_state, reason)))


async def main():
    await asyncio.gather(
    stateChangeCatcher("wlp0s20f3"),
    non_blocking_io_1(),
    non_blocking_io_2())


nm = NetworkManager()




#asyncio.run(list_active_hardware_networkdevice_states(args.only_hw))
sdbus.set_default_bus(sdbus.sd_bus_open_system())
#asyncio.run(list_active_hardware_networkdevice_states(True))
#asyncio.run(stateChangeCatcher("wlp0s20f3"))
print("let's go!")
asyncio.run(main())
