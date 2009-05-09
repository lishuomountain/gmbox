#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import gtk
import gtk.glade
import gmbox
import thread
import downpage


DEBUG=0

if os.name=='posix':
    import pynotify

(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST,COL_DOWN) = range(5)
(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST,COL_ALBUM) = range(5)
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
             "on_button_download_selected_clicked": self.download_selected,
             "on_button_listen_selected_clicked":self.listen_selected,

             "on_search_button_clicked":self.doSearchMusic,

             "on_mbutton_previous_clicked":self.tray_play_prev,
             "on_mbutton_play_clicked": self.listen,
             "on_mbutton_pause_clicked": self.pause_music,
             "on_mbutton_next_clicked": self.tray_play_next}
        self.xml.signal_autoconnect(dic)

        #page 1 from glade
        self.list_view= ListView(self.xml)
        self.list_view.treeview.connect('button-press-event', self.click_checker)
        self.list_view.treeview.connect('key_press_event', self.tree_view_key_checker)

        hbox = self.xml.get_widget('list_box_for_combox')
        opt = self.xml.get_widget('combobox1')
        opt = gtk.combo_box_new_text()

        [opt.append_text(slist) for slist in self.list_view.songlists]
        opt.connect("changed", self.doSearch, opt)  #自动获取列表
        opt.set_active(0)
        hbox.pack_start(opt, False)

        #self.list_button = self.xml.get_widget('list_button')
        #self.list_button.connect('clicked', self.doSearch, opt)
        self.local_list_button = self.xml.get_widget('local_list_button')
        self.local_list_button.connect('clicked', self.dolistLocalFile, opt)
        
        #page 2: search page
        self.search_entry = self.xml.get_widget('search_entry')
        self.search_entry.connect('key_press_event', self.entry_key_checker)
        self.search_button = self.xml.get_widget('search_button')

        self.search_list_view= SearchListView(self.xml)
        self.search_list_view.treeview.connect('button-press-event', self.click_checker)
        self.search_list_view.treeview.connect('key_press_event', self.tree_view_key_checker)

        #page 3:  downlist page
        self.down_tree = downpage.DownTreeView(self.xml)

        #page 4: playlist page
        self.playlist_view= PlayListView(self.xml)


        #setup system tray icon
        self.setupSystray()


        statusbar = self.xml.get_widget("statusbar")

        self.playbar = self.xml.get_widget("playbar")
        self.playbar.set_text("playing")

        #self.command_entry = self.xml.get_widget("command_entry")

        self.window.set_title("GMBox")
        self.window.set_default_size(800, 600)

        #ui_logo=gtk.gdk.Pixbuf.create_from_xpm("data/gmbox.xpm")
        ui_logo=gtk.gdk.pixbuf_new_from_file("data/gmbox.png")
        self.window.set_icon(ui_logo)

        self.window.connect('destroy', gtk.main_quit)
        self.window.connect('key_press_event', self.key_checker)
        self.window.show_all();
        #self.command_entry.hide()

        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)
        #self.window.add_accelerator("hide()",accel_group,ord('w'),gtk.gdk.CONTROL_MASK,0)
        self.current_path=0
        #self.doSearch(self.list_button,opt)

    def setupSystray(self):
        self.systray = gtk.StatusIcon()
        self.systray.set_from_file("data/gmbox.png")
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
        self.current_list=self.list_view
        
    def btnList_clicked(self,widget):
        self.notebook.set_current_page(3)
        self.current_list=self.playlist_view

    def btnSearched_clicked(self,widget):
        self.notebook.set_current_page(1)
        self.current_list=self.search_list_view

    def btnDown_clicked(self,widget):
        self.notebook.set_current_page(2)
        self.current_list=self.down_tree

    def btnAbout_clicked(self,widget):
        self.notebook.set_current_page(4)

    def downList(self,text,widget):
        """Hold song index and prepare for download"""
        self.list_view.get_list(text)
        self.current_list=self.list_view
        #self.list_button.set_sensitive(True)
        widget.set_sensitive(True)

    def doSearch(self,widget,opt):
        """Begin song list download thread"""
        text=opt.get_active_text().decode('utf8')
        widget.set_sensitive(False)
        thread.start_new_thread(self.downList,(text,widget,))

    def doSearchMusic(self,widget):
        key = self.search_entry.get_text().decode('utf8')
        print key
        self.search_button.set_sensitive(False)
        thread.start_new_thread(self.SearchMusic,(key,))

    def SearchMusic(self,key):
        self.search_list_view.get_list(key)
        self.current_list=self.search_list_view
        self.search_button.set_sensitive(True)

    def dolistLocalFile(self,widget,opt):
        print "while start thread"
        thread.start_new_thread(self.listLocalFile,(gmbox.musicdir,))
        print "OK"
    def listLocalFile(self,path):
        print "in new thread"
        self.local_list_button.set_sensitive(False)
        self.file_list_view = FileListView(path)

        self.currentlist = self.file_list_view
        self.file_list_view.get_list()
        self.local_list_button.set_sensitive(True)
        print "exit thread"

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
                if self.current_list==self._songlist:
                    self.delete_file(widget)
                else:
                    self.DelFromPlaylist(widget)

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
        selected = self.current_list.treeview.get_selection().get_selected()
        list_model,iter = selected
        num = len(self.down_tree.songlist)+1
        #artist = list_model.get_value(iter, COL_ARTIST)
        #title = list_model.get_value(iter, COL_TITLE)
        artist = self.current_list.get_artist(self.current_path)
        title = self.current_list.get_title(self.current_path)
        self.down_tree.down_model.append([num,title,artist,"start"])

        if os.name=='posix':
            self.notification = pynotify.Notification("下载", self.current_list.get_title(self.current_path), "dialog-warning")
        self.notification.set_timeout(1)
        self.notification.show()
        print 'being to download'
        try:
            thread.start_new_thread(self.current_list.downone, (self.current_path,))
        except:
            print "Error"

    def addToPlaylist(self, widget):
        selected = self.current_list.treeview.get_selection().get_selected()
        list_model,iter = selected
        artist = list_model.get_value(iter, COL_ARTIST)
        title = list_model.get_value(iter, COL_TITLE)
        id = self.current_list.get_id(self.current_path)
        self.playlist_view.add(title,artist,str(id))


    def DelFromPlaylist(self, widget):
        selected = self.playlist_tree.get_selection().get_selected()
        list_model,iter = selected
        #num = self.list_model.get_value(iter,COL_NUM)
        num = len(self.playlist.songlist)+1
        #list_model.remove(self.path[0])
        #self.playlist.add(self._songlist.get_title(self.path[0]),self._songlist.get_artist(self.path[0]),str(self.path[0]))
        #id = self.current_list.get_id(self.current_path)
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
            self.notification = pynotify.Notification("试听", self.current_list.get_title(start), "dialog-warning")
            self.notification.set_timeout(1)
            self.notification.show()
        self.playbar.set_text("now playing " + self.current_list.get_title(start))
        print "now playing ",self.current_list.get_title(start)
        self.current_list.play(start)
        #self.current_list.autoplay(start)

    def listen_init(self, widget):
        self.current_list=self.playlist
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
        if self.current_list==self._songlist:
            return self.list_tree
        elif self.current_list==self.playlist:
            return self.playlist_tree
        elif self.current_list==self.search_list:
            return self.search_list_tree

    def pause_music(self,widget):
        pass
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



    def get_current_location(self,view,event):
        x = int(event.x)
        y = int(event.y)
        pth = view.get_path_at_pos(x, y)

        if not pth:
            pass
        else:
            self.path, col, cell_x, cell_y = pth
            self.current_path=self.path[0]
            title = self.current_list.get_title(self.current_path)
            print "选中 ",title

    def get_current_list(self,view,event):
        pass

    def key_checker(self,widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            if event.keyval == ord(':'):
                self.command_entry.show()
                #self.set_cursor(self.command_entry)
            if event.keyval == gtk.keysyms.Escape:
                self.command_entry.hide()

    def entry_key_checker(self,widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            if event.keyval == gtk.keysyms.Return:
                self.doSearchMusic(widget)

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
                if self.current_list==self._songlist:
                    self.delete_file(widget)
                else:
                    self.DelFromPlaylist(widget)

    def download_selected(self):
        pass

    def listen_selected(self):
        pass

class ListView(gmbox.Lists):
    def __init__(self,xml):
        """get hot song list treeview widget"""
        gmbox.Lists.__init__(self)
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.model = gtk.ListStore(str, str, str,str)
        #self.model.connect("row-changed", self.SaveSongIndex)

        self.treeview = xml.get_widget('list_treeview')
        self.treeview.set_model(self.model)
        self.treeview.set_enable_search(0)
        #treeview.bind('<Button-3>', self.click_checker)
        #treeview.bind('<Double-Button-1>', self.listen)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        checkbutton = gtk.CheckButton()
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled)
        column = gtk.TreeViewColumn("选中", renderer,active=COL_STATUS)
        column.set_resizable(True)
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

    def get_list(self,text):
        gmbox.Lists.get_list(self,text)
        self.model.clear()
        [self.model.append([False,self.songlist.index(song)+1,song['title'],song['artist']]) for song in self.songlist]

    def fixed_toggled(self, cell, path):
        # get toggled iter
        iter = self.model.get_iter((int(path),))
        fixed = self.model.get_value(iter, COL_STATUS)
        print "fixed is ",fixed

        # do something with the value
        fixed = not fixed

        print "now fixed is ",fixed

        if not fixed:
            print 'Select[row]:',path
        else:
            print 'Invert Select[row]:',path

        # set new value
        self.model.set(iter, COL_STATUS, fixed)        

class PlayListView(gmbox.PlayList):
    def __init__(self,xml):
        gmbox.PlayList.__init__(self)
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.model = gtk.ListStore(str, str, str)
        #self.model.connect("row-changed", self.SaveSongIndex)
        
        self.treeview = xml.get_widget("playlist_treeview")
        self.treeview.set_model(self.model)
        self.treeview.set_enable_search(0)
        #self.treeview.connect('button-press-event', self.playlist_click_checker)
        #self.treeview.connect('key_press_event', self.tree_view_key_checker)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
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

        self.model.clear()
        [self.model.append([self.songlist.index(song)+1,song['title'],song['artist']]) for song in self.songlist]

    def add(self,title,artist,id):
        gmbox.PlayList.add(self,title,artist,id)
        num = len(self.songlist)+1
        self.model.append([num,title,artist])
        if os.name=='posix':
            notification = pynotify.Notification("添加到播放列表", title, "dialog-warning")
            notification.set_timeout(1)
            notification.show()

class SearchListView(gmbox.SearchLists):
    def __init__(self,xml):
        gmbox.SearchLists.__init__(self)
        """get hot song list treeview widget"""
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.model = gtk.ListStore(str, str, str,str)
        #self.list_model.connect("row-changed", self.SaveSongIndex)
        
        self.treeview = xml.get_widget('search_treeview')
        self.treeview.set_model(self.model)
        self.treeview.set_enable_search(0)
        #treeview.bind('<Button-3>', self.click_checker)
        #treeview.bind('<Double-Button-1>', self.listen)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        checkbutton = gtk.CheckButton()
        renderer = gtk.CellRendererToggle()
        column = gtk.TreeViewColumn("选中", renderer)
        column.set_resizable(True)
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

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COL_ALBUM)
        renderer.set_property('editable', False)
       #renderer.connect("edited", self.on_cell_edited, None)
        column = gtk.TreeViewColumn("专辑", renderer, text=COL_ALBUM)
        column.set_resizable(True)
        self.treeview.append_column(column)
        self.treeview.set_rules_hint(True)

    def get_list(self,key):
        gmbox.SearchLists.get_list(self,key)
        self.model.clear()
        [self.model.append([self.songlist.index(song)+1,song['title'],song['artist'],song['album']]) for song in self.songlist]

class FileListView(gmbox.FileList):
    def __init__(self,xml):
        """get hot song list treeview widget"""
        gmbox.FileList.__init__(self)
        #依次存入：歌曲编号，歌曲名，歌手，专辑，长度，url
        self.model = gtk.ListStore(str, str, str,str)
        #self.model.connect("row-changed", self.SaveSongIndex)

        self.treeview = xml.get_widget('list_treeview')
        self.treeview.set_model(self.model)
        self.treeview.set_enable_search(0)
        #treeview.bind('<Button-3>', self.click_checker)
        #treeview.bind('<Double-Button-1>', self.listen)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        checkbutton = gtk.CheckButton()
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled)
        column = gtk.TreeViewColumn("选中", renderer,active=COL_STATUS)
        column.set_resizable(True)
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

    def get_list(self):
        print "debug info 1"
        self.model.clear()
        print "debug info 2"
        for song in self.songlist:
            print "adding",song['title'],
            self.list_model.append(
                [str(self.songlist.index(song)+1),song['title'],song['artist']])
            print "done!"
        print "debug info"

    def fixed_toggled(self, cell, path):
        # get toggled iter
        iter = self.model.get_iter((int(path),))
        fixed = self.model.get_value(iter, COL_STATUS)
        print "fixed is ",fixed

        # do something with the value
        fixed = not fixed

        print "now fixed is ",fixed

        if not fixed:
            print 'Select[row]:',path
        else:
            print 'Invert Select[row]:',path

        # set new value
        self.model.set(iter, COL_STATUS, fixed)        

def test():
    print "testing for thread"

def main():
    gmbox.ConfigFile()
    win = MainWindow();
    if os.name=='posix':
        gtk.gdk.threads_init()
        gtk.main()


if __name__ == '__main__':
    main()
