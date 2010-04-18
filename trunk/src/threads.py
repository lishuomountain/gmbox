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

'''GUI：处理子进程及子线程'''

class Threads():
    '''处理子进程及子线程'''
    def __init__(self):
        self.down = None  #此为线程
        self.play = None  #此为进程
        self.play_control = None  #此为线程
    def is_downing(self):
        '''是否仍在下载'''
        return True if threads.down and threads.down.is_alive() else False
    def is_playing(self):
        '''是否在播放'''
        return True if threads.play_control and threads.play_control.is_alive() else False
    def kill_play(self):
        '''杀死播放子进程'''
        if self.play != None:
            self.play.poll()
            if self.play.returncode == None:
                self.play.terminate()
        
threads = Threads()

