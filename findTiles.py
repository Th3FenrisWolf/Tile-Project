import asyncio
from bleak import BleakScanner
import sys

# usage:
# python3 findTiles.py [address] [search time]
# 
# This script discovers and prints all nearby Tile Devices.

addr_list = []
search_addr = None
tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"

def detection_callback(device, advertisement_data):
    # Whenever a device is found...
    global search_addr
    global addr_list
    global tileUUID
    if tileUUID in device.metadata["uuids"]:
        # we found a tile
        if search_addr == None:
            # if not searching for any particular tile:
            if device.address not in addr_list:
                # document only unique instances
                addr_list.append(device.address)
                print("NAME:", device.name, " ADDRESS:", device.address, " RSSI:", device.rssi, advertisement_data)
        elif device.address == search_addr:
            print("Tile of interest found!")
            print("NAME:", device.name, " ADDRESS:", device.address, " RSSI:", device.rssi, advertisement_data)
            # since we found what we're looking for, exit
            sys.exit(0)

async def main(addr = None, time = 30.0):
    args = sys.argv[1:]
    global search_addr
    if len(args) == 0:
        print("Searching for all Tiles for", time, "seconds...")
    elif len(args) == 1:
        addr = args[0]
        search_addr = addr
        print("Searching for Tile w/ address", search_addr, "for", time, "seconds...")
    elif len(args) == 2:
        addr = args[0]
        search_addr = addr
        time = float(args[1])
        print("Searching for Tile w/ address", search_addr, "for", time, "seconds...")    
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(time)
    await scanner.stop()

asyncio.run(main())