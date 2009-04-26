#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import gtk
import gtk.glade
import gmbox
import thread


DEBUG=0

if os.name=='posix':
    import pynotify

(COL_NUM, COL_TITLE, COL_ARTIST,COL_DOWN) = range(4)
class MainWindow():
    def __init__(self):

        self.gladefile="data/gmbox.glade"
        self.xml=gtk.glade.XML(self.gladefile)
        self.window = self.xml.get_widget("window_main")
        self.notebook = self.xml.get_widget("notebook_top")
        self.notebook.set_show_tabs(False)

        dic={"on_pbutton_album_clicked":self.btnAlbum_clicked,
             "on_pbutton_down_clicked": self.btnDown_clicked,
             "on_pbutton_list_clicked": self.btnList_clicked,
             "on_pbutton_searched_clicked": self.btnSearched_clicked,
             "on_pbutton_about_clicked": self.btnAbout_clicked,

             "on_mbutton_previous_clicked":self.tray_play_prev,
             "on_mbutton_play_clicked": self.listen,
             "on_mbutton_pause_clicked": self.pause_music,
             "on_mbutton_next_clicked": self.tray_play_next}
        self.xml.signal_autoconnect(dic)

        #page 1
        vbox= self.xml.get_widget("vbox_p1")
        hbox = gtk.HBox()
        opt = gtk.combo_box_new_text()
        self._songlist = gmbox.Lists()
        for slist in self._songlist.get_songlists():
            opt.append_text(slist)
        opt.set_active(0)
        hbox.pack_start(opt, False)
        self.list_button = gtk.Button('获取列表')
        size = self.list_button.size_request()
        self.list_button.set_size_request(size[0]+50, -1)
        opt.set_size_request(size[0]+150, -1)
        self.list_button.connect('clicked', self.doSearch, opt)
        hbox.pack_start(self.list_button, False)

        self.local_list_button = gtk.Button('本地歌曲列表')
        size = self.local_list_button.size_request()
        self.local_list_button.set_size_request(size[0]+50, -1)
        opt.set_size_request(size[0]+150, -1)
        self.local_list_button.connect('clicked', self.dolistLocalFile, opt)
        hbox.pack_start(self.local_list_button, False)

        vbox.pack_start(hbox, False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.list_tree = self.getListTreeView()
        self.list_tree.set_rules_hint(True)
        scroll.add(self.list_tree)
        vbox.pack_start(scroll)


        #page playlist
        playlist_vbox= self.xml.get_widget("vbox_p4")
        
        playlist_scroll = gtk.ScrolledWindow()
        playlist_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        playlist_scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.playlist_tree = self.getPlaylistTreeView()
        self.playlist_tree.set_rules_hint(True)
        playlist_scroll.add(self.playlist_tree)
        playlist_vbox.pack_start(playlist_scroll)



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

        statusbar = self.xml.get_widget("statusbar")

        button = self.xml.get_widget("mbutton_previous")
        #button.add(image)
        #statusbar.add(button)

        #button = self.xml.get_widget("mbutton_play")
        #button = gtk.Button()
        #image=gtk.Image()
        #image.set_from_file("images/media-play.png")
        #button.add(image)
        #statusbar.add(button)

        #button= self.xml.get_widget("mbutton_pause")
        #button = gtk.Button()
        #image=gtk.Image()
        #image.set_from_file("images/media-pause.png")
        #button.add(image)
        #statusbar.add(button)

        #button = self.xml.get_widget("mbutton_next")
        #button = gtk.Button()
        #image=gtk.Image()
        #image.set_from_file("images/media-next.png")
        #button.add(image)
        #statusbar.add(button)

        logo = self.xml.get_widget("logo")

        self.playbar = self.xml.get_widget("playbar")
        self.playbar.set_text("playing")

        self.window.set_title("GMBox")
        self.window.set_default_size(800, 600)
        self.window.connect('destroy', gtk.main_quit)
        self.window.connect('key_press_event', self.key_checker)
        self.window.show_all();

        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)
        #self.window.add_accelerator("hide()",accel_group,ord('w'),gtk.gdk.CONTROL_MASK,0)
        self.current_path=0

    def setupSystray(self):
        self.systray = gtk.StatusIcon()
        self.systray.set_from_file("data/systray.png")
        self.systray.connect("activate", self.systrayCb)
        self.systray.connect('popup-menu', self.systrayPopup)
        self.systray.set_tooltip("Click to toggle window visibility")
        self.systray.set_visible(True)

        if os.name=='posix':
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
        popup_menu.append(restore_item)

        prev_item = gtk.MenuItem("Previous")
        prev_item.connect("activate", self.tray_play_prev)
        popup_menu.append(prev_item)

        next_item = gtk.MenuItem("Next")
        next_item.connect("activate", self.tray_play_next)
        popup_menu.append(next_item)

        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", gtk.main_quit)
        popup_menu.append(quit_item)

        popup_menu.show_all()
        time = gtk.get_current_event_time()
        popup_menu.popup(None, None, None, 0, time)
        

    def btnAlbum_clicked(self,widget):
        self.notebook.set_current_page(0)
        
    def btnList_clicked(self,widget):
        self.notebook.set_current_page(3)
        self.currentlist=self.playlist

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
        return treeview

    def downList(self,text):
        """Hold song index and prepare for download"""
        self._songlist = gmbox.Lists()
        self._songlist.get_list(text)
        self.list_model.clear()
        for song in self._songlist.songlist:
            self.list_model.append(
                [self._songlist.songlist.index(song)+1,song['title'],song['artist']])
        self.currentlist=self._songlist
        self.list_button.set_sensitive(True)

    def doSearch(self,widget,opt):
        """Begin song list download thread"""
        
        text=opt.get_active_text().decode('utf8')
        self.list_button.set_sensitive(False)
        thread.start_new_thread(self.downList,(text,))

    def dolistLocalFile(self,widget,opt):
        thread.start_new_thread(self.listLocalFile,(gmbox.musicdir,))
    def listLocalFile(self,path):
        self.local_list_button.set_sensitive(False)
        self._songlist = gmbox.FileList(path)
        #self._songlist = gmbox.Lists("华语热歌")
        self.currentlist = self._songlist
        self.list_model.clear()
        for song in self._songlist.songlist:
            self.list_model.append(
                [self._songlist.songlist.index(song)+1,song['title'],song['artist']])
        self.local_list_button.set_sensitive(True)

    def getListTreeView(self):
        """get hot song list treeview widget"""
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.list_model = gtk.ListStore(str, str, str)
        #self.list_model.connect("row-changed", self.SaveSongIndex)

        
        treeview = gtk.TreeView(self.list_model)
        treeview.set_enable_search(0)
        treeview.connect('button-press-event', self.click_checker)
        treeview.connect('key_press_event', self.tree_view_key_checker)
        #treeview.bind('<Button-3>', self.click_checker)
        #treeview.bind('<Double-Button-1>', self.listen)
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


    def getPlaylistTreeView(self):
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.playlist_model = gtk.ListStore(str, str, str)
        #self.model.connect("row-changed", self.SaveSongIndex)

        
        treeview = gtk.TreeView(self.playlist_model)
        treeview.set_enable_search(0)
        treeview.connect('button-press-event', self.playlist_click_checker)
        treeview.connect('key_press_event', self.tree_view_key_checker)
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


        self.playlist = gmbox.PlayList()
        self.playlist_model.clear()
        for song in self.playlist.songlist:
            self.playlist_model.append(
                [self.playlist.songlist.index(song)+1,song['title'],song['artist']])

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
        menuitem.connect('activate', self.addToPlaylist)
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('删除已有下载')
        menuitem.connect('activate', self.delete_file)
        popupmenu.append(menuitem)

        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)

    def SetupPopup2(self):
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

    def downone(self, widget):
        selected = self.list_tree.get_selection().get_selected()
        list_model,iter = selected
        num = self.list_model.get_value(iter,COL_NUM)
        artist = self.list_model.get_value(iter, COL_ARTIST)
        title = self.list_model.get_value(iter, COL_TITLE)
        self.down_model.append([num,title,artist,"start"])

        if os.name=='posix':
            self.notification = pynotify.Notification("下载", self._songlist.get_title(self.current_path), "dialog-warning")
        self.notification.set_timeout(1)
        self.notification.show()
        print 'being to download'
        try:
            thread.start_new_thread(self._songlist.downone, (self.current_path,))
        except:
            print "Error"

    def addToPlaylist(self, widget):
        selected = self.list_tree.get_selection().get_selected()
        list_model,iter = selected
        #num = self.list_model.get_value(iter,COL_NUM)
        num = len(self.playlist.songlist)+1
        artist = self.list_model.get_value(iter, COL_ARTIST)
        title = self.list_model.get_value(iter, COL_TITLE)
        self.playlist_model.append([num,title,artist])
        #self.playlist.add(self._songlist.get_title(self.path[0]),self._songlist.get_artist(self.path[0]),str(self.path[0]))
        id = self.currentlist.get_id(self.current_path)
        self.playlist.add(title,artist,str(id))

        if os.name=='posix':
            self.notification = pynotify.Notification("添加到播放列表", self._songlist.get_title(self.current_path), "dialog-warning")
            self.notification.set_timeout(1)
            self.notification.show()

    def DelFromPlaylist(self, widget):
        selected = self.playlist_tree.get_selection().get_selected()
        list_model,iter = selected
        #num = self.list_model.get_value(iter,COL_NUM)
        num = len(self.playlist.songlist)+1
        #self.playlist_model.remove(self.path[0])
        #self.playlist.add(self._songlist.get_title(self.path[0]),self._songlist.get_artist(self.path[0]),str(self.path[0]))
        #id = self.currentlist.get_id(self.current_path)
        self.playlist.delete(self.current_path)

        if os.name=='posix':
            self.notification = pynotify.Notification("从播放列表删除", self.playlist.get_title(self.current_path), "dialog-warning")
            self.notification.set_timeout(1)
            self.notification.show()
    def listen(self, widget):
        try:
            thread.start_new_thread(self.play,(self.current_path,))
        except:
            print "Error"

    def play(self,start):
        '''试听,播放'''
        if os.name=='posix':
            self.notification = pynotify.Notification("试听", self.currentlist.get_title(start), "dialog-warning")
            self.notification.set_timeout(1)
            self.notification.show()
        self.playbar.set_text("now playing " + self.currentlist.get_title(start))
        #self.currentlist.play(start)
        self.currentlist.autoplay(start)

    def listen_init(self, widget):
        self.currentlist=self.playlist
        self.current_path=self.path[0]
        self.listen(widget)

    def focus_next(self,widget):
        self.current_path= self.current_path + 1
        widget.set_cursor(self.current_path)
        if DEBUG:
            print "now focus",self.current_path
    def focus_prev(self,widget):
        self.current_path= self.current_path - 1
        widget.set_cursor(self.current_path)
        if DEBUG:
            print "now focus",self.current_path

    def play_next(self,widget):
        #widget.focus_next(widget)
        self.focus_next(widget)
        self.listen(widget)
        if DEBUG:
            print "now playing",self.current_path
    def play_prev(self,widget):
        #widget.focus_prev(widget)
        self.focus_prev(widget)
        self.listen(widget)
        if DEBUG:
            print "now playing",self.current_path

    def tray_play_next(self,widget):
        current_treeview = self.get_current_treeview()
        self.play_next(current_treeview)

    def tray_play_prev(self,widget):
        current_treeview = self.get_current_treeview()
        self.play_prev(current_treeview)

    def get_current_treeview(self):
        if self.currentlist==self._songlist:
            return self.list_tree
        elif self.currentlist==self.playlist:
            return self.playlist_tree

    def pause_music(self,widget):
        pass
    def click_checker(self, view, event):
        '''榜单页，下载页击键处理'''
        self.get_current_locatioin(view,event)
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.listen(view)

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

    def delete_file(self,event):
        self._songlist.delete_file(self.current_path)

        selected = self.list_tree.get_selection().get_selected()
        list_model,iter = selected
        #num = self.list_model.get_value(iter,COL_NUM)
        num = len(self.playlist.songlist)+1
        artist = self.list_model.get_value(iter, COL_ARTIST)
        title = self.list_model.get_value(iter, COL_TITLE)
        #self.list_model.remove()
        #self.playlist.add(self._songlist.get_title(self.path[0]),self._songlist.get_artist(self.path[0]),str(self.path[0]))
        self._songlist.delete_file(self.current_path)


    def playlist_click_checker(self, view, event):
        self.get_current_locatioin(view,event)

        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.listen(view)

        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            #selected,iter = view.get_selection().get_selected()
            #index = selected.get_value(iter, 0)
            #print index

            # Here test whether we have songlist, if have, show popup menu
            try:
                if self.playlist:
                    self.SetupPopup2()
            except:
                pass

    def get_current_locatioin(self,view,event):
        x = int(event.x)
        y = int(event.y)
        pth = view.get_path_at_pos(x, y)

        if not pth:
            pass
        else:
            self.path, col, cell_x, cell_y = pth
            self.current_path=self.path[0]
            title = self.currentlist.get_title(self.current_path)
            print "选中 ",title

    def key_checker(self,widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            if event.keyval == ord('h'):
                self.window.hide()

    def tree_view_key_checker(self,widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            if event.keyval == ord('n'):
                self.play_next(widget)
            if event.keyval == ord('p'):
                self.play_prev(widget)
            if event.keyval == gtk.keysyms.space:
                self.listen(widget)
            if event.keyval == gtk.keysyms.Return:
                self.listen(widget)
            if event.keyval == ord('j'):
                self.focus_next(widget)
            if event.keyval == ord('k'):
                self.focus_prev(widget)
            if event.keyval == ord('a'):
                self.addToPlaylist(widget)
            if event.keyval == ord('d'):
                if self.currentlist==song._songlist:
                    self.delete_file(widget)
                else:
                    self.DelFromPlaylist(widget)
def test():
    print "testing for thread"


def main():
    win = MainWindow();
    if os.name=='posix':
        gtk.gdk.threads_init()
    gtk.main()


if __name__ == '__main__':
    main()
