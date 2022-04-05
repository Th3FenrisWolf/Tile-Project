import os, sys, time, random, re, asyncio, getpass
from shutil import get_terminal_size

from tile_api.commands.song import Strength

from pwinput import pwinput
from aiohttp import ClientSession

sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'pytile/pytile'))
from api import async_login
from errors import *
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'tile_api/commands'))
from song import Songs, Strength
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'scripts'))
from known_tps import Known_Tps
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'tile_firmwares/common_ones'))
from os import listdir
from os.path import isfile, join
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'tile_api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'discover_scripts'))
from discover_scripts import list_nearby_tiles
from tile import Tile

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+') # borrowed from somewhere on Github . . . 
terminal_width = get_terminal_size().columns

# Pretty Print
def slow_type(t):
    typing_speed = 80 #wpm
    for l in t:
        sys.stdout.write(l)
        sys.stdout.flush()
        time.sleep(random.random()*10.0/typing_speed)
    print('')
    time.sleep(1)

# Performs PyTile HTTP call to fetch data from Tile's servers
async def getPyTilesFromAccount(user_email, user_password) -> None:
    async with ClientSession() as session:
        api = await async_login(user_email, user_password, session)
        print("Successfully connected to Tile account")
        tiles = await api.async_get_tiles()
        return tiles

def print_banner():
    print("_" * terminal_width + "\n")
    print("        _____ _____  ___  _     _      ")
    print("       |_   _|  _  |/ _ \| |   | |     ")
    print(" _ __ ___| | | | | / /_\ \ |__ | | ___ ")
    print("| '__/ _ \ | | | | |  _  | '_ \| |/ _ \\")
    print("| | |  __/ | \ \_/ / | | | |_) | |  __/")
    print("|_|  \___\_/  \___/\_| |_/_.__/|_|\___|\n")
    print("An API control your Tile Trackers.")
    print("_" * terminal_width + "\n")

def getPyTiles():
   # Loop Until Valid Authentication
    while True:
        # Get Login and Verify
        user_email = input("Please input the email that is associated with your Tile account: ")
        # Check Email Format
        while(not (re.fullmatch(email_regex, user_email))):
            user_email = input("Sorry, not a valid format, please input the email that is associated with your Tile account: ")

        user_password = pwinput("Please input the password that is associated with your Tile account: ")

        # Connect to Account - from Pytile
        try:
            tile_list = asyncio.get_event_loop().run_until_complete(getPyTilesFromAccount(user_email, user_password))
            return tile_list
        except InvalidAuthError as err:
            print("Invalid Authentication")

def main():
    print_banner()

    # Ask User What to Do ("m" for my Tiles, "a" for all in area)
    print("Would you like to connect to one of your Tiles or would you like to see all the Tile's in the area?")
    tile_choice = input("Type 'm' for a listing of all your Tiles or 'a' for a listing of all the Tiles in the area: ")
    tile_choice = tile_choice.lower()
    valid_tile_choice = ('m', 'a')
    while(tile_choice not in valid_tile_choice):
        tile_choice= input(f"{tile_choice} is not a valid option, please type either m or a: ")

    # If their Tiles, list all of the ones that are connected to their Tile account - can do ring, firmware update, or TDI for any of the Tiles in their account
    # If all the Tiles in the area -- can do TDI for any of them

    # if selected to see all their tiles
    if(tile_choice == 'm'):
        tile_list = getPyTiles()

        print(f"Tiles connected to account are: ") 
        for tile_index, tile in enumerate(tile_list.values()):
            if tile.kind == "TILE":
                print(f"{tile_index + 1}. {tile.name}")

        # Have the Tiles listed with a number and the name (if there), mac address, and Tile ID,
        # have the user input a number (such as "1" for the first in the list)
        # to select which one they want to choose
        num_selected = int(input("\nSelect which one you would like by typing it numerically: "))
        # TODO validate this number is in range
        tile_selected = list(tile_list.values())[num_selected - 1]
        tile_id = tile_selected.uuid
        tile_auth = tile_selected.auth_key

        # attempt to connect to this tile
        

        # Step 7.m If their Tiles - ask if they'd like to ring, do a firmware update, or tdi for their selected Tile ("r" for ring, "f" for firmware update, "t" for tdi)
        action_chosen = input("For the selected Tile please type 'r' to ring the Tile, 'f' to perform a firmware update, or 't' to list all the Tile's info: ")
        action_chosen = action_chosen.lower()
        valid_actions = ('r', 'f', 't')
        while(action_chosen not in valid_actions):
            action_chosen = input(f"{action_chosen} is not a valid option, please type either r or f or t: ")

        if(action_chosen == 't'):
            # just run tdi on the selected tile
            print("Here is the information from the Tile server for the selected Tile")
            
            # TODO access the tile here
            print(f"{tile_selected.name}'s hardware version: {tile_selected.hardware_version}")
            print(f"{tile_selected.name}'s firmware version: {tile_selected.firmware_version}")
            print(f"{tile_selected.name}'s ID: {tile_selected.uuid}")
            print(f"{tile_selected.name}'s authkey: {tile_selected.auth_key}")
            print(f"{tile_selected.name}'s last known latitude and longitude: {tile_selected.latitude}, {tile_selected.longitude}")

        elif(action_chosen == 'r'):
            print("Attempting to connect (please wait)")
            API_tile = Tile(tile_id, tile_auth)
            # ring after connect to show success
            print("Connected")
            API_tile.ring(Songs.ACTIVE.value, Strength.LOW.value)
            # need to differentiate between the basic songs already loaded the the tps
            tps_or_loaded = input("Would you like to choose a programmable song or a basic song?\nEnter 'p' for a programmable song and 'b' for basic song: ")
            tps_or_loaded = tps_or_loaded.lower()
            tps_or_loaded_valid_options = ('p', 'b')
            while(tps_or_loaded not in tps_or_loaded_valid_options):
                tps_or_loaded = input(f"{tps_or_loaded} is not a valid option, please type either 'p' or 'b': ")
            
            # default to FIND / custom song
            song_number_code = Songs.FIND.value

            # tps songs listed and one chosen
            if(tps_or_loaded == 'p'):
                # go to scripts/known_tps.py and print out the names enumerated
                for song_num, song in enumerate(Known_Tps):
                    print(f"{song_num+1}. {song.name}")
                song_number = int(input("Which of these do you want to choose? Input that number: "))
                # TODO validate
                song_chosen = [e for e in Known_Tps][song_num - 1]
                song_chosen_path = song_chosen.value
                print('Uploading custom song')
                API_tile.send_custom_song(song_chosen_path)
                print("Finished uploading custom song")

            # basic songs listed and one chosen
            elif(tps_or_loaded == 'b'):
                # go to tile_api/commands/song.py and list the songs enumerated
                for song_num, song in enumerate(Songs):
                    print(f"{song_num+1}. {song.name}")
                song_number = int(input("Which of these do you want to choose? Input that number: "))
                # TODO validate
                song_chosen = [e for e in Songs][song_number - 1]
                song_number_code = song_chosen.value

            #input the volume of whichever song needs to be played
            song_volume = int(input("What volume would you like to play the song? Enter 1 for low, 2 for medium, and 3 for high: "))

            #validate that it's 1, 2, or 3
            while(song_volume not in range(1, 4)):
                song_volume = int(input(f"{song_volume} is not a valid option, please enter 1 for low, 2 for medium, and 3 for high: "))

    
            # call ring fuction which is in tile.py and might need to change that slightly
            print(f"Playing {song_chosen.name}")
            API_tile.ring(song_number_code, song_volume.to_bytes(1, "little"))
            API_tile.disconnect()

        elif(action_chosen == 'f'):
            print("Attempting to connect (please wait)")
            API_tile = Tile(tile_id, tile_auth)
            # ring after connect to show success
            print("Connected")
            API_tile.ring(Songs.ACTIVE.value, Strength.LOW.value)
            # need to list all the possible firmwares to choose from
            print("Possible firmware versions to choose from are these: ")
            mypath = "./tile_firmwares"
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            firmware_num = 1
            for b in onlyfiles:
                print(f"{firmware_num}. {b}")
                firmware_num+=1
            API_tile.disconnect()
    
    # if selected to see all the tiles in the area
    if(tile_choice =='a'):
        # need to call findTiles here - but an abbreviated version of the script
        asyncio.run(list_nearby_tiles.run())

    # Step 6.a Have the Tiles listed with a number and the name (if there), mac address, and Tile ID, have the user input a number (such as "1" for the first in the list) to select which one they want to choose

    # Step tdi. List all tdi info
    #           After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

    # Step exit. Cleanly disconnect from the tile, call disconnect
    
if __name__ == "__main__":
    main()