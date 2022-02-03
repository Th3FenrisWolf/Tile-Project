import asyncio
from bleak import BleakScanner
import sys

# usage:
# python3 discover.py [search time] [address]

devices_found = 0
addr_list = []
search_addr = None

def detection_callback(device, advertisement_data):
    global search_addr
    global addr_list
    global devices_found
    if search_addr == None:
        if device.address not in addr_list:
            devices_found += 1
            addr_list.append(device.address)
            print(device)
            #print(device.address, "Name:", device.name, "RSSI:", device.rssi, advertisement_data)
    elif device.address == search_addr:
        print("Search Device Found!")
        print(device)
        #print(device.address, "Name:", device.name, "RSSI:", device.rssi, advertisement_data)
        sys.exit(0)
    else:
        if device.address not in addr_list:
            devices_found += 1
            print("Found a device (", devices_found, ")")

async def main(time = 30.0, addr = None):
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
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(time)
    await scanner.stop()

asyncio.run(main())