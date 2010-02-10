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
'''GUI内置的播放界面'''

import os, gtk
from subprocess import Popen, PIPE
try:
    import pynotify
except ImportError:
    pynotify = None
    
from threads import threads

(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST) = range(4)
class PlayList(gtk.TreeView):
    '''播放列表类'''
    def __init__(self):
        gtk.TreeView.__init__(self)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled)
        column = gtk.TreeViewColumn("选中", renderer, active=COL_STATUS)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_NUM)
        column = gtk.TreeViewColumn("编号", renderer, text=COL_NUM)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_TITLE)
        column = gtk.TreeViewColumn("歌曲", renderer, text=COL_TITLE)
        column.set_resizable(True)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ARTIST)
        column = gtk.TreeViewColumn("歌手", renderer, text=COL_ARTIST)
        column.set_resizable(True)
        self.append_column(column)
        self.set_rules_hint(True)
    def fixed_toggled(self, cell, path):
        oiter = self._model.get_iter((int(path),))
        fixed = self._model.get_value(oiter, COL_STATUS)
        fixed = not fixed
        self._model.set(oiter, COL_STATUS, fixed)


class PlayBox(gtk.VBox):
    '''播放界面'''
    def __init__(self):
        gtk.VBox.__init__(self)

        self.but_prev = gtk.Button(label=u'前一首',
                                   stock=gtk.STOCK_MEDIA_PREVIOUS)
        self.but_next = gtk.Button(label=u'后一首',
                                   stock=gtk.STOCK_MEDIA_NEXT)
        self.but_play = gtk.Button(label=u'播放',
                                   stock=gtk.STOCK_MEDIA_PLAY)
        self.but_stop = gtk.Button(label=u'停止',
                                   stock=gtk.STOCK_MEDIA_STOP)
        self.but_play.connect('clicked', self.play)
        self.but_stop.connect('clicked', self.stop)
        
        buttons = gtk.HBox()
        buttons.pack_start(self.but_prev, False)
        buttons.pack_start(self.but_play, False)
        buttons.pack_start(self.but_stop, False)
        buttons.pack_start(self.but_next, False)
        
        play_list = PlayList()
        self.pack_start(play_list)        
        self.pack_start(gtk.ProgressBar())
        self.pack_start(buttons)
        if pynotify:
            pynotify.init("GMbox")
        
    def play(self, widget):
        '''试听，播放'''
        threads.kill_paly()
        if pynotify:
            self.notification = pynotify.Notification('试听', u'把握你的美-江映蓉', 'dialog-info')
            self.notification.set_timeout(5000)
            self.notification.show()
        #self.playbar.set_text('now playing ' + self.current_list.get_title(start))
        #print 'now playing ', self.current_list.get_title(start)
        #self.current_list.play(start)
        #self.current_list.autoplay(start)
        threads.play = Popen(['mpg123', '/home/lily/gmbox_download/把握你的美-江映蓉.mp3'], stdout=PIPE, stderr=PIPE)
        
    def stop(self, widget=None):
        '''停止'''
        threads.kill_paly()

    def listen_init(self, widget):
        self.current_list = self.playlist
        self.current_path = self.path[0]
        self.listen(widget)

    def focus_next(self, widget):
        self.current_path = self.current_path + 1
        widget.set_cursor(self.current_path)
        #if DEBUG:
        #    print 'now focus', self.current_path
    def focus_prev(self, widget):
        self.current_path = self.current_path - 1
        widget.set_cursor(self.current_path)
        #if DEBUG:
        #    print 'now focus', self.current_path

    def play_next(self, widget):
        #widget.focus_next(widget)
        self.focus_next(widget)
        self.listen(widget)
        #if DEBUG:
        #    print 'now playing', self.current_path
    def play_prev(self, widget):
        #widget.focus_prev(widget)
        self.focus_prev(widget)
        self.listen(widget)
        #if DEBUG:
        #    print 'now playing', self.current_path
