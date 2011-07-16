#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = '''打印调试函数'''

def print_song(song):
    '''打印Song类实例信息

    注意：
    在测试Songlist或者Directory类时，
    你可以注释：
    song.load_detail()
    song.load_streaming()
    以免发出过多的http请求。
    '''

    song.load_detail()
    song.load_streaming()

    for name in dir(song):
        if type(getattr(song, name)) == unicode:
            print "%s: %s" % (name , getattr(song, name))
    print

def print_songlist(songlist):
    '''打印Songlist类实例信息

    注意：
    在测试Songlist或者Directory类时，
    你可以注释：
    print_song(song)
    以免发出过多的http请求。
    '''

    for name in dir(songlist):
        if type(getattr(songlist, name)) == unicode:
            print "%s: %s" % (name , getattr(songlist, name))

    for song in songlist.songs:
        print_song(song)
    print

def print_directory(directory):
    '''打印Directory类实例信息

    注意：
    在测试Songlist或者Directory类时，
    你可以注释
    songlist.load_songs()
    以免发出过多的http请求。
    '''

    for songlist in directory.songlists:
        songlist.load_songs()
        print_songlist(songlist)
