#!/usr/bin/env python
# -*- coding: utf-8 -*-

# run:
# python py2exe.py py2exe

from distutils.core import setup
import py2exe

setup(
    name = 'gmbox',
    description = 'Google music box',
    version = '0.4',
    windows = [
        {
            'script':'gmbox.py',
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
        ('pixbufs',[
            'pixbufs/directory.png',
            'pixbufs/gmbox.ico',
            'pixbufs/info.png',
            'pixbufs/songlist.png',
            'pixbufs/error.png',
            'pixbufs/gmbox.png',
            'pixbufs/refresh.png',
            'pixbufs/song.png'])
        ]
)