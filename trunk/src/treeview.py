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

import gtk, logging, threading
from time import sleep

from threads import threads
from statusbar import statusbar
from lib.core import gmbox

log = logging.getLogger('gmbox.treeview')

(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST) = range(4)

class Abs_View(gtk.TreeView):
    '''基类：构造各个页面的Treeview'''
    
    def __init__(self, treeview_id):
        '''依次存入：status,歌曲编号，歌曲名，歌手          #专辑，长度，url'''

        gtk.TreeView.__init__(self)
        self.connect('button-press-event', self.click_checker)        

        self.set_enable_search(0)
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
    
    def select_all(self, v):
        for i in range(len(self._model)):
            oiter = self._model.get_iter((i,))
            self._model.set(oiter, COL_STATUS, v)

    def up_prs(self, blocks, block_size, total_size):
        if blocks == -1:
            statusbar.push(0, u'正在下载' + total_size + '...')
            statusbar.textbox.set_text(block_size)
        elif blocks == -2:
            statusbar.push(0, u'已完成.')
        else:
            percentage = float(blocks) / (total_size / block_size + 1)
            statusbar.progress.set_fraction(percentage)
    def SetupPopup(self):
        '''popup menu for album list tab'''
        
        time = gtk.get_current_event_time()

        popupmenu = gtk.Menu()
        menuitem = gtk.MenuItem('下载')
        menuitem.connect('activate', lambda w:self.download(self.current_path))
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('试听')
        #TODO 此功能待完善
        menuitem.set_sensitive(False)
        #menuitem.connect('activate', self.listen)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('添加到播放列表')
        #TODO 此功能待完善
        menuitem.set_sensitive(False)
        #menuitem.connect('activate', self.addToPlaylist)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('删除已有下载')
        #TODO 此功能待完善
        menuitem.set_sensitive(False)
        #menuitem.connect('activate', self.delete_file)
        popupmenu.append(menuitem)

        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)

        
    def click_checker(self, view, event):
        '''榜单页，下载页击键处理'''
        self.get_current_location(event.x, event.y)
            
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            if None != self.current_path:
                self.SetupPopup()

    def get_current_location(self, x, y):
        '''Used for save path of mouse click position'''

        pth = self.get_path_at_pos(int(x), int(y))

        if pth:
            path, col, cell_x, cell_y = pth
            self.current_path = path[0]
            log.debug('select index : %d' % self.current_path)
        else:
            self.current_path = None
                            
# methods for popup menu above
    def download(self, which):
        if threads.is_downing():
            print u'另一个进程正在下载。。。'
            return
        if isinstance(which, int):
            threads.down = threading.Thread(target=gmbox.downone, args=(which, self.up_prs))
        else:
            threads.down = threading.Thread(target=gmbox.down_listed, args=(which, self.up_prs))
        threads.down.daemon = True
        threads.down.start()
        
    def down_select(self):
        selected = []
        for i in range(len(self._model)):
            oiter = self._model.get_iter((i,))
            if self._model.get_value(oiter, COL_STATUS):
                selected.append(i)
        if selected:
            self.download(selected)
        
class ListView(Abs_View):
    '''榜单下载页面'''
    
    def __init__(self):
        '''get hot song list treeview widget'''
        Abs_View.__init__(self, 'list_treeview')
        self._model = gtk.ListStore(bool, str, str, str)
        self.set_model(self._model)


    def get_list(self, text, combo):
        '''request network for songs(ablums) list and load it'''
        statusbar.push(0, u'正在获取"' + text + u'"的歌曲列表,请稍候...')
        list_thread = threading.Thread(target=gmbox.get_list, args=(text, self.list_up_prs))
        list_thread.start()
        update_thread = threading.Thread(target=self.update_listview, args=(list_thread, combo,))
        update_thread.start()

        return update_thread
        
    def update_listview(self, thread, combo):

        # loop inquiry until download thread is not alive
        while thread.isAlive():
            sleep(0.1)
        else:
            gtk.gdk.threads_enter()
            self._model.clear()
            if gmbox.songlist:
                [self._model.append(
                    [False, gmbox.songlist.index(song) + 1, song['title'] , song['artist']]
                    ) for song in gmbox.songlist]
                statusbar.push(0, u'获取列表成功.')
            else:
                statusbar.push(0, u'错误:获取列表失败.')
            combo.set_sensitive(True)
            gtk.gdk.threads_leave()

    def list_up_prs(self, current_page, total_pages):
        statusbar.progress.set_fraction(float(current_page)/total_pages)

class AlbumListView(Abs_View):
    '''专辑榜单下载页面'''
    
    def __init__(self):
        '''get hot song list treeview widget'''
        Abs_View.__init__(self, 'list_treeview')
        self._model = gtk.ListStore(bool, str, str, str)
        self.set_model(self._model)
        
    def update_albumlistview(self, thread, combo):

        # loop inquiry until download thread is not alive
        while thread.isAlive():
            sleep(0.1)
        else:
            gtk.gdk.threads_enter()
            self._model.clear()
            if gmbox.albumlist:
                [self._model.append(
                    [False, gmbox.albumlist.index(album)+1, album['name'] , album['memo']]
                    ) for album in gmbox.albumlist]
                statusbar.push(0, u'获取列表成功.')
            else:
                statusbar.push(0, u'错误:获取列表失败.')
            combo.set_sensitive(True)
            gtk.gdk.threads_leave()
            
    def get_albumlist(self, text, combo):
        '''request network for songs(ablums) list and load it'''
        statusbar.push(0, u'正在获取"' + text + u'"的专辑列表,请稍候...')
        list_thread = threading.Thread(target=gmbox.get_album_IDs, args=(text, self.list_up_prs))
        list_thread.start()
        update_thread = threading.Thread(target=self.update_albumlistview, args=(list_thread, combo,))
        update_thread.start()

        return update_thread

    def list_up_prs(self, current_page, total_pages):
        statusbar.progress.set_fraction(float(current_page)/total_pages)

    def download(self, which):
        if threads.is_downing():
            print u'另一个进程正在下载。。。'
            return
        if isinstance(which, int):
            threads.down = threading.Thread(target=gmbox.downalbum, args=(which, self.up_prs))
        else:
            threads.down = threading.Thread(target=gmbox.downalbums, args=(which, self.up_prs))
        threads.down.daemon = True
        threads.down.start()
        
class SearchView(Abs_View):
    '''关键词搜索页面'''
    
    def __init__(self):
        Abs_View.__init__(self, 'list_searchview')
        self._model = gtk.ListStore(bool, str, str, str)
        self.set_model(self._model)

    def search(self, text, combo):
        '''request network for songs(ablums) list and load it'''
        statusbar.push(0, u'正在搜索"' + text + u'",请稍候...')
        search_thread = threading.Thread(target=gmbox.search, args=(text,))
        search_thread.start()
        update_thread = threading.Thread(target=self.update_searchview, args=(search_thread, combo,))
        update_thread.start()

        return update_thread

    def update_searchview(self, thread, combo):

        # loop inquiry until download thread is not alive
        while thread.isAlive():
            sleep(0.1)
        else:
            gtk.gdk.threads_enter()
            self._model.clear()
            if gmbox.songlist:
                [self._model.append(
                    [False, gmbox.songlist.index(song) + 1, song['title'] , song['artist']]
                    ) for song in gmbox.songlist]
                statusbar.push(0, u'搜索成功.')
            else:
                statusbar.push(0, u'错误:搜索失败.')
            combo.set_sensitive(True)
            gtk.gdk.threads_leave()

class AlbumSearchView(Abs_View):
    '''关键词搜索页面'''
    
    def __init__(self):
        Abs_View.__init__(self, 'list_searchview')
        self._model = gtk.ListStore(bool, str, str, str)
        self.set_model(self._model)

    def search(self, text, combo):
        '''request network for songs(ablums) list and load it'''
        statusbar.push(0, u'正在搜索专辑"' + text + u'",请稍候...')
        search_thread = threading.Thread(target=gmbox.searchalbum, args=(text,))
        search_thread.start()
        update_thread = threading.Thread(target=self.update_searchview, args=(search_thread, combo,))
        update_thread.start()

        return update_thread

    def update_searchview(self, thread, combo):

        # loop inquiry until download thread is not alive
        while thread.isAlive():
            sleep(0.1)
        else:
            gtk.gdk.threads_enter()
            self._model.clear()
            if gmbox.albumlist:
                [self._model.append(
                    [False, gmbox.albumlist.index(album) + 1, album['name'] , album['memo']]
                    ) for album in gmbox.albumlist]
                statusbar.push(0, u'搜索成功.')
            else:
                statusbar.push(0, u'错误:搜索失败.')
            combo.set_sensitive(True)
            gtk.gdk.threads_leave()
            
    def download(self, which):
        if threads.is_downing():
            print u'另一个进程正在下载。。。'
            return
        if isinstance(which, int):
            threads.down = threading.Thread(target=gmbox.downalbum, args=(which, self.up_prs))
        else:
            threads.down = threading.Thread(target=gmbox.downalbums, args=(which, self.up_prs))
        threads.down.daemon = True
        threads.down.start()

