import os, sys, time, random, re, asyncio, getpass
from sqlite3 import connect
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'pytile/pytile'))
from api import async_login
from pwinput import pwinput
from aiohttp import ClientSession
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'tile_api/commands'))
from song import Songs
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'scripts'))
from known_tps import Known_Tps_two

# variables
user_email = ""
user_password = ""
regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+') # borrowed from somewhere on Github . . . 
user_email_valid = False
myTiles = False                 # set to true when the user wants to see their tiles, false when they want to see all tiles
tile_cmd = ""                   # set to r, t, or f, no longer than one character long
tile_cmd_valid = False          # set to true when it is just f, t, or r and nothing else
tile_choice = ""                # set to m for my tiles or a or all tiles
tile_choice_valid = False       # verifies that it's what it's supposed to be
tile_selected = 0
action_chosen = ""              # this is what will hold r, f, or t
action_chosen_valid = False     # will be changed to true when verified as true
song_chosen = ""
song_number = 0
song_number_chosen = False      # not actually implemented currently but will eventually
song_volume = 0
song_volume_valid = False       # not actually impleneted currently but will eventually

# functions
def slow_type(t):
    typing_speed = 80 #wpm
    for l in t:
        sys.stdout.write(l)
        sys.stdout.flush()
        time.sleep(random.random()*10.0/typing_speed)
    print('')
    time.sleep(1)

# need to make it tell if your tile password or email are wrong and ask them to re-input it all, might need to make username and password input a function
async def connectToTileAccount() -> None:
    """Run!"""
    async with ClientSession() as session:
        api = await async_login(user_email, user_password, session)
        print("Successfully connected to Tile account")
        tiles = await api.async_get_tiles()
        return tiles

# Step 1. Have a little intro/explanation for this user interface and what it's for, how it'll work
print("_"*140+"\n")
print("\tHello! Welcome to the (reTOAblepy or reTOAble or reTOApy or something like that) API which is used to control a a Tile Tracker.")
print("_"*140+"\n")

# Step 2. Ask the user for their Tile account's email and password -- store in variables, need to verify that email is ok format
user_email = input("Please input the email that is associated with your Tile account: ")
print("Verifying your email, just a moment . . . ")
while(not (re.fullmatch(regex, user_email))):
    user_email = input("Sorry, not a valid format, please input the email that is associated with your Tile account: ")
user_password = pwinput("Please input the password that is associated with your Tile account: ")
#user_password = input("Please input the password that is associated with your Tile account: ")

# Step 3. Done in background - connect with pyTile to the users account - get auth key here
# Can connect to pyTile and can get all kinds of info (mac address) being important but still not the auth key even though it should be stored somewhere and should be able to access it somewhere. So also need to see if I can access the tile id here, that would be majorly helpful
tile_list = asyncio.run(connectToTileAccount())

# Step 4. Ask user if they would like to see a listing of all their Tiles or of all the available Tiles in the area ("m" for my Tiles, "a" for all in area)

print("Would you like to connect to one of your Tiles or would you like to see all the Tile's in the area?")
tile_choice = input("Type 'm' for a listing of all your Tiles or 'a' for a listing of all the Tiles in the area: ")
if(tile_choice.lower() == 'm' or tile_choice.lower() == 'a'):
    tile_choice_valid = True
while(not tile_choice_valid):
    tile_choice= input(f"{tile_choice} is not a valid option, please type either m or a: ")
    if(tile_choice.lower()=='m' or tile_choice.lower() == 'a'):
        tile_choice_valid = True

# Step 5. If their Tiles, list all of the ones that are connected to their Tile account - can do ring, firmware update, or TDI for any of the Tiles in their account
#         If all the Tiles in the area -- can do TDI for any of them

tile_list_num = 1
#tile_list = None

# if selected to see all their tiles
if(tile_choice == 'm' and tile_choice_valid == True):
    print(f"Tiles connected to account are: ") 
    #tile_list = asyncio.run(connectToTileAccount())
    #print(tile_list)
    #print(f"test type is {type(tile_list)}")
    for tile_uuid, tile in tile_list.items():
        if tile.kind == "TILE":
            print(f"{tile_list_num}. {tile.name}")
            tile_list_num+=1

    # Step 6.m Have the Tiles listed with a number and the name (if there), mac address, and Tile ID, have the user input a number (such as "1" for the first in the list) to select which one they want to choose
    tile_selected = int(input("\nSelect which one you would like by typing it numerically: "))
    print(list(tile_list.values())[tile_selected-1])
    tile_list = list(tile_list.values())
    tile_mac = tile_list[tile_selected -1].uuid
    print(f"Tile's mac: {tile_mac}")
    tile_auth = tile_list[tile_selected -1].auth_key
    print(f"Tile's authkey: {tile_auth}")

    # Step 7.m If their Tiles - ask if they'd like to ring, do a firmware update, or tdi for their selected Tile ("r" for ring, "f" for firmware update, "t" for tdi)
    action_chosen = input("For the selected Tile please type 'r' to ring the Tile, 'f' to perform a firmware update, or 't' to list all the Tile's info: ")
    if(action_chosen.lower() == 'r' or action_chosen.lower() == 'f' or action_chosen.lower() == 't'):
        action_chosen_valid = True
    while(not action_chosen_valid):
        action_chosen = input(f"{action_chosen} is not a valid option, please type either r or f or t: ")
        if(action_chosen.lower() == 'r' or action_chosen.lower() == 'f' or action_chosen.lower() == 't'):
            action_chosen_valid = True

#   Step ring. List all the songs enumerated (both tps and songs preloaded on tile) -- and have the user choose one (like doing "3" for the third in the list)
#       List the possible volumes (low, medium, high aka 1,2,3) and have the user input which one they would like to choose (like doing "2" for medium volume)
#       Call the ring function with the tile id, auth key (need to get in this step), selected song, and selected volume
#       After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4
    if(action_chosen.lower() == 'r' and action_chosen_valid):
        # need to differentiate between the basic songs already loaded the the tps
        tps_or_loaded = input("Would you like to choose a programmable song or a basic song?\nEnter 'p' for a programmable song and 'b' for basic song: ")
        tps_or_loaded_valid = False
        if(tps_or_loaded.lower() == 'p' or tps_or_loaded.lower() == 'b'):
            tps_or_loaded_valid = True
        while(not tps_or_loaded_valid):
            tps_or_loaded = input(f"{tps_or_loaded} is not a valid option, please type either 'p' or 'b': ")
            if(tps_or_loaded.lower() == 'p' or tps_or_loaded.lower() == 'b'):
                tps_or_loaded_valid = True
        
        # tps songs listed and one chosen
        if(tps_or_loaded == 'p' and tps_or_loaded_valid):
            # go to scripts/known_tps.py and print out the names enumerated
            for song_num, song in enumerate(Known_Tps_two):
                print(f"{song_num+1}. {song.name}")
            song_number = int(input("Which of these do you want to choose? Input that number: "))
            print(f"Song_number type is: {type(song_number)}")
            song_chosen = Known_Tps_two(song_number)
            print(f"Song chosen: {song_chosen.name}")

        # basic songs listed and one chosen
        if(tps_or_loaded == 'b' and tps_or_loaded_valid):
            # go to tile_api/commands/song.py and list the songs enumerated
            for song_num, song in enumerate(Songs):
                print(f"{song_num+1}. {song.name}")
            song_number = int(input("Which of these do you want to choose? Input that number: "))
            #not working
            songs = list(Songs.values())
            song_chosen = songs[song_number-1]
            print(f"Song chosen: {song_chosen.name}")

        #input the volume of whichever song needs to be played
        song_volume = input("What volume would you like to play the song? Enter 1 for low, 2 for medium, and 3 for high: ")
        #validate that it's 1, 2, or 3

        #call ring

    # end of ring stuff 

    dummy = input("   ")

#   Step firmware. List all the firmware versions enumerated -- and have the user choose one
#       Call the tofu function with the tile id, auth key (need to get in this step), and selected firmware
#       After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

    if(action_chosen.lower() == 'f' and action_chosen_valid):
        # need to list all the possible firmwares to choose from
        print("Possible firmware versions to choose from are these: ")

#    Step tdi. List all tdi info
#       After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

    if(action_chosen.lower() == 't' and action_chosen_valid):
        # just run tdi on the selected tile
        print("Possible songs to choose from are these: ")


# if selected to see all the tiles in the area
if(tile_choice =='a' and tile_choice_valid == True):
    # need to call findTiles here - but an abbreviated version of the script
    print("need to call findTiles")

# Step 6.a Have the Tiles listed with a number and the name (if there), mac address, and Tile ID, have the user input a number (such as "1" for the first in the list) to select which one they want to choose

# Step tdi. List all tdi info
#           After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

# Step exit. Cleanly disconnect from the tile, call disconnect, clear all the variables - especially the password one for safety

# Step dependancy script: create a dependancy script -- need to run a pip install bleak and pip install pwinput and pip install aiohttp

#random stuff
#printing out tps
        #absolute_path = os.path.abspath(__file__)
        #file_directory = os.path.dirname(absolute_path)
        #song_val = tps.Known_Tps(3)
#
        #my_path = os.path.join(file_directory, "Tile Programmable Songs (TPS)", song_val)
        #print(my_path)