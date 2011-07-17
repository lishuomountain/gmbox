#!/usr/bin/env python
# -*- coding: utf-8 -*-

# copy this file to gmbox/setup.py, then run
# python setup.py py2exe
# archive the output gmbox-win folder

from distutils.core import setup
import py2exe

setup(
    name = 'gmbox-gtk',
    description = 'Google Music Box GTK',
    version = '0.4',
    windows = [
        {
            'script':'gmbox-gtk.py',
            'icon_resources':[(1, 'data/pixbufs/gmbox.ico')],
        }
    ],
    options = {
        'py2exe': {
            'packages' : 'encodings',
            'includes' : 'cairo, pango, pangocairo, atk, gobject, gio',
            'dist_dir' : 'dist',
        }
    },
    data_files=[
        ('data', [
            'data/glade/gmbox.glade',
            'data/pixbufs/directory.png',
            'data/pixbufs/gmbox.ico',
            'data/pixbufs/info.png',
            'data/pixbufs/songlist.png',
            'data/pixbufs/error.png',
            'data/pixbufs/gmbox.png',
            'data/pixbufs/refresh.png',
            'data/pixbufs/song.png'
        ])
    ]
)
