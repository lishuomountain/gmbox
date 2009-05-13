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


import re, urllib, urllib2, sys, os, time
from HTMLParser import HTMLParser
import thread
from stat import *

from xml.dom import minidom
import codecs

reload(sys)
sys.setdefaultencoding('utf8')


if os.name=='posix':
    #player="mplayer"
    player="mpg123"
if os.name=='nt':
    player="mpxplay.exe"
    
userhome = os.path.expanduser('~')
#musicdir=userhome+'/Music/google_music/top100/'
#gmbox_home=userhome+'/.gmbox/'

if os.path.exists(musicdir)==0:
    os.makedirs(musicdir)   #递归创建目录  mkdir是创建最后一层目录！amoblin
if os.path.exists(gmbox_home)==0:
    os.makedirs(gmbox_home)
    
playlist_path=gmbox_home+'default.xml'



play_over=1  #标志信号量：自动播放完毕还是被打断，默认自动播放完



if __name__ == '__main__':
    print u"请勿直接执行此文件,图选界面请执行MainWindow.py,命令行界面请执行cli.py"
    
