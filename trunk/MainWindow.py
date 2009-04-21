#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gtk.glade
import gmbox
import thread

(COL_NUM, COL_TITLE, COL_ARTIST) = range(3)
class MainWindow():
    def __init__(self):

        self.gladefile="gmbox.glade"
        self.xml=gtk.glade.XML(self.gladefile)
        self.window = self.xml.get_widget("window_main")
        self.notebook = self.xml.get_widget("notebook_top")
        self.notebook.set_show_tabs(False)

        dic={"on_pbutton_album_clicked":self.btnAlbum_clicked,
                "on_pbutton_down_clicked": self.btnDown_clicked,
                "on_pbutton_list_clicked": self.btnList_clicked,
                "on_pbutton_searched_clicked": self.btnSearched_clicked,
                "on_pbutton_about_clicked": self.btnAbout_clicked}
        self.xml.signal_autoconnect(dic)

        #page 1
        vbox= self.xml.get_widget("vbox_p1")
        hbox = gtk.HBox()
        opt = gtk.combo_box_new_text()
        for slist in gmbox.songlists:
            opt.append_text(slist)
        opt.set_active(0)
        hbox.pack_start(opt, False)
        self.button = gtk.Button('获取列表')
        size = self.button.size_request()
        self.button.set_size_request(size[0]+50, -1)
        opt.set_size_request(size[0]+150, -1)
        self.button.connect('clicked', self.doSearch, opt)
        hbox.pack_start(self.button, False)
        vbox.pack_start(hbox, False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        tree = self.setTreeView()
        tree.set_rules_hint(True)
        scroll.add(tree)
        vbox.pack_start(scroll)

        #setup system tray icon
        self.setupSystray()
        
        self.window.set_title("GMBox")
        self.window.set_default_size(800, 600)
        self.window.connect('destroy', gtk.main_quit)
        self.window.show_all();

    def setupSystray(self):
        self.systray = gtk.StatusIcon()
        self.systray.set_from_file("systray.png")
        self.systray.connect("activate", self.systrayCb)
        self.systray.connect('popup-menu', self.systrayPopup)
        self.systray.set_tooltip("Click to toggle window visibility")
        self.systray.set_visible(True)
        return

    def systrayCb(self, widget):
        """Check out window's status"""
        if self.window.get_property('visible'):
            self.window.hide()
        else:
            self.window.deiconify()
            self.window.present()

    def systrayPopup(self, statusicon, button, activate_time):
        """Create and show popup menu"""
        popup_menu = gtk.Menu()
        restore_item = gtk.MenuItem("Restore")
        restore_item.connect("activate", self.systrayCb)
        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", gtk.main_quit)
        popup_menu.append(restore_item)
        popup_menu.append(quit_item)
        popup_menu.show_all()
        time = gtk.get_current_event_time()
        popup_menu.popup(None, None, None, 0, time)
        

    def btnAlbum_clicked(self,widget):
        self.notebook.set_current_page(0)
        
    def btnList_clicked(self,widget):
        self.notebook.set_current_page(3)

    def btnSearched_clicked(self,widget):
        self.notebook.set_current_page(1)

    def btnDown_clicked(self,widget):
        self.notebook.set_current_page(2)

    def btnAbout_clicked(self,widget):
        self.notebook.set_current_page(4)

    
        
    def downList(self,text):
        l=gmbox.Lists(text);
        self.model.clear()
        for song in l.songlist:
            self.model.append(
                [l.songlist.index(song)+1,song['title'],song['artist']])
        self.button.set_sensitive(True)

    def doSearch(self,widget,opt):
        text=opt.get_active_text().decode('utf8')
        self.button.set_sensitive(False)
        thread.start_new_thread(self.downList,(text,))
        #l=gmbox.Lists(text);
        #self.model.clear()
        #for song in l.songlist:
        #    self.model.append(
        #        [l.songlist.index(song)+1,song['title'],song['artist']])

    def setTreeView(self):
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.model = gtk.ListStore(str, str, str)
        treeview = gtk.TreeView(self.model)
        treeview.connect('button-press-event', self.onSearchListRightClicked, None)
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

#        renderer = gtk.CellRendererText()
#        renderer.set_data("column", COL_ALBUM)
#        renderer.set_property('editable', True)
#        #renderer.connect("edited", self.on_cell_edited, None)
#        column = gtk.TreeViewColumn("专辑", renderer, text=COL_ALBUM)
#        column.set_resizable(True)
#        treeview.append_column(column)
#
#        renderer = gtk.CellRendererText()
#        renderer.set_data("column", COL_SIZE)
#        column = gtk.TreeViewColumn("长度", renderer, text=COL_SIZE)
#        column.set_resizable(True)
#        treeview.append_column(column)
        return treeview


    def onSearchListRightClicked(self, view, event, data):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            selected = view.get_selection().get_selected()
            popupmenu = gtk.Menu()
            menuitem = gtk.MenuItem('下载')
            #menuitem.connect('activate', self.download, selected)
            popupmenu.append(menuitem)
            menuitem = gtk.MenuItem('试听')
            #menuitem.connect('activate', self.listen, selected)
            popupmenu.append(menuitem)
            menuitem = gtk.MenuItem('删除已有下载')
            #menuitem.connect('activate', self.delete, selected)
            popupmenu.append(menuitem)
            popupmenu.show_all()
            popupmenu.popup(None, None, None, event.button, event.get_time(), None)
       

def test():
    print "testing for thread"

def main():
    win = MainWindow();
    gtk.gdk.threads_init()
    gtk.main()


if __name__ == '__main__':
    main()
