#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import gmbox

(COL_NUM, COL_TITLE, COL_ARTIST,COL_DOWN) = range(4)
(COL_NUM, COL_TITLE, COL_ARTIST,COL_ALBUM) = range(4)

class DownTreeView(gmbox.DownloadLists):
    def __init__(self,xml):
        gmbox.DownloadLists.__init__(self)
        #依次存入：歌曲编号，歌曲名，歌手，下载状态，下载进度
        self.down_model=gtk.ListStore(str,str,str,str)
        treeview = xml.get_widget("download_treeview")
        treeview.set_model(self.down_model)
        treeview.set_enable_search(0)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_NUM)
        column = gtk.TreeViewColumn("编号", renderer, text=COL_NUM)
        column.set_resizable(True)
        treeview.append_column(column)
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_TITLE)
        column = gtk.TreeViewColumn("歌曲", renderer, text=COL_TITLE)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ARTIST)
        column = gtk.TreeViewColumn("歌手", renderer, text=COL_ARTIST)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_DOWN)
        column = gtk.TreeViewColumn("状态", renderer, text=COL_DOWN)
        column.set_resizable(True)
        treeview.append_column(column)
        treeview.set_rules_hint(True)
