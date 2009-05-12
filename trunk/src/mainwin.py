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


import pygtk
pygtk.require('2.0')
import gtk
import os
from optparse import OptionParser


from lib.utils import find_image
from tabview import *

if os.name == 'posix':
    import pynotify

class mainwin(gtk.Window):
    def __init__(self):
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_title("GMBox")
        self.set_default_size(800, 600)
        # need work
        ui_logo=gtk.gdk.pixbuf_new_from_file(find_image('gmbox.png'))
        self.set_icon(ui_logo)

        self.connect('destroy', gtk.main_quit)
        #self.window.connect('key_press_event', self.key_checker)

        vb = gtk.VBox(False, 0)
        self.but_box = self.setup_but_box()
        self.gm_notebook = tabview()
        self.status = gtk.Statusbar()
        vb.pack_start(self.but_box, False, False, 5)
        vb.pack_start(self.gm_notebook, True, True)
        vb.pack_start(self.status, False, False)

        #setup system tray icon
        self.setupSystray()

        self.add(vb)
        self.show_all()

        
    def setupSystray(self):
        
        self.systray = gtk.StatusIcon()
        # need write a find picture method
        self.systray.set_from_file(find_image('gmbox.png'))
        self.systray.connect("activate", self.systrayCb)
        self.systray.connect('popup-menu', self.systrayPopup)
        self.systray.set_tooltip("Click to toggle window visibility")
        self.systray.set_visible(True)

        if os.name == 'posix':
            pynotify.init("Some Application or Title")
            self.notification = pynotify.Notification("Title", "body", "dialog-warning")
            self.notification.set_urgency(pynotify.URGENCY_NORMAL)
            self.notification.set_timeout(1)
        return

    def systrayCb(self, widget):
        """Check out window's status"""
        
        if self.get_property('visible'):
            self.hide()
        else:
            self.show()
            #self.deiconify()
            #self.present()

    def systrayPopup(self, statusicon, button, activate_time):
        """Create and show popup menu"""
        
        popup_menu = gtk.Menu()
        restore_item = gtk.MenuItem("Restore")
        restore_item.connect("activate", self.systrayCb)
        popup_menu.append(restore_item)

        #prev_item = gtk.MenuItem("Previous")
        #prev_item.connect("activate", self.tray_play_prev)
        #popup_menu.append(prev_item)

        #next_item = gtk.MenuItem("Next")
        #next_item.connect("activate", self.tray_play_next)
        #popup_menu.append(next_item)

        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", gtk.main_quit)
        popup_menu.append(quit_item)

        popup_menu.show_all()
        time = gtk.get_current_event_time()
        popup_menu.popup(None, None, None, 0, time)


    def setup_but_box(self):

        but_box = gtk.HButtonBox()

        but_album = gtk.Button('榜单下载')
        but_album.connect('clicked',
                          lambda w:self.gm_notebook.set_current_page(0))
        
        but_search = gtk.Button('音乐搜索')
        but_search.connect('clicked',
                           lambda w:self.gm_notebook.set_current_page(1))
        
        but_down = gtk.Button('下载管理')
        but_down.connect('clicked',
                         lambda w:self.gm_notebook.set_current_page(2))
        
        but_playlist = gtk.Button('播放列表')
        but_playlist.connect('clicked',
                             lambda w:self.gm_notebook.set_current_page(3))
        
        but_about = gtk.Button('关于')
        but_about.connect('clicked',
                          lambda w:self.gm_notebook.set_current_page(4))

        but_box.pack_start(but_album)
        but_box.pack_start(but_search)
        but_box.pack_start(but_down)
        but_box.pack_start(but_playlist)
        but_box.pack_start(but_about)

        return but_box

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--debug',  action='store_true', dest='debug')

    (options, args) = parser.parse_args()

    if options.debug:
        import logging
        log = logging.getLogger('gmbox')
        logging.basicConfig(level=logging.DEBUG)

    mainwin()
    gtk.main()
