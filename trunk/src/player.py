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
from lib.config import config
try:
    import pynotify
except ImportError:
    pynotify = None
    
from threads import threads

(COL_STATUS, COL_NUM, COL_TITLE, COL_FILE) = range(4)
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

        self.set_rules_hint(True)
        
        self._model = gtk.ListStore(bool, str, str, str)
        self.set_model(self._model)
        
        os.path.walk(config.item['savedir'], self.insert, None)
        
    def fixed_toggled(self, cell, path):
        oiter = self._model.get_iter((int(path),))
        fixed = self._model.get_value(oiter, COL_STATUS)
        fixed = not fixed
        self._model.set(oiter, COL_STATUS, fixed)
    
    def insert(self, arg, dirname, names):
        for name in names:
            fname = os.path.join(dirname, name)
            if os.path.isfile(fname) and fname.lower().endswith('.mp3'):
                self._model.append([False, len(self._model), name, fname])

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
        
        self.play_list = PlayList()
        self.pack_start(self.play_list)        
        self.pack_start(gtk.ProgressBar(), False, False)
        self.pack_start(buttons, False, False)
        if pynotify:
            pynotify.init("GMbox")
        
    def play(self, widget):
        '''试听，播放'''
        selected = []
        for i in range(len(self.play_list._model)):
            oiter = self.play_list._model.get_iter((i,))
            if self.play_list._model.get_value(oiter, COL_STATUS):
                selected.append(self.play_list._model.get_value(oiter, COL_FILE))
        self.play_files(selected)

    def play_files(self, files):
        threads.kill_paly()
        for f in files:
            if pynotify:
                info = os.path.basename(f)[:-4]
                self.notification = pynotify.Notification(u'正在播放', info, 'dialog-info')
                self.notification.set_timeout(5000)
                self.notification.show()
            
            threads.play = Popen(['mpg123', f], stdout=PIPE, stderr=PIPE)
        
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

    def focus_prev(self, widget):
        self.current_path = self.current_path - 1
        widget.set_cursor(self.current_path)

    def play_next(self, widget):
        self.focus_next(widget)
        self.listen(widget)

    def play_prev(self, widget):
        self.focus_prev(widget)
        self.listen(widget)

