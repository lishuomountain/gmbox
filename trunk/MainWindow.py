#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gtk.glade
import gmbox
import thread
import pynotify

(COL_NUM, COL_TITLE, COL_ARTIST,COL_DOWN) = range(4)
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
        self.list_button = gtk.Button('获取列表')
        size = self.list_button.size_request()
        self.list_button.set_size_request(size[0]+50, -1)
        opt.set_size_request(size[0]+150, -1)
        self.list_button.connect('clicked', self.doSearch, opt)
        hbox.pack_start(self.list_button, False)
        vbox.pack_start(hbox, False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.list_tree = self.getListTreeView()
        self.list_tree.set_rules_hint(True)
        scroll.add(self.list_tree)
        vbox.pack_start(scroll)

        #setup system tray icon
        self.setupSystray()
        
        #page down
        down_vbox= self.xml.get_widget("vbox_p3")
        down_scroll = gtk.ScrolledWindow()
        down_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        down_scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        down_tree = self.getDownTreeView()
        down_tree.set_rules_hint(True)
        down_scroll.add(down_tree)
        down_vbox.pack_start(down_scroll)

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

        pynotify.init("Some Application or Title")
        self.notification = pynotify.Notification("Title", "body", "dialog-warning")
        self.notification.set_urgency(pynotify.URGENCY_NORMAL)
        self.notification.set_timeout(1)
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

    def getDownTreeView(self):
        #依次存入：歌曲编号，歌曲名，歌手，下载状态，下载进度
        self.down_model=gtk.ListStore(str,str,str,str)
        treeview = gtk.TreeView(self.down_model)
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
        return treeview

    def downList(self,text):
        """Hold song index and prepare for download"""
        self._songlist = gmbox.Lists(text)
        
        self.list_model.clear()
        for song in self._songlist.songlist:
            self.list_model.append(
                [self._songlist.songlist.index(song)+1,song['title'],song['artist']])
        self.list_button.set_sensitive(True)

    def doSearch(self,widget,opt):
        """Begin song list download thread"""
        
        text=opt.get_active_text().decode('utf8')
        self.list_button.set_sensitive(False)
        thread.start_new_thread(self.downList,(text,))

    def getListTreeView(self):
        """get hot song list treeview widget"""
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.list_model = gtk.ListStore(str, str, str)
        #self.list_model.connect("row-changed", self.SaveSongIndex)

        
        treeview = gtk.TreeView(self.list_model)
        treeview.connect('button-press-event', self.click_checker)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_NUM)
        column = gtk.TreeViewColumn("编号", renderer, text=COL_NUM)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_TITLE)
        #renderer.set_property('editable', True)
        #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("歌曲", renderer, text=COL_TITLE)
        column.set_resizable(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ARTIST)
        #renderer.set_property('editable', True)
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

    def SetupPopup(self):
        time = gtk.get_current_event_time()

        popupmenu = gtk.Menu()
        menuitem = gtk.MenuItem('下载')
        menuitem.connect('activate', self.downone)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('试听')
        menuitem.connect('activate', self.listen)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('添加到播放列表')
        #menuitem.connect('activate', self.addlist, selected)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('删除已有下载')
        #menuitem.connect('activate', self.delete, selected)
        popupmenu.append(menuitem)

        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)

    def downone(self, widget):

        selected = self.list_tree.get_selection().get_selected()
        list_model,iter = selected
        num = self.list_model.get_value(iter,COL_NUM)
        artist = self.list_model.get_value(iter, COL_ARTIST)
        title = self.list_model.get_value(iter, COL_TITLE)
        self.down_model.append([num,artist,title,"start"])

        self.notification = pynotify.Notification("下载", self._songlist.get_title(self.path[0]), "dialog-warning")
        self.notification.set_timeout(1)
        self.notification.show()
        thread.start_new_thread(self._songlist.downone, (self.path[0],))

    def listen(self, widget):
        self.notification = pynotify.Notification("试听", self._songlist.get_title(self.path[0]), "dialog-warning")
        self.notification.set_timeout(1)
        self.notification.show()
        thread.start_new_thread(self._songlist.listen, (self.path[0],))

    def click_checker(self, view, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            #selected,iter = view.get_selection().get_selected()
            #index = selected.get_value(iter, 0)
            #print index

            # Here test whether we have songlist, if have, show popup menu
            try:
                if self._songlist:
                    self.SetupPopup()
            except:
                pass

            x = int(event.x)
            y = int(event.y)
            pth = view.get_path_at_pos(x, y)

            if not pth:
                pass
            else:
                self.path, col, cell_x, cell_y = pth

def test():
    print "testing for thread"


def main():
    win = MainWindow();
    gtk.gdk.threads_init()
    gtk.main()


if __name__ == '__main__':
    main()
