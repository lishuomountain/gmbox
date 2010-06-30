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
import subprocess
from threading import Thread
from lib.config import config
from lib.utils import deal_input
from lyrics import Lyrics
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
        self.connect('button-press-event', self.click_checker)

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
        
        self.current_path = 0
        self.set_cursor(self.current_path)
        
    def click_checker(self, view, event):
        pos = self.get_path_at_pos(int(event.x), int(event.y))
        if pos is not None:
            self.current_path = pos[0][0]
    
    def play_rfsh(self, o):
        self._model.clear()
        os.path.walk(config.item['savedir'], self.insert, None)
        self.set_cursor(self.current_path)
        
    def fixed_toggled(self, cell, path):
        oiter = self._model.get_iter((int(path),))
        fixed = self._model.get_value(oiter, COL_STATUS)
        fixed = not fixed
        self._model.set(oiter, COL_STATUS, fixed)
    
    def insert(self, arg, dirname, names):
        for name in names:
            fname = os.path.join(dirname, name)
            if os.path.isfile(fname) and fname.lower().endswith('.mp3'):
                self._model.append([True, len(self._model) + 1, name, fname])
    
    def focus_next(self):
        if self.current_path == len(self._model) - 1:
            return False
        self.current_path = self.current_path + 1
        while not self.is_selected(self.current_path):
            if self.current_path == len(self._model):
                return False
            self.current_path = self.current_path + 1
        self.set_cursor(self.current_path)
        return True

    def focus_prev(self):
        if self.current_path == 0:
            return False
        self.current_path = self.current_path - 1
        while not self.is_selected(self.current_path):
            if self.current_path == 0:
                return False
            self.current_path = self.current_path - 1
        self.set_cursor(self.current_path)
        return True
    
    def is_selected(self, i):
        oiter = self._model.get_iter((i,))
        return self._model.get_value(oiter, COL_STATUS)
    
    def get_file(self, i='curr'):
        if i == 'curr':
            oiter = self._model.get_iter((self.current_path,))
        else:
            oiter = self._model.get_iter((i,))
        if os.name == 'nt':
            return self._model.get_value(oiter, COL_FILE).encode('GBK')
        else:
            return self._model.get_value(oiter, COL_FILE)

class PlayBox(gtk.VBox):
    '''播放界面'''
    def __init__(self):
        gtk.VBox.__init__(self)

        self.but_prev = gtk.Button(label=u'前一首',
                                   stock=gtk.STOCK_MEDIA_PREVIOUS)
        self.but_next = gtk.Button(label=u'后一首',
                                   stock=gtk.STOCK_MEDIA_NEXT)
        self.but_play = gtk.Button(label=u'播放所选',
                                   stock=gtk.STOCK_MEDIA_PLAY)
        self.but_stop = gtk.Button(label=u'停止',
                                   stock=gtk.STOCK_MEDIA_STOP)
        self.but_rfsh = gtk.Button(label=u'刷新')

        self.but_play.connect('clicked', self.play)
        self.but_stop.connect('clicked', self.stop)
        self.but_prev.connect('clicked', self.play_prev)
        self.but_next.connect('clicked', self.play_next)
        
        buttons = gtk.HBox()
        buttons.pack_start(self.but_prev, False)
        buttons.pack_start(self.but_play, False)
        buttons.pack_start(self.but_stop, False)
        buttons.pack_start(self.but_next, False)
        buttons.pack_end(self.but_rfsh, False)
        
        self.play_list = PlayList()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.play_list)
        hbox = gtk.HBox()
        hbox.pack_start(scroll)
        self.cover = gtk.Image()
        self.lyrics = Lyrics()
        vbox = gtk.VBox()
        vbox.pack_start(self.cover, False, False)
        vbox.pack_start(self.lyrics)
        hbox.pack_start(vbox)
        self.pack_start(hbox)        
        self.pack_start(gtk.ProgressBar(), False, False)
        self.pack_start(buttons, False, False)
        self.play_state = None
        self.but_rfsh.connect('clicked', self.play_list.play_rfsh)
        if pynotify:
            pynotify.init("GMbox")
        
    def play(self, widget):
        '''试听，播放'''
        if threads.is_playing():
            return
        threads.play_control = Thread(target=self.play_files)
        self.play_state = 'playing'
        threads.play_control.daemon = True
        threads.play_control.start()
    
    def play_files(self):
        threads.kill_play()
        while True:
            f=self.play_list.get_file()
            threads.play = self.play_file(f)
            threads.play.communicate()
            if threads.play.returncode == 0 and not self.play_list.focus_next():
                break;
            if self.play_state == 'stoped':
                break;
            
    def play_file(self, f):
        if pynotify:
            info = os.path.basename(f)[:-4]
            self.notification = pynotify.Notification(u'正在播放', info, 'dialog-info')
            self.notification.set_timeout(5000)
            self.notification.show()
        
        coverfile = os.path.join(os.path.dirname(f), 'cover.jpg')
        if os.path.exists(coverfile):
            self.cover.set_from_file(deal_input(coverfile))
            #self.lyrics.lines = 13
        else:
            self.cover.clear()
            coverfile = None
            #self.lyrics.lines = 19
        
        self.lyrics.load(f[:-4] + '.lrc')
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            startupinfo = None
        
        return subprocess.Popen(['mpg123', f], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, startupinfo=startupinfo)
        
    def stop(self, widget=None):
        '''停止'''
        self.play_state = 'stoped'
        threads.kill_play()

    def play_next(self, widget):
        self.play_list.focus_next()
        if self.play_state != 'playing':
            self.play(None)
        else:
            threads.play.terminate()

    def play_prev(self, widget):
        self.play_list.focus_prev()
        if self.play_state != 'playing':
            self.play(None)
        else:
            threads.play.terminate()
    
playbox = PlayBox()
