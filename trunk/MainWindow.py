#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,gtk,sys
import gmbox

(COL_NUM, COL_TITLE,
 COL_ARTIST, COL_ALBUM,
 COL_SIZE, COL_URL) = range(6)
class MainWindow(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self)

        self.connect('destroy', gtk.main_quit)      
        
        vbox = gtk.VBox()
        vbox.set_border_width(10)
        self.add(vbox)
        
        hbox = gtk.HBox()
        #label = gtk.Label('/'.join(
        #['%s'%key for key in gmbox.songlists]))
        #vbox.pack_start(label, False)
	opt = gtk.combo_box_new_text()
        for slist in gmbox.songlists:
            	opt.append_text(slist)
        hbox.pack_start(opt, False)
        button = gtk.Button('获取列表')
        size = button.size_request()
        button.set_size_request(size[0]+50, -1)
        opt.set_size_request(size[0]+150, -1)
        button.connect('clicked', self.doSearch, opt)
        hbox.pack_start(button, False)
        vbox.pack_start(hbox, False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        tree = self.setTreeView()
        tree.set_rules_hint(True)
        scroll.add(tree)
        vbox.pack_start(scroll)
        
        self.set_title('GMBox')
        self.set_default_size(800, 600)
        
        
    def doSearch(self,widget,opt):
	text=opt.get_active_text().decode(sys.stdin.encoding)
	l=gmbox.Lists(text);

    def setTreeView(self):
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.model = gtk.ListStore(str, str, str, str, str, str)
        treeview = gtk.TreeView(self.model)
        #treeview.connect('button-press-event', self.onSearchListRightClicked, None)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_NUM)
        column = gtk.TreeViewColumn("编号", renderer, text=COL_NUM)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_TITLE)
        renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌曲", renderer, text=COL_TITLE)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ARTIST)
        renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌手", renderer, text=COL_ARTIST)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ALBUM)
        renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("专辑", renderer, text=COL_ALBUM)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_SIZE)
        column = gtk.TreeViewColumn("长度", renderer, text=COL_SIZE)
        column.set_resizable(True)
        treeview.append_column(column)
        return treeview

def main():
    win = MainWindow();
    win.show_all()
    gtk.main()


if __name__ == '__main__':
    main()
