#start with asking user what command they want to do, "f" or "F" for firmware update, "r" or "R" for ring

#within tofu, ask which version, version a, b, c, or d and then which tile "s" for spare key, w for wallet, b for backpack, and t for toy
#within ring, ask which song they'd like to play, and how loud and which tile

print("\n\tHello! Welcome to the reTOAble API which is used to control a a Tile Tracker.\n")
print("\tThere are three things you can do: \n\t\t*perform a firmware update -- to do this, input \"f\"\n\t\t*ring the Tile with any of the listed songs you'd like -- input \"r\"\n\t\t*get any and all information about a selected Tile -- input \"t\"\n")

tile_cmd_input = input("\tCommand you would like to execute, input \"f\", \"r\", or \"t\":\t")
tile_cmd = ""
tile_cmd_valid = False
tile_cmd_cnt = 0

while tile_cmd_valid != True:
    if tile_cmd_input.lower() == 'f':
        tile_cmd = "tofu"
        tile_cmd_valid = True
    elif tile_cmd_input.lower() == 'r':
        tile_cmd = "ring"
        tile_cmd_valid = True
    elif tile_cmd_input.lower == 't':
        tile_cmd = "tdi"
        tile_cmd_valid = True
    else:
        if tile_cmd_cnt >= 4:
            print("It appears you are having a hard time, let's do ring!")
            tile_cmd = 'ring'
            break
        print("Sorry, " + tile_cmd_input + " is not a valid command, try again please!")
        tile_cmd_input = input("\tCommand you would like to execute, input \"f\", \"r\", or \"t\":\t")
        tile_cmd_valid = False
        tile_cmd_cnt+=1

#if tile_cmd == "ring":
    #call findTile to find the tiles in the area and put into an object to display then the user can determine which tile they want to ring by inputting it's position/number
    #print out all sounds/TPS and then have the user select which number/position they want to play
    #have the user input how loud they want to play the song, 1, 2, or 3
    #need to change ring to have a function where can input which device, how loud, and what song to connect to