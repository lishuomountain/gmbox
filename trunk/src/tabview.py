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
import webbrowser

from player import PlayBox
from config import ConfigTable
from treeview import ListView, SearchView, AlbumListView, AlbumSearchView
from lib.const import songlists, albums_lists, VERSION

log = logging.getLogger('gmbox.tabview')

class Tabview(gtk.Notebook):
    '''主窗口的各页面'''
    def __init__(self):
        '''初始化'''
        gtk.Notebook.__init__(self)
        
        self.set_show_tabs(False)

        self.setup_lists_tab()
        self.setup_search_tab()
        self.setup_album_lists_tab()
        self.setup_album_search_tab()
#        self.setup_down_tab()
        self.setup_playlist_tab()
        self.setup_config_tab()
        self.setup_about_tab()
        self.show_all()
        self.connect('switch-page', self.page_changed)
        self.re_fun = {} #用于缓存tab切换的时候的函数
        
# =========================================
# methods setup these tabs
        
    def setup_lists_tab(self):
        
        self.list_view = ListView()
        hb = gtk.HBox(False, 0)
        
        self.combox = gtk.combo_box_new_text()
        self.combox.append_text("--请选择--")
        [self.combox.append_text(slist) for slist in songlists]
        self.combox.set_active(0)
        self.combox.connect("changed", self.do_getlist)
        
        self.but_down_select = gtk.Button('下载选中的音乐')
        self.but_down_select.connect('clicked', lambda w:self.list_view.down_select())
        self.but_adition_select = gtk.Button('试听选中的音乐')
        self.but_adition_select.set_sensitive(False)
        o_select_all = gtk.CheckButton(u'全选')
        o_select_all.connect('toggled', self.do_select_all, self.list_view)
        hb.pack_start(gtk.Label(u'榜单下载: '), False, False)
        hb.pack_start(self.combox, False, False)
        hb.pack_start(self.but_down_select, False, False)
        hb.pack_start(self.but_adition_select, False, False)
        hb.pack_end(o_select_all, False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.list_view)

        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)

    def setup_search_tab(self):
        
        self.search_view = SearchView()
        hb = gtk.HBox(False, 0)
        self.search_entry = gtk.Entry()
        self.search_entry.connect('activate', lambda w:self.do_search(self.search_ok))
        self.search_ok = gtk.Button("搜索")
        self.search_ok.connect('clicked', self.do_search)
        self.but_down_select = gtk.Button('下载所选')
        self.but_down_select.connect('clicked', lambda w:self.search_view.down_select())
        o_select_all = gtk.CheckButton(u'全选')
        o_select_all.connect('toggled', self.do_select_all, self.search_view)
        hb.pack_start(gtk.Label(u'音乐搜索: '), False, False)
        hb.pack_start(self.search_entry)
        hb.pack_start(self.search_ok, False)
        hb.pack_start(self.but_down_select, False)
        hb.pack_end(o_select_all, False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.search_view)
        
        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)

    def setup_album_lists_tab(self):
        
        self.album_list_view = AlbumListView()
        hb = gtk.HBox(False, 0)
        
        self.album_combox = gtk.combo_box_new_text()
        self.album_combox.append_text("--请选择--")
        [self.album_combox.append_text(slist) for slist in albums_lists]
        self.album_combox.set_active(0)
        self.album_combox.connect("changed", self.do_getalbumlist)
        
        self.but_down_select = gtk.Button('下载选中的音乐')
        self.but_down_select.connect('clicked', lambda w:self.album_list_view.down_select())
        self.but_adition_select = gtk.Button('试听选中的音乐')
        self.but_adition_select.set_sensitive(False)
        o_select_all = gtk.CheckButton(u'全选')
        o_select_all.connect('toggled', self.do_select_all, self.album_list_view)
        hb.pack_start(gtk.Label(u'专辑榜单: '), False, False)
        hb.pack_start(self.album_combox, False, False)
        hb.pack_start(self.but_down_select, False, False)
        hb.pack_start(self.but_adition_select, False, False)
        hb.pack_end(o_select_all, False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.album_list_view)

        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)

    def setup_album_search_tab(self):
        
        self.album_search_view = AlbumSearchView()
        hb = gtk.HBox(False, 0)
        self.album_search_entry = gtk.Entry()
        self.album_search_entry.connect('activate', lambda w:self.do_album_search(self.album_search_ok))
        self.album_search_ok = gtk.Button("搜索")
        self.album_search_ok.connect('clicked', self.do_album_search)
        self.but_down_select = gtk.Button('下载所选')
        self.but_down_select.connect('clicked', lambda w:self.album_search_view.down_select())
        o_select_all = gtk.CheckButton(u'全选')
        o_select_all.connect('toggled', self.do_select_all, self.album_search_view)
        hb.pack_start(gtk.Label(u'专辑搜索: '), False, False)
        hb.pack_start(self.album_search_entry)
        hb.pack_start(self.album_search_ok, False)
        hb.pack_start(self.but_down_select, False)
        hb.pack_end(o_select_all, False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.album_search_view)
        
        vb = gtk.VBox(False, 0)
        vb.pack_start(hb, False, False)
        vb.pack_start(scroll, True, True)

        self.append_page(vb)

#    def setup_down_tab(self):
#
#        scroll = gtk.ScrolledWindow()
#        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        tmp_label = gtk.Label('coming soon ...')
#        tmp_label.set_use_markup(True)
#
#        vb = gtk.VBox(False, 0)
#        vb.pack_start(tmp_label, True, True)
#
#        self.append_page(vb)
        
    def setup_playlist_tab(self):

        self.player = PlayBox()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        tmp_label = gtk.Label('coming soon ...')

        vb = gtk.VBox(False, 0)
        vb.pack_start(tmp_label, True, True)
        vb.pack_start(self.player, False)

        self.append_page(vb)

    def setup_config_tab(self):
        config_table = ConfigTable()
        self.append_page(config_table)
        
    def setup_about_tab(self):
        vb = gtk.VBox()
        about_label = gtk.Label('<span size="xx-large" weight="ultrabold">'
            + 'gmbox V' + VERSION + '</span>')
        about_label.set_use_markup(True)
        bt_home = gtk.Button(u'项目主页')
        bt_home.connect('clicked', lambda w: webbrowser.open('http://code.google.com/p/gmbox/'))
        bt_blog = gtk.Button(u' 博客 ')
        bt_blog.connect('clicked', lambda w: webbrowser.open('http://li2z.cn/category/gmbox/?from=gmbox'))
        hb = gtk.HBox()
        hb.pack_start(bt_home)
        hb.pack_start(bt_blog)
        vb.pack_start(about_label)
        vb.pack_start(hb, False, False)
        self.append_page(vb)
        
# signal methods =======================

    def do_select_all(self, widget, view):
        view.select_all(widget.get_active())

    def do_getlist(self, widget):
        '''Begin song(album) list download thread'''
        
        text = widget.get_active_text().decode('utf8')
        if text != "--请选择--":
            # get_list thread will set_sensitive true if download done
            widget.set_sensitive(False)
            self.list_view.get_list(text, widget)
        #保存一个恢复用的函数,在切到其他tab再切回来的时候调用
        self.re_fun[0] = lambda:self.list_view.get_list(text, widget)
    def do_getalbumlist(self, widget):
        '''Begin song(album) list download thread'''
        
        text = widget.get_active_text().decode('utf8')
        if text != "--请选择--":
            # get_list thread will set_sensitive true if download done
            widget.set_sensitive(False)
            self.album_list_view.get_albumlist(text, widget)
        self.re_fun[2] = lambda:self.album_list_view.get_albumlist(text, widget)
    def do_search(self, widget):
        text = self.search_entry.get_text()
        widget.set_sensitive(False)
        self.search_view.search(text, widget)
        self.re_fun[1] = lambda:self.search_view.search(text, widget)
    def do_album_search(self, widget):
        text = self.album_search_entry.get_text()
        widget.set_sensitive(False)
        self.album_search_view.search(text, widget)
        self.re_fun[3] = lambda:self.album_search_view.search(text, widget)
    def page_changed(self, notebook, page, page_num):
        log.debug('tab changed to: ' + str(page_num))
        #切换tab的时候,再调用一次,相当于和gmbox类的当前列表同步
        if page_num in self.re_fun:
            self.re_fun[page_num]()

