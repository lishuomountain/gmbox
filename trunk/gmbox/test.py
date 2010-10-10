#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core import *

def print_song(song):
    song.load_detail()
    song.load_streaming()

    for name in dir(song):
        if type(getattr(song, name)) == unicode:
            print "%s: %s" % (name , getattr(song, name))
    print

def print_songlist(songlist):
    for name in dir(songlist):
        if type(getattr(songlist, name)) == unicode:
            print "%s: %s" % (name , getattr(songlist, name))
    
    for song in songlist.songs:
        print_song(song)
    print

def print_directory(directory):
    for songlist in directory.songlists:
        #songlist.load_songs()
        print_songlist(songlist)

if __name__ == '__main__':
    
#    print "%s\n" % Song.musicdownload("S5c956b9af4dc56ba")
    print_song(Song("Sb1ee641ab6133e1a"))
    
#    print_songlist(Album("B5f03f5ad567ecbec"))
#    print_songlist(Search("beyond"))
#    print_songlist(Chartlisting("chinese_new_songs_cn"))   
#    print_songlist(Topiclisting("top100_autumn_day"))
#    print_songlist(ArtistSong("A887b2d5bdd631594"))
#    print_songlist(Tag("%E6%82%A0%E6%89%AC"))
#    print_songlist(Screener())
#    print_songlist(Similar("Sb1ee641ab6133e1a"))
#    print_songlist(Starrecc("top100_star_chenyixun"))
#
#    print_directory(DirSearch("海阔天空"))
#    print_directory(DirChartlisting("chinese_new-release_albums_cn"))
#    print_directory(DirTopiclistingdir())
#    print_directory(DirArtist("beyond"))
#    print_directory(DirArtistAlbum("A887b2d5bdd631594"))
#    print_directory(DirTag("%E6%82%A0%E6%89%AC"))
#    print_directory(DirStarrecc())


