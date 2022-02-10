import asyncio
from bleak import BleakScanner
from enum import Enum
import sys

# usage:
# python3 findTiles.py [search time] [address]
# 
# This script discovers and prints all nearby Tile Devices.

known_device_names = ["Spare key", "wallet", "backpack", "toy"]
known_device_addresses = ["E6:9E:55:1A:91:28", "DF:30:61:4F:AB:DA", "E1:5B:A3:01:A0:F1", "D1:7F:8E:E6:9E:B1"]

madelines_earbuds = "12:34:56:00:33:E1"
madelines_earbuds2 = "12:34:56:00:37:1D"

exclude_list_addrs = [madelines_earbuds, madelines_earbuds2]
found_addr_list = []
search_addr = None
tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"
tiles_found = 0

# Label things true or false depending on what information you want to see:
class Display_Attributes(Enum):
    NAME = True
    ADDRESS = True
    METADATA = False # a lot of redundant information
    RSSI = True
    UUIDS = False
    ADVERTISEMENT_DATA = False

def print_device_data(device, advertisement_data):
    info = ""
    if Display_Attributes.NAME.value == True:
        info += ("Name: " + str(device.name) + " ")
    if Display_Attributes.ADDRESS.value == True:
        info += ("Address: " + str(device.address) + " ")
    if Display_Attributes.RSSI.value == True:
        info += ("RSSI: " + str(device.rssi) + " ")
    if Display_Attributes.METADATA.value == True:
        info += ("Metadata: " + str(device.metadata) + " ")
    if Display_Attributes.UUIDS.value == True:
        info += ("UUID(s): " + str(device.metadata["uuids"]) + " ")
    if Display_Attributes.ADVERTISEMENT_DATA.value == True:
        info += (str(advertisement_data))
    print(info)

def detection_callback(device, advertisement_data):
    # Whenever a device is found...
    global search_addr
    global found_addr_list
    global tileUUID
    global exclude_list_addrs
    global known_device_names
    global known_device_addresses
    global tiles_found
    if tileUUID in device.metadata["uuids"]:
        # we found a tile
        tiles_found += 1
        if search_addr == None:
            # if not searching for any particular tile:
            # exclude devices we don't want to appear
            if device.address not in found_addr_list:
                # document only unique instances
                found_addr_list.append(device.address)
                # if device is excluded...
                if device.address in exclude_list_addrs:
                    print("excluded device found", "(", device.name, ")")
                # if device is known...
                elif device.address in known_device_addresses:
                    i = known_device_addresses.index(device.address)
                    print("Found device --<<", str(known_device_names[i]), ">>--")
                    print_device_data(device, advertisement_data)
                # otherwise just print
                else:
                    print_device_data(device, advertisement_data)
        elif device.address == search_addr:
            print("Tile of interest found!")
            print_device_data(device, advertisement_data)
            # since we found what we're looking for, exit
            sys.exit(0)

async def main(addr = None, time = 60.0):
    args = sys.argv[1:]
    global search_addr
    global tiles_found
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
    print("Tiles found:", str(tiles_found))

asyncio.run(main())