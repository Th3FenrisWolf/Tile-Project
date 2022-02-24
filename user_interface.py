import os, sys, time, random, re, asyncio, getpass
from sqlite3 import connect
from tile_programmable_songs import tps
from pytile import async_login
from pwinput import pwinput
from aiohttp import ClientSession

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

# functions
def slow_type(t):
    typing_speed = 80 #wpm
    for l in t:
        sys.stdout.write(l)
        sys.stdout.flush()
        time.sleep(random.random()*10.0/typing_speed)
    print('')
    time.sleep(1)

async def connectToTileAccount() -> None:
    """Run!"""
    async with ClientSession() as session:
        api = await async_login(user_email, user_password, session)
        slow_type("Successfully connected to Tile account")
        tiles = await api.async_get_tiles()

        count = 0
        for tile_uuid, tile in tiles.items():
            pass
            #print(f"The Tile's name is {tile.name}")
            #user_tiles[count] = tile_obj(tile.name, tile.uuid, tile.firmware_version)
            #count+=1
        #print(help(tile))   
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
    tile_list = asyncio.run(connectToTileAccount())
    #print(tile_list)
    #print(f"test type is {type(tile_list)}")
    for tile_uuid, tile in tile_list.items():
        if tile.kind == "TILE":
            print(f"{tile_list_num}. {tile.name}")
            tile_list_num+=1

    # Step 6.m Have the Tiles listed with a number and the name (if there), mac address, and Tile ID, have the user input a number (such as "1" for the first in the list) to select which one they want to choose
    tile_selected = int(input("\nSelect which one you would like by typing it numerically: "))
    print(list(tile_list.values())[tile_selected-1])

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
        #need to list all the possible songs
        print("Possible songs to choose from are these: ")

#   Step firmware. List all the firmware versions enumerated -- and have the user choose one
#                Call the tofu function with the tile id, auth key (need to get in this step), and selected firmware
#                After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

# Step tdi. List all tdi info
#           After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

# if selected to see all the tiles in the area
# if(tile_choice =='a' and tile_choice_valid == True):
    # need to call findTiles here - but an abbreviated version of the script

# Step 6.a Have the Tiles listed with a number and the name (if there), mac address, and Tile ID, have the user input a number (such as "1" for the first in the list) to select which one they want to choose

# Step tdi. List all tdi info
#           After it's done, ask if they would like to exit or restart - if exit then cleanly disconnect and clear all the variables, if restart go back to step 4

# Step exit. Cleanly disconnect from the tile, call disconnect, clear all the variables

# Step dependancy script: create a dependancy script -- need to run a pip install bleak and pip install pytile and pip install pwinput

#random stuff
#printing out tps
        #absolute_path = os.path.abspath(__file__)
        #file_directory = os.path.dirname(absolute_path)
        #song_val = tps.Known_Tps(3)
#
        #my_path = os.path.join(file_directory, "Tile Programmable Songs (TPS)", song_val)
        #print(my_path)