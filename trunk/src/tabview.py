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

from lib.const import *


class tabview(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)
        
        self.set_show_tabs(False)

        self.setup_album_tab()
        self.setup_search_tab()

        self.show_all()

# =========================================
# methods setup five tabs
        
    def setup_album_tab(self):
        
        #page 1: list page

        hb = gtk.HBox(False, 0)
        
        self.combox = gtk.combo_box_new_text()
        self.combox.append_text("--请选择--")
        [self.combox.append_text(slist) for slist in songlists]
        self.combox.set_active(0)
        #self.combox.connect("changed", self.doSearch)
        
        self.but_down_select = gtk.Button('下载选中的音乐')
        self.but_adition_select = gtk.Button('试听选中的音乐')
        hb.pack_start(self.combox)
        hb.pack_start(self.but_down_select)
        hb.pack_start(self.but_adition_select)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)

        #self.list_view= ListView(self.xml)
        #self.list_view.treeview.connect('button-press-event', self.click_checker)
        #self.list_view.treeview.connect('key_press_event', self.tree_view_key_checker)


    def setup_search_tab(self):
        
        hb = gtk.HBox(False, 0)
        self.search_entry = gtk.Entry()
        self.search_ok = gtk.Button("搜索")
        hb.pack_start(self.search_entry)
        hb.pack_start(self.search_ok)

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

        #page 3:  downlist page
        #self.down_tree = downpage.DownTreeView(self.xml)
        #self.down_tree = DownTreeView(self.xml)
        #self.file_list_view = FileListView(self.xml,gmbox.musicdir)
        #button = self.xml.get_widget('filelist_button')
        #button.connect('clicked',self.dolistLocalFile,)


        pass

    def setup_playlist_tab(self):

        #page 4: playlist page
        #self.playlist_view= PlayListView(self.xml)
        #self.playlist_view.treeview.connect('button-press-event',self.playlist_click_checker)
        #self.playlist_view.treeview.connect('key_press_event',self.tree_view_key_checker)

        pass

    def setup_about_tab(self):
        
        pass

# ============================================
# signal methods

    def doSearch(self,widget):
        '''Begin song(album) list download thread'''
        
        text=widget.get_active_text().decode('utf8')
        if text != "--请选择--":
            widget.set_sensitive(False)
            thread.start_new_thread(self.downList,(text,widget,))

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
    
    def SetupPopup(self):
        '''popup menu for album list tab'''
        
        time = gtk.get_current_event_time()

        popupmenu = gtk.Menu()
        menuitem = gtk.MenuItem('下载')
        menuitem.connect('activate', self.downone)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('试听')
        menuitem.connect('activate', self.listen)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('添加到播放列表')
        menuitem.connect('activate', self.addToPlaylist)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('删除已有下载')
        menuitem.connect('activate', self.delete_file)
        popupmenu.append(menuitem)

        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)

        
    def click_checker(self, view, event):
        '''榜单页，下载页击键处理'''
        
        #self.get_current_list(view,event)
        self.get_current_location(view,event)
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.listen(view)
            
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            #selected,iter = view.get_selection().get_selected()
            #index = selected.get_value(iter, 0)
            #print index

            # Here test whether we have songlist, if have, show popup menu
            try:
                #if self.list_view:
                self.SetupPopup()
            except:
                print "button press error..."
                pass

# ========================================
# methods for popup menu above
        
    def downone(self, widget):
        #selected = self.current_list.treeview.get_selection().get_selected()
        #list_model,iter = selected
        #artist = list_model.get_value(iter, COL_ARTIST)
        #title = list_model.get_value(iter, COL_TITLE)
        artist = self.current_list.get_artist(self.current_path)
        title = self.current_list.get_title(self.current_path)
        id = self.current_list.get_id(self.current_path)
        self.down_tree.add(title,artist,id)

    def listen(self, widget):
        try:
            thread.start_new_thread(self.play,(self.current_path,))
        except:
            print "Error"

    def addToPlaylist(self, widget):
        selected = self.current_list.treeview.get_selection().get_selected()
        list_model,iter = selected
        artist = list_model.get_value(iter, COL_ARTIST)
        title = list_model.get_value(iter, COL_TITLE)
        id = self.current_list.get_id(self.current_path)
        self.playlist_view.add(title,artist,str(id))

    def delete_file(self,event):
        self._songlist.delete_file(self.current_path)

        selected = self.list_tree.get_selection().get_selected()
        list_model,iter = selected
        #num = self.list_model.get_value(iter,COL_NUM)
        num = len(self.playlist.songlist)+1
        artist = list_model.get_value(iter, COL_ARTIST)
        title = list_model.get_value(iter, COL_TITLE)
        list_model.remove(self.current_path)
        #self.playlist.add(self._songlist.get_title(self.path[0]),self._songlist.get_artist(self.path[0]),str(self.path[0]))
        self._songlist.delete_file(self.current_path)

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


            


        
"""

class Abs_View:
    '''抽象类：构造各个页面的Treeview'''
    def __init__(self,xml):
        '''依次存入：status,歌曲编号，歌曲名，歌手          #专辑，长度，url'''
        self.model = gtk.ListStore(bool, str, str,str)
        #self.model.connect("row-changed", self.SaveSongIndex)

    def set_treeview(self,xml,treeview_id):
        '''set title'''
        self.treeview = xml.get_widget(treeview_id)
        self.treeview.set_model(self.model)
        self.treeview.set_enable_search(0)
        #treeview.bind('<Button-3>', self.click_checker)
        #treeview.bind('<Double-Button-1>', self.listen)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        checkbutton = gtk.CheckButton()

        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled)
        column = gtk.TreeViewColumn("选中", renderer,active=COL_STATUS)
        #column = gtk.TreeViewColumn("选中", renderer)
        #column.set_resizable(True)
        self.treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_NUM)
        column = gtk.TreeViewColumn("编号", renderer, text=COL_NUM)
        column.set_resizable(True)
        self.treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_TITLE)
        #renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌曲", renderer, text=COL_TITLE)
        column.set_resizable(True)
        self.treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ARTIST)
        #renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌手", renderer, text=COL_ARTIST)
        column.set_resizable(True)
        self.treeview.append_column(column)
        self.treeview.set_rules_hint(True)

    def fixed_toggled(self, cell, path):
        # get toggled iter
        iter = self.model.get_iter((int(path),))
        fixed = self.model.get_value(iter, COL_STATUS)

        # do something with the value
        fixed = not fixed

        if fixed:
            print 'Select[row]:',path
        else:
            print 'Invert Select[row]:',path

        # set new value
        self.model.set(iter, COL_STATUS, fixed)

class ListView(Abs_View,gmbox.Lists):
    '''榜单下载页面'''
    def __init__(self,xml):
        '''get hot song list treeview widget'''
        gmbox.Lists.__init__(self)
        self.model = gtk.ListStore(bool, str, str,str)
        Abs_View.set_treeview(self,xml,'list_treeview')

    def get_list(self,text):
        gmbox.Lists.get_list(self,text)
        self.model.clear()
        [self.model.append([False,self.songlist.index(song)+1,song['title'],song['artist']]) for song in self.songlist]

class SearchListView(Abs_View,gmbox.SearchLists):
    '''音乐搜索页面'''
    def __init__(self,xml):
        gmbox.SearchLists.__init__(self)
        self.model = gtk.ListStore(bool,str, str, str,str)
        Abs_View.set_treeview(self,xml,'search_treeview')

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ALBUM)
        renderer.set_property('editable', False)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("专辑", renderer, text=COL_ALBUM)
        column.set_resizable(True)
        self.treeview.append_column(column)

    def get_list(self,key):
        gmbox.SearchLists.get_list(self,key)
        self.model.clear()
        [self.model.append([False,self.songlist.index(song)+1,song['title'],song['artist'],song['album']]) for song in self.songlist]

class DownTreeView(Abs_View,gmbox.DownloadLists):
    '''下载管理页面之正在下载'''
    def __init__(self,xml):
        gmbox.DownloadLists.__init__(self)
        #依次存入：歌曲编号，歌曲名，歌手，下载状态，下载进度
        self.model=gtk.ListStore(bool,str,str,str,str)
        Abs_View.set_treeview(self,xml,"download_treeview")

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_DOWN)
        column = gtk.TreeViewColumn("状态", renderer, text=COL_DOWN)
        column.set_resizable(True)
        self.treeview.append_column(column)
        self.treeview.set_rules_hint(True)

    def add(self,title,artist,id):
        thread.start_new_thread(gmbox.DownloadLists.add, (self,title,artist,id,))
        num = len(self.songlist)
        self.model.append([False,num,title,artist,"start"])

        if os.name=='posix':
            self.notification = pynotify.Notification("下载", title, "dialog-warning")
        self.notification.set_timeout(1)
        self.notification.show()
        print 'being to download'

class FileListView(Abs_View,gmbox.FileList):
    '''下载管理页面之已下载'''
    def __init__(self,xml,path):
        '''get hot song list treeview widget'''
        gmbox.FileList.__init__(self,path)
        #依次存入：status,歌曲编号，歌曲名，歌手
        self.model = gtk.ListStore(bool, str, str,str,str)
        #self.model.connect("row-changed", self.SaveSongIndex)
        Abs_View.set_treeview(self,xml,'file_treeview')

    def get_list(self):
        gmbox.FileList.get_list(self,gmbox.musicdir)
        print "debug info 1"
        #raw_input("waiting")
        self.model.clear()
        print "debug info 2"
        #raw_input("waiting")
        [self.model.append([False,str(self.songlist.index(song)+1),song['title'],song['artist'],'finished']) for song in self.songlist]
        #raw_input("waiting")
        print "debug info"

class PlayListView(Abs_View,gmbox.PlayList):
    '''播放列表页面'''
    def __init__(self,xml):
        gmbox.PlayList.__init__(self)
        self.model = gtk.ListStore(bool, str, str,str)
        Abs_View.set_treeview(self,xml,"playlist_treeview")

        self.model.clear()
        [self.model.append([False,self.songlist.index(song)+1,song['title'],song['artist']]) for song in self.songlist]

    def add(self,title,artist,id):
        gmbox.PlayList.add(self,title,artist,id)
        num = len(self.songlist)+1
        self.model.append([False,num,title,artist])
        if os.name=='posix':
            notification = pynotify.Notification("添加到播放列表", title, "dialog-warning")
            notification.set_timeout(1)
            notification.show()
"""
