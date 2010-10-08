#!/usr/bin/env python
# -*- coding: utf-8 -*-

# run:
# python cx_freeze.py

from cx_Freeze import main
import sys
import os
import shutil

cmd = '''
    cxfreeze 
    mainwin.py 
    --target-dir gmbox-win 
    --target-name gmbox.exe 
    --icon pixbufs\gmbox.ico 
'''
sys.argv = cmd.split()
main()

data_files = [
    'gmbox.glade',
    'PLUGININFO',
    'pixbufs',
    'pixbufs/gmbox.ico',
    'pixbufs/gmbox.png',
    'pixbufs/track.png',
    'pixbufs/album.png',
    'pixbufs/refresh.png',
    'pixbufs/listing.png',
    'pixbufs/missing.png'
]
dist_folder = "gmbox-win"
if os.path.exists(dist_folder):
    for file in data_files:   
        dst = os.path.join(os.path.abspath(dist_folder), file)
        print "copying %s -> %s" % (file, dst)
        if os.path.isfile(file):
            shutil.copyfile(file, dst)
        elif os.path.isdir(file):
            shutil.copytree(file, dst)
