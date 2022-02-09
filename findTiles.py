import asyncio
from bleak import BleakScanner
import sys

# usage:
# python3 findTiles.py [search time] [address]
# 
# This script discovers and prints all nearby Tile Devices.

madelines_earbuds = "12:34:56:00:33:E1"
madelines_earbuds2 = "12:34:56:00:37:1D"

deviceNames = ["Spare key", "wallet", "backpack", "toy"]
deviceAddresses = ["E6:9E:55:1A:91:28", "DF:30:61:4F:AB:DA", "E1:5B:A3:01:A0:F1", "D1:7F:8E:E6:9E:B1"]

exclude_list_addrs = [madelines_earbuds, madelines_earbuds2]
found_addr_list = []
search_addr = None
tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"

def detection_callback(device, advertisement_data):
    # Whenever a device is found...
    global search_addr
    global found_addr_list
    global tileUUID
    global exclude_list_addrs
    global deviceNames
    global deviceAddresses
    if tileUUID in device.metadata["uuids"]:
        # we found a tile
        if search_addr == None:
            # if not searching for any particular tile:
            # exclude devices we don't want to appear
            if device.address not in found_addr_list:
                # document only unique instances
                found_addr_list.append(device.address)
                # note whether device found was excluded, etc.
                if device.address in exclude_list_addrs:
                    print("excluded device found", "(", device.name, ")")
                elif device.address in deviceAddresses:
                    i = deviceAddresses.index(device.address)
                    print("Found device --<<", str(deviceNames[i]), ">>-- (Address:", device.address, ")")
                else:
                    print("NAME:", device.name, " ADDRESS:", device.address, " RSSI:", device.rssi, advertisement_data)
        elif device.address == search_addr:
            print("Tile of interest found!")
            print("NAME:", device.name, " ADDRESS:", device.address, " RSSI:", device.rssi, advertisement_data)
            # since we found what we're looking for, exit
            sys.exit(0)

async def main(addr = None, time = 60.0):
    args = sys.argv[1:]
    global search_addr
    if len(args) == 0:
        print("Searching for all Tile devices for", time, "seconds...")
    elif len(args) == 1:
        time = float(args[0])
        print("Searching for all Tile devices for", time, "seconds...")
    elif len(args) == 2:
        time = float(args[0])
        addr = str(args[1])
        search_addr = addr
        print("Searching for Tile w/ address", search_addr, "for", time, "seconds...")    
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(time)
    await scanner.stop()

asyncio.run(main())