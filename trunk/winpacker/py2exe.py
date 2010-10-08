#!/usr/bin/env python
# -*- coding: utf-8 -*-

# run:
# python py2exe.py py2exe

from distutils.core import setup
import py2exe

setup(
    name = 'gmbox',
    description = 'Google music box',
    version = '0.3.0',
    windows = [
        {
            'script':'mainwin.py',
            'icon_resources':[(1,'pixbufs/gmbox.ico')],
        }
    ],
    options = {
        'py2exe': {
            'packages' : 'encodings',
            'includes' : 'cairo, gio, atk, pangocairo, pango',
            'dist_dir' : 'gmbox-win',
        }
    },
    data_files=[
        'gmbox.glade',
        'PLUGININFO',
        ('pixbufs',[
            'pixbufs/gmbox.ico',
            'pixbufs/gmbox.png',
            'pixbufs/track.png',
            'pixbufs/album.png',
            'pixbufs/refresh.png',
            'pixbufs/listing.png',
            'pixbufs/missing.png'])
        ]
)