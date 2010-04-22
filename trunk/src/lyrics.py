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
'''GUI内置的歌词显示'''

import re, os
import gtk
from time import time, sleep
from threading import Thread
from threads import threads

class Lyrics(gtk.Label):
    '''歌词显示控件'''
    def __init__(self):
        '''初始化'''
        gtk.Label.__init__(self)
        self.time_reg = re.compile(r'\[([0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,2})\]')
        self.con_reg = re.compile('^[0-9\[\]:\.]*(.*)$')
        self.__ref_freq = 0.1
        self.status = 'idle'
        self.lines = 15
        self.comm_style = '<span>%s</span>\n'
        self.curr_style = '<span color="blue" size="large" weight="bold">%s</span>\n'
        self.err_style = '<span color="red" size="large" weight="ultrabold">%s</span>\n'
        self.set_markup('<span size="large" weight="ultrabold">歌词显示区域</span>')
        
    def load(self, lrc_file):
        '''载入歌词文件，同时打开歌词刷新子线程'''
        self.status = 'needstop'
        sleep(self.__ref_freq * 2.5)
        if not os.path.exists(lrc_file):
            self.set_markup(self.err_style % u'未发现对应的歌词文件！')
            return
        self.stime = int(time() * 100)
        lrc = open(lrc_file).read().decode('utf8')
        if lrc.startswith(u'\ufeff'):
            lrc = lrc[1:]
        self.lyrics = {0 : u'《%s》' % os.path.basename(lrc_file)[:-4]}
        self.timeline = [0]
        for line in lrc.split('\n'):
            curr = self.con_reg.findall(line)[0]
            if curr.endswith('\r'):
                curr = curr.split('\r')[0]
            for timestamp in self.time_reg.findall(line):
                h = int(timestamp.split(':')[0])
                m = int(timestamp.split(':')[1].split('.')[0])
                s = int(timestamp.split(':')[1].split('.')[1])
                hms = ( h * 60 + m ) * 100 + s
                if hms != 0:
                    self.timeline.append(hms)
                    self.lyrics[hms] = curr
        self.timeline.sort()
#        for t in self.timeline:
#            print t,'==>',self.lyrics[t]
        threads.lyrics = Thread(target=self.update_lyrics)
        threads.lyrics.daemon = True
        threads.lyrics.start()
    
    def update_lyrics(self):
        '''负责刷新歌词'''
        self.status = 'runing'
        old_region_s = -1
        while True:
            passed = int(time() * 100) - self.stime
            region_s = 0
            for region_e in self.timeline:
                if passed <= region_e:
                    break
                region_s = region_e
            if old_region_s != region_s:
                self.set_time(region_s, region_e)
                old_region_s = region_s
            if self.status == 'needstop':
                break
            sleep(self.__ref_freq)
    
    def set_time(self, region_s, region_e):
        '''根据时间点，组织并显示歌词'''
        text = '\n'
        now = self.timeline.index(region_s)
        i = 0
        for hms in self.timeline:
            #这个大if，是为了尽量显示指定的行。
            if ( now < self.lines / 2 and i < self.lines ) or \
                ( now > len(self.timeline) - self.lines / 2 and \
                i >= len(self.timeline) - self.lines ) or \
                ( abs( i - now ) <= int(self.lines / 2) ):
                if hms == region_s:
                    text += self.curr_style % self.lyrics[hms]
                else:
                    text += self.comm_style % self.lyrics[hms]
            i += 1
        self.set_markup(text)
        
