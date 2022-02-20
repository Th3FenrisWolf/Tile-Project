#need to basically make an object for each of the songs with the name, a number for accessability, and the link to access the song in ring or wherever it's needed

#this is for reading in the link
#import os
#probably can depricate

#class Song:
#
#    def __init__ (self, num, name, link):
#        self.name = name
#        self.num = num
#        self.link = link
#
#    def print_song_name (song):
#        print("Chosen song name: " + song.name)
#
#tps_als = Song(1, "Auld Lang Syne", "./auld_lang_syne.tsong")
#tps_als = Song(2, "Blues for Slim", "./dutch_904.tsong")
#tps_als = Song(3, "County Fair", "./county_fair.tsong")
#tps_als = Song(4, "Classic Call", "./dutch_.tsong")
#
#Song.print_song_name(tps_als)

from enum import Enum

class Known_Tps(Enum):
    auld_lang_syne =    "/auld_lang_syne.tsong"
    #blues_for_slim =   "/blues_for_slim.tsong"
    county_fair =       "/county_fair.tsong"
    #dutch_904 =        "/dutch_904.tsong"
    blues_for_slim =    "/dutch_904.tsong"
    #dutch_1003 =       "/dutch_1003.tsong"
    the_classic_call =  "/dutch_1003.tsong"
    jingle_bells =      "/jingle_bells.tsong"
    jumping_beans =     "/jumping_beans.tsong"
    skipping_stones =   "/skipping_stones.tsong"
    #the_classic_call = "/the_classic_call.tsong"
    to_and_fro =        "/to_and_fro.tsong"
    
    