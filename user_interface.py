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

# Global variables
email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+') # borrowed from somewhere on Github . . . 
terminal_width = get_terminal_size().columns
authenticated = False

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
            tile_list = asyncio.run(getPyTilesFromAccount(user_email, user_password))
            global authenticated
            authenticated = True
            return tile_list
        except InvalidAuthError as err:
            print("Invalid Authentication")

def user_interface():
        tile_choice = 'x'
        while(tile_choice != 'e'):
            print("Would you like to connect to one of your Tiles or would you like to see all the Tile's in the area?")
            tile_choice = input("Type 'm' for a listing of all your Tiles or 'a' for a listing of all the Tiles in the area: ")
            tile_choice = tile_choice.lower()
            valid_tile_choice = ('m', 'a')
            while(tile_choice not in valid_tile_choice):
                tile_choice= input(f"{tile_choice} is not a valid option, please type either m or a: ")
                
            if(tile_choice == 'm'):
                if not authenticated:
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
                # Ask what to do with Tile
                action_chosen = input("For the selected Tile please type 'r' to ring the Tile, 'f' to perform a firmware update, or 't' to list all the Tile's info: ")
                action_chosen = action_chosen.lower()
                valid_actions = ('r', 'f', 't')
                while(action_chosen not in valid_actions):
                    action_chosen = input(f"{action_chosen} is not a valid option, please type either r or f or t: ")

                # List device info about the Tile
                if(action_chosen == 't'):
                    print("Here is the information from the Tile server for the selected Tile")
                    print(f"{tile_selected.name}'s hardware version: {tile_selected.hardware_version}")
                    print(f"{tile_selected.name}'s firmware version: {tile_selected.firmware_version}")
                    print(f"{tile_selected.name}'s ID: {tile_selected.uuid}")
                    print(f"{tile_selected.name}'s authkey: {tile_selected.auth_key}")
                    print(f"{tile_selected.name}'s last known latitude and longitude: {tile_selected.latitude}, {tile_selected.longitude}")

                    # Ask if the user wants to do something else)
                    action_chosen2 = input("Would you like to exit (e) or do something else (d)?")
                    action_chosen2 = action_chosen2.lower()
                    valid_actions2 = ('d', 'e')
                    while(action_chosen2 not in valid_actions2):
                        action_chosen2 = input(f"{action_chosen2} is not a valid option, please type either e or d: ")
                    if(action_chosen2 == 'e'):
                        tile_choice = 'e'

                # Ring the Tile
                elif(action_chosen == 'r'):
                    print("Attempting to connect (please wait)")
                    API_tile = Tile(tile_id, tile_auth)
                    # ring after connect to show success
                    print("Connected")
                    API_tile.ring(Songs.ACTIVE.value, Strength.LOW.value)
                    # Differentiate between the basic songs already loaded the the tps
                    tps_or_loaded = input("Would you like to choose a programmable song or a basic song?\nEnter 'p' for a programmable song and 'b' for basic song: ")
                    tps_or_loaded = tps_or_loaded.lower()
                    tps_or_loaded_valid_options = ('p', 'b')
                    while(tps_or_loaded not in tps_or_loaded_valid_options):
                        tps_or_loaded = input(f"{tps_or_loaded} is not a valid option, please type either 'p' or 'b': ")
                    # default to FIND / custom song
                    song_number_code = Songs.FIND.value

                    # List TPS Songs
                    if(tps_or_loaded == 'p'):
                        for song_num, song in enumerate(Known_Tps):
                            print(f"{song_num+1}. {song.name}")
                        song_number = int(input("Which of these do you want to choose? Input that number: "))
                        # TODO validate
                        song_chosen = [e for e in Known_Tps][song_num - 1]
                        song_chosen_path = song_chosen.value
                        print('Uploading custom song')
                        API_tile.send_custom_song(song_chosen_path)
                        print("Finished uploading custom song")

                    # List basic songs
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
                    action_chosen2 = input("Would you like to exit (e) or do something else (d)?")
                    action_chosen2 = action_chosen2.lower()
                    valid_actions2 = ('d', 'e')
                    while(action_chosen2 not in valid_actions2):
                        action_chosen2 = input(f"{action_chosen2} is not a valid option, please type either e or d: ")
                    if(action_chosen2 == 'e'):
                        API_tile.disconnect()
                        tile_choice = 'e'

                # Firmware update - need to tell the user they can only go up in firmware not down
                elif(action_chosen == 'f'):
                    print("Attempting to connect (please wait)")
                    API_tile = Tile(tile_id, tile_auth)
                    # ring after connect to show success
                    print("Connected")
                    API_tile.ring(Songs.ACTIVE.value, Strength.LOW.value)
                    # need to list all the possible firmwares to choose from
                    print("Possible firmware versions to choose from are these: ")
                    mypath = "./tile_firmwares"

                    # Lists all the Tiles in the area
                    onlyfiles = sorted([f for f in listdir(mypath) if isfile(join(mypath, f))])
                    for firmware_num, b in enumerate(onlyfiles):
                        print(f"{firmware_num + 1}. {b}")
                        
                    firmware_selection = int(input("Which of these do you want to choose? Input that number: "))

                    # TODO validate
                    firmware_filename = onlyfiles[firmware_selection - 1]

                    firmware_version = firmware_filename[firmware_filename.rfind("_")+1:-4]

                    API_tile.send_firmware_update(f"{mypath}/{firmware_filename}", firmware_version)

                    # Ask if the user wants to do something else
                    action_chosen2 = input("Would you like to exit (e) or do something else (d)?")
                    action_chosen2 = action_chosen2.lower()
                    valid_actions2 = ('d', 'e')
                    while(action_chosen2 not in valid_actions2):
                        action_chosen2 = input(f"{action_chosen2} is not a valid option, please type either e or d: ")
                    if(action_chosen2 == 'e'):
                        API_tile.disconnect()
                        tile_choice = 'e'
            
            # if selected to see all the tiles in the area
            if(tile_choice =='a'):
                asyncio.run(list_nearby_tiles.run())

                # Ask if the user wants to do something else
                action_chosen2 = input("Would you like to exit (e) or do something else (d)?")
                action_chosen2 = action_chosen2.lower()
                valid_actions2 = ('d', 'e')
                while(action_chosen2 not in valid_actions2):
                    action_chosen2 = input(f"{action_chosen2} is not a valid option, please type either e or d: ")
                if(action_chosen2 == 'e'):
                    tile_choice = 'e'
        credits()

def credits():
    print("reTOAble created by")                                                                            
    print(" _____                _____ _ _               _   _                           ")                           
    print("| __  |_ _ ___ ___   |  _  | | |_ ___ ___ ___| |_| |_                         ")                        
    print("|    -| | | .'|   |  |     | | . |  _| -_|  _|   |  _|                        ")                     
    print("|__|__|_  |__,|_|_|  |__|__|_|___|_| |___|___|_|_|_|                          ")                  
    print("      |___|                                                                   ")               
    print("                                                                              ")            
    print(" _____       _     _ _            _____ _       _             _     _   _   _ ") 
    print("|     |___ _| |___| |_|___ ___   |     | |_ ___|_|___ _ _ ___| |___| |_| |_|_|") 
    print("| | | | .'| . | -_| | |   | -_|  |   --|   | .'| |  _| | | . | | . |  _|  _| |") 
    print("|_|_|_|__,|___|___|_|_|_|_|___|  |_____|_|_|__,|_|_|  \_/|___|_|___|_| |_| |_|") 
    print("                                                                              ") 
    print("                                                                              ") 
    print(" _____ _           _   _          ____  _ _           _                       ") 
    print("|_   _|_|_____ ___| |_| |_ _ _   |    \|_| |_ ___ ___| |_                     ") 
    print("  | | | |     | . |  _|   | | |  |  |  | | . | -_|  _|  _|                    ") 
    print("  |_| |_|_|_|_|___|_| |_|_|_  |  |____/|_|___|___|_| |_|                      ") 
    print("                          |___|                                               ") 
    print("                                                                              ") 
    print(" _____         _              _ _ _ _         _     _   _                     ") 
    print("|_   _|_ _ ___| |_ ___ ___   | | | |_|___ ___|_|___| |_| |_                   ") 
    print("  | | | | |  _| '_| -_|  _|  | | | | |   |  _| | . |   |  _|                  ") 
    print("  |_| |___|___|_,_|___|_|    |_____|_|_|_|_| |_|_  |_|_|_|                    ") 
    print("                                               |___|                          ") 
    print("                                                                              ")         

def main():
    print_banner() 
    user_interface()
    
if __name__ == "__main__":
    main()
