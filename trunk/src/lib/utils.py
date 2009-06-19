#!/usr/bin/env python
# -*- coding: utf-8 -*-

# gmbox, Google music box.
# Copyright (C) 2009, gmbox team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import sys

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
    
def find_image(image_name,basefile=None):
    """Using the iamge_name, search in the common places. Return the path for
    the image or None if the image couldn't be found."""

    # the order is the priority, so keep global paths before local paths
    if not basefile:
        basefile = __file__
    current_dir = os.path.abspath(os.path.dirname(basefile))
    common_paths = [
            os.path.join(current_dir, '..', 'pixbufs'),
            os.path.join(current_dir, '..', '..', 'pixbufs'),
            os.path.join(sys.prefix, 'share', 'gmbox', 'pixbufs')]

    for path in common_paths:
        filename = os.path.join(path, image_name)
        if os.access(filename, os.F_OK):
            return filename
    return None

def unistr(m):
    '''给re.sub做第二个参数,返回&#nnnnn;对应的中文'''
    return unichr(int(m.group(1)))

def sizeread(size):
    '''传入整数,传出B/KB/MB'''
    #FIXME:这个有现成的函数没?
    if size>1024*1024:
        return '%0.2fMB' % (float(size)/1024/1024)
    elif size>1024:
        return '%0.2fKB' % (float(size)/1024)
    else:
        return '%dB' % size

def deal_input(str):
    if os.name=='nt':
        return str.decode('GBK')
    else:
        return str.decode('UTF-8')
