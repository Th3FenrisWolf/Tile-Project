#need to basically make an object for each of the songs with the name, a number for accessability, and the link to access the song in ring or wherever it's needed

#this is for reading in the link
#import os

class Song:

    def __init__ (self, num, name, link):
        self.name = name
        self.num = num
        self.link = link

    def print_song_name (song):
        print("Chosen song name: " + song.name)

tps_als = Song(1, "Auld Lang Syne", "agadfsdf")

Song.print_song_name(tps_als)
    