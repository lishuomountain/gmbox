#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core import *
from const import *
from test import *
from config import *
from pages import *
from treeviews import *
import sys
import pango
import thread
import subprocess
import traceback

class GmBox():
    
    def __init__(self):
  
        builder = gtk.Builder()
        builder.add_from_file(MODULE_PATH + "/gmbox.glade")
        builder.connect_signals(self)
        for widget in builder.get_objects():
            if issubclass(type(widget), gtk.Buildable):
                name = gtk.Buildable.get_name(widget)
                setattr(self, name, widget)

        # global variables
        self.result_pages = {}
        self.clipboard = gtk.Clipboard()

        # init widget data                
        self.init_mainwin()
        self.init_info_textview()
        self.init_category_treeview()
        self.init_screener_widgets()
        self.init_result_notebook()
        self.init_playlist_treeview()
        self.init_downlist_treeview()
        self.init_preferences_widgets()
        self.init_player_widgets()
        self.init_status_icon()
        
        self.init_not_done_yet()

    # gui setup functions         
    def init_mainwin(self):
        
        # main window
        self.mainwin.hided = False
        
        # main panel
        self.sidebar_vbox.hided = False
        self.info_vbox.hided = False
        self.info_vbox.hide()
        
        # sidebar panels
        self.search_vbox.hided = False
        self.category_vbox.hided = False
        #self.screener_vbox.hided = False
        self.screener_vbox.hide()
        self.screener_vbox.hided = True
        
        # window title and icon
        self.mainwin.set_title("谷歌音乐盒 - 0.4 alpha")
        self.mainwin.set_icon(ICON_DICT["gmbox"])
        
    def init_info_textview(self):
        self.info_textview.modify_font(pango.FontDescription("Mono"))
        self.info_textview.set_editable(False)
        self.info_textbuffer = self.info_textview.get_buffer()
        
    def init_category_treeview(self):
        # remove the children add in glade
        widgets = self.category_scrolledwindow.get_children()
        for widget in widgets:
            self.category_scrolledwindow.remove(widget)
            
        # ceate treeview manualy
        category_treeview = CategoryTreeview(self)
        self.category_scrolledwindow.add(category_treeview)
        self.category_scrolledwindow.show_all()
        
    def init_screener_widgets(self):
        tempo_adjustment = gtk.Adjustment(value=50, upper=100)
        pitch_adjustment = gtk.Adjustment(value=50, upper=100)
        timbre_adjustment = gtk.Adjustment(value=50, upper=100)
        date_adjustment = gtk.Adjustment(value=50, upper=100)

        self.tempo_hscale.set_adjustment(tempo_adjustment)
        self.pitch_hscale.set_adjustment(pitch_adjustment)
        self.timbre_hscale.set_adjustment(timbre_adjustment)
        self.date_hscale.set_adjustment(date_adjustment)
        
    def init_result_notebook(self):
        page_text = "空白"
        page_key = "empty"
        empty_result_page = ResultPage(self)
        empty_result_page_label = ResultPageLabel(empty_result_page, page_text, page_key)
        self.result_pages[page_key] = (empty_result_page, empty_result_page_label)
        # replace glade holder page
        self.result_notebook.remove_page(0)
        self.result_notebook.append_page(empty_result_page, empty_result_page_label)
        
    def init_playlist_treeview(self):
        # remove the children add in glade
        widgets = self.playlist_scrolledwindow.get_children()
        for widget in widgets:
            self.playlist_scrolledwindow.remove(widget)
            
        # ceate treeview manualy
        self.playlist_treeview = PlaylistTreeview(self)
        self.playlist_scrolledwindow.add(self.playlist_treeview)
        self.playlist_scrolledwindow.show_all()
        
    def init_downlist_treeview(self):
        # remove the children add in glade
        widgets = self.downlist_scrolledwindow.get_children()
        for widget in widgets:
            self.downlist_scrolledwindow.remove(widget)
            
        # ceate treeview manualy
        self.downlist_treeview = DownlistTreeview(self)
        self.downlist_scrolledwindow.add(self.downlist_treeview)
        self.downlist_scrolledwindow.show_all()
        
    def init_preferences_widgets(self):
        self.file_chooser_dialog = gtk.FileChooserDialog("选择一个文件", None,
                                   gtk.FILE_CHOOSER_ACTION_OPEN,
                                   (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                                   gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.folder_chooser_dialog = gtk.FileChooserDialog("选择一个文件夹", None,
                                   gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                   (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                                   gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        load_config_file()
        self.update_player_widgets()
        self.update_preferences_widgets()
        
    def init_player_widgets(self):
        play_process_adjustment = gtk.Adjustment(value=0, upper=100)
        self.play_process_hscale.set_adjustment(play_process_adjustment)
    
    def init_status_icon(self):
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_pixbuf(ICON_DICT["gmbox"])
        self.status_icon.connect("activate", self.on_status_icon_activate)
        self.status_icon.set_visible(CONFIG["show_status_icon"])
        
    def init_not_done_yet(self):                
        # win32 mpg123 not usable
        if sys.platform == "win32":
            self.player_internal_radiobutton.set_sensitive(False)
            self.player_external_radiobutton.set_active(True)
            
        # song detail
        self.view_detail_menuitem.hide() 
        self.menuitem5.hide()

    def update_preferences_widgets(self):        
        # regular
        self.download_folder_entry.set_text(CONFIG["download_folder"])
        self.filename_template_entry.set_text(CONFIG["filename_template"])        
        self.download_cover_checkbutton.set_active(CONFIG["download_cover"])
        self.download_lyric_checkbutton.set_active(CONFIG["download_lyric"])
        self.show_status_icon_checkbutton.set_active(CONFIG["show_status_icon"])
        
        # player
        self.player_internal_radiobutton.set_active(CONFIG["player_use_internal"])
        self.player_external_radiobutton.set_active(not CONFIG["player_use_internal"])
        self.player_path_entry.set_text(CONFIG["player_path"])
        self.player_single_entry.set_text(CONFIG["player_single"])        
        self.player_multi_entry.set_text(CONFIG["player_multi"])
        
        # downloader
        self.downloader_internal_radiobutton.set_active(CONFIG["downloader_use_internal"])
        self.downloader_external_radiobutton.set_active(not CONFIG["downloader_use_internal"])
        self.downloader_path_entry.set_text(CONFIG["downloader_path"])
        self.downloader_single_entry.set_text(CONFIG["downloader_single"])        
        self.downloader_multi_entry.set_text(CONFIG["downloader_multi"])    
            
    def update_status_icon(self):     
        self.status_icon.set_visible(CONFIG["show_status_icon"])

    def update_player_widgets(self):        
        # hide or display player control
        if CONFIG["player_use_internal"]:
            self.player_vseparator.show()
            self.player_hbox.show()
        else:
            self.stop_player()
            self.player_vseparator.hide()
            self.player_hbox.hide()

    def update_player_process_hscale(self):
        self.play_process_hscale.set_value(self.player.song.play_process)
        return self.player_running.isSet()

    def print_message(self, text):
        context_id = self.statusbar.get_context_id("context_id")
        self.statusbar.push(context_id, text)
        iter = self.info_textbuffer.get_end_iter()
        info_text = "%s %s\n" % (time.strftime("%H:%m:%S"), text)
        self.info_textbuffer.insert(iter, info_text)
        
    def create_result_page(self, target, arg, page_text, page_key):
        # need to remove the empty result page
        empty_result_page = self.result_pages["empty"][0]
        if self.result_notebook.page_num(empty_result_page) != -1:
            self.result_notebook.remove(empty_result_page)
        
        # create result page
        result_page = ResultPage(self)
        result_page_label = ResultPageLabel(result_page, page_text, page_key)
        result_page_label.connect("button-press-event", self.on_result_notebook_tab_button_press_event)

        self.result_pages[page_key] = (result_page, result_page_label)
        index = self.result_notebook.append_page(result_page, result_page_label)
        self.result_notebook.set_current_page(index)
        
        # then call core to get result
        try:
            if arg is None:
                result = target()
            else:
                result = target(arg)   
        except Exception, error:
            traceback.print_exc()
            result_page.load_message("遇到错误：%s" % str(error))
            # remove from result dict for retry
            self.result_pages.pop(page_key)
        else:
            if isinstance(result, Songlist):
                length = len(result.songs)
            else:
                length = len(result.songlists)
            
            if length == 0:
                result_page.load_message("找不到和查询条件相符的音乐")
            else:
                result_page.load_result(result)

    def find_result_page(self, page_key):
        # switch to reslut page
        self.main_notebook.set_current_page(0)
        
        if self.result_pages.has_key(page_key):            
            # need to remove the empty result page
            empty_result_page = self.result_pages["empty"][0]
            if self.result_notebook.page_num(empty_result_page) != -1:
                self.result_notebook.remove(empty_result_page)
            
            # reuse result page
            result_page, result_page_label = self.result_pages[page_key]
            index = self.result_notebook.page_num(result_page)
            if index == -1:
                # not in notebook, append it again                
                index = self.result_notebook.append_page(result_page, result_page_label)
            self.result_notebook.set_current_page(index)
            return True
        else:
            return False
        
    def do_search(self, text, type):
        if type == "song":
            self.print_message('搜索歌曲“%s”。' % text)
            page_text = text
            page_key = "search_song:%s" % text
            if not self.find_result_page(page_key):
                thread.start_new_thread(self.create_result_page, (Search, text, page_text, page_key))
        elif type == "album":
            self.print_message('搜索专辑“%s”。' % text)
            page_text = text
            page_key = "search_album:%s" % text
            if not self.find_result_page(page_key):
                thread.start_new_thread(self.create_result_page, (DirSearch, text, page_text, page_key))
        else: # artist
            self.print_message('搜索歌手“%s”。' % text)
            page_text = text
            page_key = "search_artist:%s" % text
            if not self.find_result_page(page_key):
                thread.start_new_thread(self.create_result_page, (DirArtist, text, page_text, page_key))
     
    def do_chartlisting(self, name, type):
        # find id from name
        for chartlisting in CHARTLISTING_DIR:
            if chartlisting[0] == name:
                id = chartlisting[1]
                break
        
        self.print_message('获取排行榜“%s”。' % name)
        page_text = name
        page_key = "chartlisting:%s" % id
        if not self.find_result_page(page_key):
            if type == Song:
                thread.start_new_thread(self.create_result_page, (Chartlisting, id, page_text, page_key))
            else:
                thread.start_new_thread(self.create_result_page, (DirChartlisting, id, page_text, page_key)) 
    
    def do_tag(self, name, type):
        if type == Song:
            self.print_message('搜索歌曲标签“%s”。' % name)
            page_text = name
            page_key = "tag_song:%s" % name
            if not self.find_result_page(page_key):
                thread.start_new_thread(self.create_result_page, (Tag, name, page_text, page_key))
        else:
            self.print_message('正在搜索专题标签“%s”。' % name)
            page_text = name
            page_key = "tag_topic:%s" % name
            if not self.find_result_page(page_key):
                thread.start_new_thread(self.create_result_page, (DirTag, name, page_text, page_key))
            
    def do_topiclistingdir(self):
        self.print_message('获取最新专题。')
        page_text = "最新专题"
        page_key = "topiclistingdir"
        if not self.find_result_page(page_key):
            thread.start_new_thread(self.create_result_page, (DirTopiclistingdir, None, page_text, page_key))
      
    def do_starrecommendationdir(self):
        self.print_message('获取大牌私房歌。')        
        page_text = "私房歌"
        page_key = "starrecommendationdir"
        if not self.find_result_page(page_key):
            thread.start_new_thread(self.create_result_page, (DirStarrecc, None, page_text, page_key))
  
    def do_screener(self, args_dict):           
        simple_hash = ";".join(["%s:%s" % (key, value) for key, value in args_dict.items()])
        self.print_message('获取挑歌结果。')
        page_text = "挑歌"
        page_key = "screener:%s" % simple_hash
        if not self.find_result_page(page_key):
            # reuse result page
            if self.reuse_result_tab_checkbutton.get_active():
                result_page_index = self.result_notebook.get_current_page()
                result_page = self.result_notebook.get_nth_page(result_page_index)
                result_page_label = self.result_notebook.get_tab_label(result_page)
                is_last_page = (self.result_notebook.get_n_pages() - result_page_index) == 1
                if result_page_label.page_key.startswith("screener") and is_last_page:
                    self.result_notebook.remove(result_page)
            thread.start_new_thread(self.create_result_page, (Screener, args_dict, page_text, page_key))
        
    def do_similar(self, id, name):
        self.print_message('获取“%s”的相似歌曲。' % name)
        page_text = name
        page_key = "similar:%s" % id
        if not self.find_result_page(page_key):
            thread.start_new_thread(self.create_result_page, (Similar, id, page_text, page_key))
        
    def do_artist_song(self, id, name):        
        self.print_message('获取“%s”的热门歌曲。' % name)
        page_text = name
        page_key = "artist_song:%s" % id
        if not self.find_result_page(page_key):
            thread.start_new_thread(self.create_result_page, (ArtistSong, id, page_text, page_key))
        
    def do_artist_album(self, id, name):
        self.print_message('获取“%s”的专辑。' % name)
        page_text = name
        page_key = "artist_album:%s" % id
        if not self.find_result_page(page_key):
            thread.start_new_thread(self.create_result_page, (DirArtistAlbum, id, page_text, page_key))
        
    def do_album(self, id, name):        
        self.print_message('获取专辑"%s"的歌曲。' % name)
        page_text = name
        page_key = "album：%s" % id
        if not self.find_result_page(page_key):
            thread.start_new_thread(self.create_result_page, (Album, id, page_text, page_key))   
        
    def popup_content_menu(self, songs, event, caller):
        self.selected_songs = songs
        
        # show last time hided widget
        self.down_menuitem.show()
        self.playlist_menuitem.show()
        self.playlist_remove_menuitem.hide()
        self.playlist_clear_menuitem.hide()
        self.downlist_menuitem.show()
        self.downlist_remove_menuitem.hide()
        self.downlist_clear_menuitem.hide()

        # hide menuitem in difference treeview
        if isinstance(caller, PlaylistTreeview):
            self.playlist_menuitem.hide()
            self.playlist_remove_menuitem.show()
            self.playlist_clear_menuitem.show()

        if isinstance(caller, DownlistTreeview):
            self.downlist_menuitem.hide()
            self.downlist_remove_menuitem.show()
            self.downlist_clear_menuitem.show()
            
        if CONFIG["downloader_use_internal"]:
            self.downlist_menuitem.hide()

        if isinstance(caller, DownlistTreeview) and CONFIG["downloader_use_internal"]:
            self.down_menuitem.hide()

        self.content_menu.popup(None, None, None, event.button, event.time) 

    def start_player(self, song):
        self.player_running = threading.Event()
        self.player_running.set()
        self.player = Player(song, self.player_running, self.player_callback)
        self.player.start()
        
        self.player.song.play_status = "播放中"
        self.player.song.play_process = 0
        self.playlist_treeview.queue_draw()
        
        self.playing = True
        self.play_button.set_label("暂停")

        # add update time inforamtion function
        gobject.timeout_add(1000, self.update_player_process_hscale)
        
    def stop_player(self):
        if hasattr(self, "player_running"):
            self.player_running.clear()
            self.player.song.play_status = ""
            self.player.song.play_process = 0
            self.playlist_treeview.queue_draw()
            self.playing = False
            self.play_button.set_label("播放")
                    
    def player_callback(self, song):
        self.player.song.play_status = ""
        self.player.song.play_process = 0
        self.playlist_treeview.queue_draw()
        song = self.playlist_treeview.get_next_song(song)
        self.start_player(song)

    def play_songs(self, songs):
        self.add_to_playlist(songs, False)
        if CONFIG["player_use_internal"]:
                self.stop_player()
                self.start_player(songs[0])
        else: # user external player
            player = CONFIG["player_path"]
            if player == "":
                self.print_message("未设置播放器。")
                return
         
            if len(songs) == 1:
                cmd = [player]
                cmd.extend(CONFIG["player_single"].split())
                song = songs[0]
                url = song.songUrl.decode("utf-8").encode(sys.getfilesystemencoding())
                if "${URL}" in cmd:
                    cmd[cmd.index("${URL}")] = url
                subprocess.Popen(cmd)
            else:
                cmd = [player]
                cmd.extend(CONFIG["player_multi"].split())
                urls = []
                for song in songs:
                    url = song.songUrl.decode("utf-8").encode(sys.getfilesystemencoding())
                    urls.append(url)
                if "${URLS}" in cmd:
                    index = cmd.index("${URLS}")
                    temp_cmd = cmd[:index]
                    temp_cmd.extend(urls)
                    temp_cmd.extend(cmd[index + 1:])
                    cmd = temp_cmd
                subprocess.Popen(cmd)
                
    def down_songs(self, songs):

        self.add_to_downlist(songs)
            
        # choose downloader
        if CONFIG["downloader_use_internal"]:
            self.downlist_treeview.start_downloader()
        else: # user external downloader  
            downloader = CONFIG["downloader_path"]
            if downloader == "":
                self.print_message("未设置下载程序。")
                return
            
            self.get_songs_urls(songs, "download")
            if CONFIG["download_lyric"] or CONFIG["download_cover"]:
                self.get_songs_urls(songs, "stream")
            
            download_folder = CONFIG["download_folder"]
            if download_folder.endswith("/"):
                download_folder = download_folder[:-1]

            if len(songs) == 1:
                cmd = [downloader]
                cmd.extend(CONFIG["downloader_single"].split())
                song = songs[0]
                url = song.downloadUrl.decode("utf-8").encode(sys.getfilesystemencoding())
                if "${URL}" in cmd:
                    cmd[cmd.index("${URL}")] = url
                
                # make save file full path
                filename = CONFIG["filename_template"].replace("${ALBUM}", song.album)
                filename = filename.replace("${ARTIST}", song.artist)
                filename = filename.replace("${TITLE}", song.name)
                if "${TRACK}" in filename:
                    # need to load stearm info
                    self.get_songs_urls([song], "stream")
                    filename = filename.replace("${TRACK}", song.providerId[-2:])
                filepath = "%s/%s.mp3" % (download_folder, filename) 
                               
                if "${FILEPATH}" in cmd:
                    cmd[cmd.index("${FILEPATH}")] = filepath

                print cmd
                subprocess.Popen(cmd, cwd=download_folder)
            else:
                cmd = [downloader]
                cmd.extend(CONFIG["downloader_multi"].split())
                urls = []
                for song in songs:
                    url = song.downloadUrl.decode("utf-8").encode(sys.getfilesystemencoding())
                    urls.append(url)
                if "${URLS}" in cmd:
                    index = cmd.index("${URLS}")
                    temp_cmd = cmd[:index]
                    temp_cmd.extend(urls)
                    temp_cmd.extend(cmd[index + 1:])
                    cmd = temp_cmd
                print cmd
                subprocess.Popen(cmd, cwd=download_folder)
        
    def add_to_playlist(self, songs, thread_stream=True):        
        if len(songs) > 0:
            if thread_stream:
                thread.start_new_thread(self.get_songs_urls, (songs, "stream"))
            else:
                self.get_songs_urls(songs, "stream")
        if CONFIG["player_use_internal"]:
            for song in songs:
                song.play_process = 0
                song.play_status = ""
        else:
            for song in songs:
                song.play_status = "外部程序播放"
        self.playlist_treeview.append_songs(songs)                
        self.print_message("已添加%d首歌曲到播放列表。" % len(songs))
    
    def add_to_downlist(self, songs):
        if CONFIG["downloader_use_internal"]:
            for song in songs:
                song.down_process = "0%"
                song.down_status = "等待中"
        else:
            for song in songs:
                song.down_process = "100%"
                song.down_status = "外部程序下载"
        self.downlist_treeview.append_songs(songs)                
        self.print_message("已添加%d首歌曲到下载列表。" % len(songs))
                
    def get_songs_urls(self, songs, url_type):
        urls = []
        if url_type == "stream":
            for song in songs:
                song.load_streaming()
                if song.songUrl == "":
                    self.print_message("获取“%s”试听地址失败，请稍后再试。" % song.name)
                else:
                    urls.append(song.songUrl)
        elif url_type == "lyric":
            for song in songs:
                song.load_streaming()
                if song.lyricsUrl == "":
                    self.print_message("获取“%s”歌词地址失败，请稍后再试。" % song.name)
                else:
                    urls.append(song.lyricsUrl)
        else: #download
            for song in songs:
                song.load_download()
                if song.downloadUrl == "":
                    self.print_message("获取“%s”下载地址失败，请稍后再试。" % song.name)
                else:
                    urls.append(song.downloadUrl)
        return urls
        
    def copy_url_to_clipboard(self, songs, url_type):
        if url_type == "stream":
            url_type_name = "试听"
        elif url_type == "lyric":
            url_type_name = "歌词"
        else: # download
            url_type_name = "下载"
        
        self.copy_menuitem.set_sensitive(False)
        self.print_message("正在获取%d首歌曲的%s地址。" % (len(songs), url_type_name))
        urls = self.get_songs_urls(songs, url_type)
        text = "\n".join(urls)
        
        # paste to clipboard
        gtk.gdk.threads_enter()
        self.clipboard.set_text(text)
        gtk.gdk.threads_leave()
        
        self.print_message("共复制%d个%s地址已复制到剪贴板。" % (len(urls), url_type_name))
        self.copy_menuitem.set_sensitive(True)
        
    def export_url_to_file(self, songs, url_type):
        if url_type == "stream":
            url_type_name = "试听"
        elif url_type == "lyric":
            url_type_name = "歌词"
        else: # download
            url_type_name = "下载"
            
        # select file to save
        filename = ""
        gtk.gdk.threads_enter()
        dialog = gtk.FileChooserDialog("选择一个文件", None,
                       gtk.FILE_CHOOSER_ACTION_SAVE,
                       (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
        dialog.destroy()    
        gtk.gdk.threads_leave()

        self.export_menuitem.set_sensitive(False)
        self.print_message("正在获取%d首歌曲的%s地址。" % (len(songs), url_type_name))
        urls = self.get_songs_urls(songs, url_type)
        text = "\n".join(urls)
        
        # export to file
        if filename != "":
            file = open(filename, "w")
            file.write(text)
            self.print_message("共导出%d个%s地址到文件。" % (len(urls), url_type_name))
        self.export_menuitem.set_sensitive(True)

    def set_artist_label_text(self):
        if self.custom_artist_radiobutton.get_active():
            markup_text = "<span size='small'>%s</span>" % self.custom_aritst_entry.get_text()
            self.artist_label.set_markup_with_mnemonic(markup_text)
        else:
            radiobuttons = self.artist_table.get_children()
            for radiobutton in radiobuttons:
                if radiobutton.get_active():
                    markup_text = "<span size='small'>%s</span>" % radiobutton.get_label()
                    self.artist_label.set_markup_with_mnemonic(markup_text)
                    break
   
    def set_genres_label_text(self):
        checkbuttons = self.genres_table.get_children()
        checkbuttons.reverse()
        text = []
        for checkbutton in checkbuttons:
            if checkbutton.get_active():
                text.append(checkbutton.get_label())
        markup_text = "<span size='small'>%s</span>" % ",".join(text)
        self.genres_label.set_markup_with_mnemonic(markup_text)
    
    def set_langs_label_text(self):
        checkbuttons = self.langs_table.get_children()
        checkbuttons.reverse()
        text = []
        for checkbutton in checkbuttons:
            if checkbutton.get_active():
                text.append(checkbutton.get_label())
        markup_text = "<span size='small'>%s</span>" % ",".join(text)
        self.langs_label.set_markup_with_mnemonic(markup_text)
        
    # callback functions
    def on_search_entry_activate(self, widget, data=None):
        
        text = self.search_entry.get_text()        
        if text == "":
            self.print_message("警告：查找字符串不能为空。")
            return
        if self.song_radiobutton.get_active():
            type = "song"
        elif self.album_radiobutton.get_active():
            type = "album"
        else:
            type = "artist"
            
        self.do_search(text, type)
    
    def on_search_entry_icon_press(self, widget, position, event, data=None):
        if position == gtk.ENTRY_ICON_SECONDARY:
            widget.set_text("")
        else:
            self.search_entry.emit("activate")   
      
    def on_preferences_menuitem_activate(self, widget, data=None):
        self.update_preferences_widgets()
        response = self.preferences_dialog.run()
        if response == gtk.RESPONSE_OK:
            # regular
            CONFIG["download_folder"] = self.download_folder_entry.get_text()
            CONFIG["filename_template"] = self.filename_template_entry.get_text()
            CONFIG["player_use_internal"] = self.player_internal_radiobutton.get_active()
            CONFIG["downloader_use_internal"] = self.downloader_internal_radiobutton.get_active()
            CONFIG["download_cover"] = self.download_cover_checkbutton.get_active()
            CONFIG["download_lyric"] = self.download_lyric_checkbutton.get_active()
            CONFIG["show_status_icon"] = self.show_status_icon_checkbutton.get_active()
            # player
            CONFIG["player_path"] = self.player_path_entry.get_text() 
            CONFIG["player_single"] = self.player_single_entry.get_text()
            CONFIG["player_multi"] = self.player_multi_entry.get_text()
            # downloader
            CONFIG["downloader_path"] = self.downloader_path_entry.get_text() 
            CONFIG["downloader_single"] = self.downloader_single_entry.get_text()
            CONFIG["downloader_multi"] = self.downloader_multi_entry.get_text()
            
            # update widgets status 
            self.update_status_icon()
            self.update_player_widgets()
                        
            # save to file
            save_config_file()
        self.preferences_dialog.hide()
      
    def on_sidebar_menuitem_toggled(self, widget, data=None):
        if self.sidebar_menuitem.get_active():
            self.sidebar_vbox.show()
            self.sidebar_vbox.hided = False
        else:
            self.sidebar_vbox.hide()
            self.sidebar_vbox.hided = True
            
    def on_clear_info_menuitem_activate(self, widget, data=None):
        self.info_textbuffer.set_text("")
            
    def on_info_menuitem_toggled(self, widget, data=None):
        if self.info_menuitem.get_active():
            self.info_vbox.show()
            self.info_vbox.hided = False
        else:
            self.info_vbox.hide()
            self.info_vbox.hided = True
            
    def on_about_menuitem_activate(self, widget, data=None):
        self.about_dialog.set_logo(ICON_DICT["gmbox"])
        self.about_dialog.set_icon(ICON_DICT["gmbox"])
        self.about_dialog.run()
        
    def on_about_dialog_response(self,widget, response_id, data=None):
        self.about_dialog.hide()
    
    def on_quit_menuitem_activate(self, widget, data=None):
        self.stop_player()
        gtk.main_quit()
                
    def on_search_button_clicked(self, widget, data=None):
        if self.search_vbox.hided:
            self.search_vbox.show()
            self.search_arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
            self.search_vbox.hided = False
        else:
            self.search_vbox.hide()
            self.search_arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
            self.search_vbox.hided = True
    
    def on_category_button_clicked(self, widget, data=None):
        if self.category_vbox.hided:
            self.category_vbox.show()
            self.category_arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
            self.category_vbox.hided = False
        else:
            self.category_vbox.hide()
            self.category_arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
            self.category_vbox.hided = True
    
    def on_screener_button_clicked(self, widget, data=None):
        if self.screener_vbox.hided:
            self.screener_vbox.show()
            self.screener_arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
            self.screener_vbox.hided = False
        else:
            self.screener_vbox.hide()
            self.screener_arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
            self.screener_vbox.hided = True
    
    def on_tempo_checkbutton_toggled(self, widget, data=None):
        status = self.tempo_checkbutton.get_active()
        self.tempo_label1.set_sensitive(status)
        self.tempo_label2.set_sensitive(status)
        self.tempo_hscale.set_sensitive(status)
        
    def on_pitch_checkbutton_toggled(self, widget, data=None):
        status = self.pitch_checkbutton.get_active()
        self.pitch_label1.set_sensitive(status)
        self.pitch_label2.set_sensitive(status)
        self.pitch_hscale.set_sensitive(status)
        
    def on_timbre_checkbutton_toggled(self, widget, data=None):
        status = self.timbre_checkbutton.get_active()
        self.timbre_label1.set_sensitive(status)
        self.timbre_label2.set_sensitive(status)
        self.timbre_hscale.set_sensitive(status)
        
    def on_date_checkbutton_toggled(self, widget, data=None):
        status = self.date_checkbutton.get_active()
        self.date_label1.set_sensitive(status)
        self.date_label2.set_sensitive(status)
        self.date_hscale.set_sensitive(status)
        
    def on_artist_checkbutton_toggled(self, widget, data=None):
        status = self.artist_checkbutton.get_active()
        self.artist_label.set_sensitive(status)
        self.artist_button.set_sensitive(status)
        if not status:
            markup_text = "<span size='small'>全部</span>"
            self.artist_label.set_markup_with_mnemonic(markup_text)
        else:
            self.set_artist_label_text()
        
    def on_genres_checkbutton_toggled(self, widget, data=None):
        status = self.genres_checkbutton.get_active()
        self.genres_label.set_sensitive(status)
        self.genres_button.set_sensitive(status)
        if not status:
            markup_text = "<span size='small'>全部</span>"
            self.genres_label.set_markup_with_mnemonic(markup_text)
        else:
            self.set_genres_label_text()
        
    def on_langs_checkbutton_toggled(self, widget, data=None):
        status = self.langs_checkbutton.get_active()
        self.langs_label.set_sensitive(status)
        self.langs_button.set_sensitive(status)        
        if not status:
            markup_text = "<span size='small'>全部</span>"
            self.langs_label.set_markup_with_mnemonic(markup_text)
        else:
            self.set_langs_label_text()
            
    def on_custom_artist_radiobutton_toggled(self, widget, data=None):
        status = self.custom_artist_radiobutton.get_active()
        self.custom_aritst_entry.set_sensitive(status)
        
    def on_artist_button_clicked(self, widget, data=None):
        self.artist_dialog.run()
        self.set_artist_label_text()
        self.artist_dialog.hide()
           
    def on_genres_button_clicked(self, widget, data=None):
        self.genres_dialog.run()
        self.set_genres_label_text()
        self.genres_dialog.hide() 
        
    def on_langs_button_clicked(self, widget, data=None):
        self.langs_dialog.run()
        self.set_langs_label_text()
        self.langs_dialog.hide() 
    
    def on_apply_button_clicked(self, widget, data=None):
        args_dict = {}
        
        if self.tempo_checkbutton.get_active():
            args_dict["tempo"] = str(self.tempo_hscale.get_value() / 100)

        if self.pitch_checkbutton.get_active():
            args_dict["pitch"] = str(self.pitch_hscale.get_value() / 100)

        if self.timbre_checkbutton.get_active():
            args_dict["timbre"] = str(self.timbre_hscale.get_value() / 100)

        if self.date_checkbutton.get_active():
            # convert format, 3 division, but not dot character.
            # for examle year 2010 
            # 1262275200.0 --> 1262275200000
            pos = (self.date_hscale.get_value() / 100) 
            year_end = int(pos * (2010 - 1980) + 1980)
            args_dict["date_h"] = "%d000" % int(time.mktime(time.strptime(str(year_end), "%Y")))
            if year_end == 1980:
                args_dict["date_l"] = "0"
            else:                
                year_start = year_end - 3
                args_dict["date_l"] = "%d000" % int(time.mktime(time.strptime(str(year_start), "%Y")))
        
        if self.artist_checkbutton.get_active():
            if self.custom_artist_radiobutton.get_active():
                args_dict["artist"] = self.custom_aritst_entry.get_text()
            else:
                text = self.artist_label.get_text()
                if text != "":
                    args_dict["artist_type"] = ARITST[text]
            
        if self.genres_checkbutton.get_active():
            text = self.genres_label.get_text()
            if text != "":
                types = []
                for name in text.split(","):
                    types.append(GENRES[name])
                args_dict["genres"] = ",".join(types)
            
        if self.langs_checkbutton.get_active():
            text = self.langs_label.get_text()
            if text != "":
                langs = []
                for name in text.split(","):
                    langs.append(LANGS[name])
                args_dict["langs"] = ",".join(langs)
        
        self.do_screener(args_dict)

    def on_result_notebook_tab_button_press_event(self, widget, event, data=None):       
        if event.type == gtk.gdk._2BUTTON_PRESS or event.button == 2:
            index = self.result_notebook.page_num(widget.result_page)
            self.result_notebook.remove_page(index)
            
            if self.result_notebook.get_n_pages() == 0:
                # add empty result page back
                empty_result_page, empty_result_page_label = self.result_pages["empty"]
                self.result_notebook.append_page(empty_result_page, empty_result_page_label)

    def on_play_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.play_songs, (self.selected_songs,))
        
    def on_down_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.down_songs, (self.selected_songs,)) 
        
    def on_playlist_clear_menuitem_activate(self, widget, data=None):
        self.playlist_treeview.clear_songs()
        
    def on_playlist_remove_menuitem_activate(self, widget, data=None):
        self.playlist_treeview.remove_songs(self.selected_songs)
        
    def on_downlist_remove_menuitem_activate(self, widget, data=None):
        self.downlist_treeview.remove_songs(self.selected_songs)
        
    def on_downlist_clear_menuitem_activate(self, widget, data=None):
        self.downlist_treeview.clear_songs()
             
    def on_playlist_menuitem_activate(self, widget, data=None):
        self.add_to_playlist(self.selected_songs)
            
    def on_downlist_menuitem_activate(self, widget, data=None):
        self.add_to_downlist(self.selected_songs)
        
    def on_search_menuitem_activate(self, widget, data=None):
        for song in self.selected_songs:
            self.do_search(song.name.encode("utf8"), "song")
        
    def on_similar_menuitem_activate(self, widget, data=None):
        for song in self.selected_songs:
            self.do_similar(song.id, song.name)
                    
    def on_album_menuitem_activate(self, widget, data=None):
        # need to album artist
        ids = []
        unique_songs = []
        for song in self.selected_songs:
            song.load_detail()
            if song.albumId not in ids:
                ids.append(song.albumId)
                unique_songs.append(song)
        for song in unique_songs:
            self.do_album(song.albumId, song.album)
        
    def on_artist_hotsong_menuitem_activate(self, widget, data=None):
        # need to unique artist
        ids = []
        unique_songs = []
        for song in self.selected_songs:
            song.load_detail()
            if song.artistId not in ids:
                ids.append(song.artistId)
                unique_songs.append(song)
        for song in unique_songs:
            self.do_artist_song(song.artistId, song.artist)
        
    def on_artist_album_menuitem_activate(self, widget, data=None):
        # need to unique artist
        ids = []
        unique_songs = []
        for song in self.selected_songs:
            song.load_detail()
            if song.artistId not in ids:
                ids.append(song.artistId)
                unique_songs.append(song)
        for song in unique_songs:
            self.do_artist_album(song.artistId, song.artist)

    def on_copy_stream_url_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.copy_url_to_clipboard, (self.selected_songs, "stream"))
            
    def on_copy_download_url_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.copy_url_to_clipboard, (self.selected_songs, "download"))
        
    def on_copy_lyric_url_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.copy_url_to_clipboard, (self.selected_songs, "lyric"))
        
    def on_export_stream_url_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.export_url_to_file, (self.selected_songs, "stream"))
            
    def on_export_download_url_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.export_url_to_file, (self.selected_songs, "download"))
        
    def on_export_lyric_url_menuitem_activate(self, widget, data=None):
        thread.start_new_thread(self.export_url_to_file, (self.selected_songs, "lyric"))
            
    def on_view_detail_menuitem_activate(self, widget, data=None):
        for song in self.selected_songs:
            print_song(song)
            
    def on_result_page_button_clicked(self, widget, data=None):
        self.main_notebook.set_current_page(0)
        
    def on_playlist_page_button_clicked(self, widget, data=None):
        self.main_notebook.set_current_page(1)

    def on_downlist_page_button_clicked(self, widget, data=None):
        self.main_notebook.set_current_page(2)
        
    def on_play_button_clicked(self, widget, data=None):
        if self.player_running.isSet():
            self.player.pause()
            self.playing = not self.playing
            if self.playing:
                self.play_button.set_label("暂停")
            else:
                self.play_button.set_label("播放")
        
    def on_stop_button_clicked(self, widget, data=None):
        self.stop_player()
        
    def on_last_song_button_clicked(self, widget, data=None):
        song = self.playlist_treeview.get_last_song(self.player.song)
        self.stop_player()
        self.start_player(song)
        
    def on_next_song_button_clicked(self, widget, data=None):
        song = self.playlist_treeview.get_next_song(self.player.song)
        self.stop_player()
        self.start_player(song)
        
    def on_download_folder_button_clicked(self, widget, data=None):
        response = self.folder_chooser_dialog.run()
        if response == gtk.RESPONSE_OK:
            text = self.folder_chooser_dialog.get_filename()
            self.download_folder_entry.set_text(text)
        self.folder_chooser_dialog.hide()
        
    def on_player_path_button_clicked(self, widget, data=None):
        response = self.file_chooser_dialog.run()
        if response == gtk.RESPONSE_OK:
            text = self.file_chooser_dialog.get_filename()
            self.player_path_entry.set_text(text)
        self.file_chooser_dialog.hide()
        
    def on_downloader_path_button_clicked(self, widget, data=None):
        response = self.file_chooser_dialog.run()
        if response == gtk.RESPONSE_OK:
            text = self.file_chooser_dialog.get_filename()
            self.downloader_path_entry.set_text(text)
        self.file_chooser_dialog.hide()

    def on_status_icon_activate(self, widget, data=None):
        if self.mainwin.hided:
            self.mainwin.show()
        else:
            self.mainwin.hide()
        self.mainwin.hided = not self.mainwin.hided
        
    def on_mainwin_delete_event(self, widget, data=None):
        if CONFIG["show_status_icon"]:
            self.mainwin.hide()            
            self.mainwin.hided = True
            return True
        else:
            self.stop_player()
            gtk.main_quit()

if __name__ == '__main__':
    gtk.gdk.threads_init()
    GmBox().mainwin.show()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
