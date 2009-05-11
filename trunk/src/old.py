

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





    def SearchMusic(self,key):
        self.search_list_view.get_list(key)
        self.current_list=self.search_list_view
        self.search_button.set_sensitive(True)



    def listLocalFile(self,widget):
        print "in new thread"

        self.current_list = self.file_list_view
        self.file_list_view.get_list()
        widget.set_sensitive(True)
        print "exit thread"


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
