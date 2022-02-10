import asyncio
from pickle import TRUE
from bleak import BleakScanner
from enum import Enum
import sys

# usage:
# python3 discover.py [search time] [address]
# 
# This script discovers and prints all nearby Bluetooth devices.

devices_found = 0
addr_list = []
search_addr = None

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
    global addr_list
    global devices_found
    if search_addr == None:
        # if not searching for particular address
        if device.address not in addr_list:
            # find and document only unique instances
            devices_found += 1
            addr_list.append(device.address)
            print_device_data(device, advertisement_data)
    elif device.address == search_addr:
        # if we found the device we're looking for
        print("Search Device Found!")
        print_device_data(device, advertisement_data)
        # since we found what we're looking for, exit
        sys.exit(0)
    else:
        # if we found a device, but it wasn't the one we are looking for
        # just to show the user that the script is working
        if device.address not in addr_list:
            devices_found += 1
            print("Found a device (", devices_found, ")")

async def main(time = 60.0, addr = None):
    global devices_found
    args = sys.argv[1:]
    if len(args) == 0:
        print("Searching for all BT devices for", time, "seconds...")
    elif len(args) == 1:
        time = float(args[0])
        print("Searching for all BT devices for", time, "seconds...")
    elif len(args) == 2:
        time = float(args[0])
        addr = str(args[1])
        global search_addr
        search_addr = addr
        print("Searching for address", search_addr, "for", time, "seconds...")
    # Start the scanner and listen for callbacks
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(time)
    await scanner.stop()
    print("Total BT devices found:", str(devices_found))

asyncio.run(main())
