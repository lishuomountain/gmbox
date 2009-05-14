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


import gtk
import logging

from player import playbox
from treeview import ListView
from lib.const import *


log = logging.getLogger('gmbox.tabview')

class tabview(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)
        
        self.set_show_tabs(False)

        self.setup_lists_tab()
        self.setup_search_tab()
        self.setup_down_tab()
        self.setup_playlist_tab()
        self.setup_about_tab()

        self.show_all()

# =========================================
# methods setup five tabs
        
    def setup_lists_tab(self):
        
        hb = gtk.HBox(False, 0)
        
        self.combox = gtk.combo_box_new_text()
        self.combox.append_text("--请选择--")
        [self.combox.append_text(slist) for slist in songlists]
        self.combox.set_active(0)
        self.combox.connect("changed", self.doSearch)
        
        self.but_down_select = gtk.Button('下载选中的音乐')
        self.but_down_select.connect('clicked',lambda w:self.list_view.down_select())
        self.but_adition_select = gtk.Button('试听选中的音乐')
        self.but_adition_select.set_sensitive(False)
        hb.pack_start(self.combox, False, False)
        hb.pack_start(self.but_down_select, False, False)
        hb.pack_start(self.but_adition_select, False, False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.list_view = ListView()
        scroll.add(self.list_view)

        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)


        #self.list_view.treeview.connect('key_press_event', self.tree_view_key_checker)


    def setup_search_tab(self):
        
        hb = gtk.HBox(False, 0)
        self.search_entry = gtk.Entry()
        self.search_ok = gtk.Button("搜索")
        hb.pack_start(self.search_entry)
        hb.pack_start(self.search_ok, False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)
        
        #page 2: search page
        
        #self.search_entry = self.xml.get_widget('search_entry')
        #self.search_entry.connect('key_press_event', self.entry_key_checker)
        #self.search_button = self.xml.get_widget('search_button')

        #self.search_list_view= SearchListView(self.xml)
        #self.search_list_view.treeview.connect('button-press-event', self.click_checker)
        #self.search_list_view.treeview.connect('key_press_event', self.tree_view_key_checker)

    def setup_down_tab(self):

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        vb = gtk.VBox(False, 0)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)

        #page 3:  downlist page
        #self.down_tree = downpage.DownTreeView(self.xml)
        #self.down_tree = DownTreeView(self.xml)
        #self.file_list_view = FileListView(self.xml,gmbox.musicdir)
        #button = self.xml.get_widget('filelist_button')
        #button.connect('clicked',self.dolistLocalFile,)

        
    def setup_playlist_tab(self):

        self.player = playbox()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        vb = gtk.VBox(False, 0)
        vb.pack_start(scroll, True, True)
        vb.pack_start(self.player, False)

        self.append_page(vb)

        #page 4: playlist page
        #self.playlist_view= PlayListView(self.xml)
        #self.playlist_view.treeview.connect('button-press-event',self.playlist_click_checker)
        #self.playlist_view.treeview.connect('key_press_event',self.tree_view_key_checker)

    def setup_about_tab(self):
        about_label=gtk.Label('<span size="xx-large" weight="ultrabold">'
            +'gmbox V'+VERSION+'</span>')
        about_label.set_use_markup(True)
        self.append_page(about_label)
        

# ============================================
# signal methods

    def doSearch(self, widget):
        '''Begin song(album) list download thread'''
        
        text=widget.get_active_text().decode('utf8')
        if text != "--请选择--":
            widget.set_sensitive(False)
            self.list_view.get_list(text)
            widget.set_sensitive(True)
            

    def doSearchMusic(self,widget):
        '''music search button clicked callback'''
        
        key = self.search_entry.get_text().decode('utf8')
        print key
        self.search_button.set_sensitive(False)
        thread.start_new_thread(self.SearchMusic,(key,))

    def dolistLocalFile(self,widget):
        '''callback for download manage tab'''
        
        print "while start thread"
        thread.start_new_thread(self.listLocalFile,(widget,))
        print "OK"

    
    
# =============================================
# ========================================


# ======================================

    def SetupPopup2(self):
        '''popup menu for playlist tab'''
        
        time = gtk.get_current_event_time()

        popupmenu = gtk.Menu()

        menuitem = gtk.MenuItem('试听')
        menuitem.connect('activate', self.listen_init)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('从列表删除')
        menuitem.connect('activate', self.DelFromPlaylist)
        popupmenu.append(menuitem)
        
        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)


    def playlist_click_checker(self, view, event):
        self.get_current_location(view,event)

        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.listen(view)

        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            #selected,iter = view.get_selection().get_selected()
            #index = selected.get_value(iter, 0)
            #print index

            # Here test whether we have songlist, if have, show popup menu
            try:
                self.SetupPopup2()
            except:
                pass

