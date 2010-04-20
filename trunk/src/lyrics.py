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

import re
import gtk
from time import time, sleep
from threading import Thread
from threads import threads

class Lyrics(gtk.Label):
    
    def __init__(self):
        gtk.Label.__init__(self)
        self.time_reg = re.compile(r'\[([0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,2})\]')
        self.con_reg = re.compile(r'^[0-9\[\]:\.]*(.*)$')
        self.__ref_freq = 0.1
        self.status = 'idle'
    
    def load(self, lrc_file):
        self.stime = int(time() * 100)
        lrc = open(lrc_file).read()
        self.lyrics = {0 : '开始'}
        self.timeline = [0]
        for line in lrc.decode('utf8').split('\n'):
            curr = self.con_reg.findall(line)
            for timestamp in self.time_reg.findall(line):
                h = int(timestamp.split(':')[0])
                m = int(timestamp.split(':')[1].split('.')[0])
                s = int(timestamp.split(':')[1].split('.')[1])
                hms = ( h * 60 + m ) * 100 + s
                self.timeline.append(hms)
                self.lyrics[hms] = curr[0].split('\r')[0]
        self.timeline.sort()
        self.status = 'needstop'
        sleep(self.__ref_freq * 2.5)
        threads.lyrics = Thread(target=self.update_lyrics)
        threads.lyrics.daemon = True
        threads.lyrics.start()
    
    def update_lyrics(self):
        self.status = 'runing'
        while True:
            passed = int(time() * 100) - self.stime
            bef = 0
            for the in self.timeline:
                if passed <= the:
                    break
                bef = the
            #TODO: 这里要优化
            self.set_time(bef, the)
            if self.status == 'needstop':
                break
            sleep(self.__ref_freq)
    
    def set_time(self, bef, the):
        text = ''
        for hms in self.timeline:
            if hms == bef:
                text += '<span color="blue" size="large" weight="ultrabold">'+self.lyrics[hms]+'</span>'+'\n'
            else:
                text += self.lyrics[hms]+'\n'
        self.set_text(text)
        self.set_use_markup(True)
