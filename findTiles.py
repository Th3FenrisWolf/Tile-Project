import asyncio
from asyncio.windows_events import NULL
from bleak import BleakScanner

async def main():
    #devices = await BleakScanner.discover()
    count = 0
    tileUUID = "0000feed-0000-1000-8000-00805f9b34fb"
    async with BleakScanner() as scanner:
        await asyncio.sleep(30.0)
        for d in scanner.discovered_devices:
            #get rid of anything windows or apple
            if str(d)[19]!='W' and str(d)[19]!='A' and str(d.metadata)!=NULL and str(d)[19]=='U':
                print("NAME: ", d.name, " ADDRESS: ", d.address, " METADATA: ", d.metadata)
                count = count + 1

#    for d in devices:
#        # if for d at position 19 it's "U or T" then print it out
#        #print(str(d))
#        if str(d)[19]=='U':
#            print("UNKNOWN HERE: ", d)
#        count = count + 1
    print("Number of unknown (Tiles?) is ", count) 

asyncio.run(main())