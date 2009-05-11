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


import os
import time
import gtk
import gtk.glade
import gmbox
import thread
import downpage


DEBUG=0



(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST,COL_DOWN) = range(5)
(COL_STATUS, COL_NUM, COL_TITLE, COL_ARTIST,COL_ALBUM) = range(5)

class MainWindow():
    def __init__(self):
        self.gladefile="data/gmbox.glade"
        self.xml=gtk.glade.XML(self.gladefile)
        self.window = self.xml.get_widget("window_main")
        self.notebook = self.xml.get_widget("notebook_top")
        

        dic={"on_pbutton_album_clicked":self.btnAlbum_clicked,
             "on_pbutton_down_clicked": self.btnDown_clicked,
             "on_pbutton_list_clicked": self.btnList_clicked,
             "on_pbutton_searched_clicked": self.btnSearched_clicked,
             "on_pbutton_about_clicked": self.btnAbout_clicked,
             "on_button_download_selected_clicked": self.download_selected,
             "on_button_listen_selected_clicked":self.listen_selected,

             "on_search_button_clicked":self.doSearchMusic,
             "on_filelist_button_clicked":self.dolistLocalFile,

             "on_mbutton_previous_clicked":self.tray_play_prev,
             "on_mbutton_play_clicked": self.listen,
             "on_mbutton_pause_clicked": self.pause_music,
             "on_mbutton_next_clicked": self.tray_play_next}
        self.xml.signal_autoconnect(dic)

        self.playbar = self.xml.get_widget("playbar")
        self.playbar.set_text("playing")

        #self.command_entry = self.xml.get_widget("command_entry")

        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)
        #self.window.add_accelerator("hide()",accel_group,ord('w'),gtk.gdk.CONTROL_MASK,0)
        self.current_path=0




    def downList(self,text,widget):
        """Hold song index and prepare for download"""
        self.list_view.get_list(text)
        self.current_list=self.list_view
        #self.list_button.set_sensitive(True)
        widget.set_sensitive(True)

    def doSearch(self,widget):
        """Begin song list download thread"""
        text=widget.get_active_text().decode('utf8')
        if text != "--请选择--":
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

    def dolistLocalFile(self,widget):
        print "while start thread"
        thread.start_new_thread(self.listLocalFile,(widget,))
        print "OK"

    def listLocalFile(self,widget):
        print "in new thread"

        self.current_list = self.file_list_view
        self.file_list_view.get_list()
        widget.set_sensitive(True)
        print "exit thread"

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
        #selected = self.current_list.treeview.get_selection().get_selected()
        #list_model,iter = selected
        #artist = list_model.get_value(iter, COL_ARTIST)
        #title = list_model.get_value(iter, COL_TITLE)
        artist = self.current_list.get_artist(self.current_path)
        title = self.current_list.get_title(self.current_path)
        id = self.current_list.get_id(self.current_path)
        self.down_tree.add(title,artist,id)

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
        '''下载选中的音乐(这里才是批量下载)'''
        pass

    def listen_selected(self):
        '''试听选中的音乐'''
        pass


def test():
    print "testing for thread"

def main():
    gmbox.ConfigFile()
    win = MainWindow();
    if os.name=='posix':
        gtk.gdk.threads_init()
    else:
        pass
    gtk.main()  #增加了else pass之后，自动缩进就不会把这行缩到if里了。。。


if __name__ == '__main__':
    main()
