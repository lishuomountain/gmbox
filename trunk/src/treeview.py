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


from lib.network import Lists

log = logging.getLogger('gmbox.treeview')

(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST,COL_DOWN) = range(5)
(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST,COL_ALBUM) = range(5)

class Abs_View(gtk.TreeView):
    '''基类：构造各个页面的Treeview'''
    
    def __init__(self, treeview_id):
        '''依次存入：status,歌曲编号，歌曲名，歌手          #专辑，长度，url'''

        gtk.TreeView.__init__(self)
        
        self.model = gtk.ListStore(bool, str, str,str)
        #self.model.connect("row-changed", self.SaveSongIndex)

        self.set_model(self.model)
        self.set_enable_search(0)
        #treeview.bind('<Button-3>', self.click_checker)
        #treeview.bind('<Double-Button-1>', self.listen)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)

        checkbutton = gtk.CheckButton()

        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled)
        column = gtk.TreeViewColumn("选中", renderer,active=COL_STATUS)
        #column = gtk.TreeViewColumn("选中", renderer)
        #column.set_resizable(True)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_NUM)
        column = gtk.TreeViewColumn("编号", renderer, text=COL_NUM)
        column.set_resizable(True)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_TITLE)
        #renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌曲", renderer, text=COL_TITLE)
        column.set_resizable(True)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ARTIST)
        #renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌手", renderer, text=COL_ARTIST)
        column.set_resizable(True)
        self.append_column(column)
        self.set_rules_hint(True)

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

        
class ListView(Abs_View):
    '''榜单下载页面'''
    
    def __init__(self):
        '''get hot song list treeview widget'''
        
        Abs_View.__init__(self, 'list_treeview')

        self._model = gtk.ListStore(bool, str, str,str)
        
        self.set_model(self._model)

        self.connect('button-press-event', self.click_checker)

    def get_list(self, text):
        '''request network for songs(ablums) list and load it'''
        
        songlist = Lists().get_list(text)
        self.model.clear()
        [self._model.append([False, songlist.index(song)+1 , song['title'] , song['artist']]) for song in songlist]

    
    def SetupPopup(self):
        '''popup menu for album list tab'''
        
        time = gtk.get_current_event_time()

        popupmenu = gtk.Menu()
        menuitem = gtk.MenuItem('下载')
        #menuitem.connect('activate', self.downone)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('试听')
        #menuitem.connect('activate', self.listen)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('添加到播放列表')
        #menuitem.connect('activate', self.addToPlaylist)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('删除已有下载')
        #menuitem.connect('activate', self.delete_file)
        popupmenu.append(menuitem)

        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)

        
    def click_checker(self, view, event):
        '''榜单页，下载页击键处理'''
        
        #self.get_current_list(view,event)
        #self.get_current_location(view, event)
        #if event.type == gtk.gdk._2BUTTON_PRESS:
        #    self.listen(view)
            
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            #selected,iter = view.get_selection().get_selected()
            #index = selected.get_value(iter, 0)
            #print index

            # Here test whether we have songlist, if have, show popup menu
            #try:
                #if self.list_view:
                self.SetupPopup()
            #except:
            #    log.debug('button press error...')

    def get_current_location(self, view, event):
        x = int(event.x)
        y = int(event.y)
        pth = view.get_path_at_pos(x, y)

        if not pth:
            pass
        else:
            self.path, col, cell_x, cell_y = pth
            self.current_path=self.path[0]
            #title = self.current_list.get_title(self.current_path)
            log.debug('select : ' + title)
    

"""        
        
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
        self.append_column(column)

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
        self.append_column(column)
        self.set_rules_hint(True)

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
