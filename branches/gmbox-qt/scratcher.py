#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Name:     scratcher.py
# Author:   xiooli <xioooli[at]yahoo.com.cn>
# Licence:  GPLv3
# Version:  110224

''' classes for music and music info downloader
'''
from string import Template
from qonfig import load_config_file
import traceback, os, urllib
from PyQt4.QtCore import QThread

CONFIG = load_config_file()

def sizeread(size):
    '''传入整数,传出B/KB/MB'''
    if size > 1024*1024:
        return '%0.2f MB' % (float(size)/1024/1024)
    elif size > 1024:
        return '%0.2f KB' % (float(size)/1024)
    else:
        return '%d B' % size

class Myopener(urllib.FancyURLopener):
    version = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

urlretrieve = Myopener().retrieve

class mythread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.callback = None
        self.data_pool = {}
        self.data_key = None
    def run(self):
        if self.callback:
            self.data_pool[self.data_key] = self.callback()

class Scratcher(QThread):
    def __init__(self, song, callback = None):
        QThread.__init__(self)
        self.song = song
        self.song.down_progress = 0
        self.song.size = None
        self.song.down_speed = '0 B/s'
        self.callback = callback
        self.start_time = time.time()
        self.mp3_filepath = self.get_filepath()

    def run(self):
        self.song.remove_lock = True
        if CONFIG["download_cover"]:
            self.download_cover()
        if CONFIG["download_lyric"]:
            self.download_lyric()
        self.download_mp3()
        self.song.remove_lock = False
        if self.callback:
            self.callback()

    def get_safe_path(self, url):
        not_safe_chars = '''\/:*?<>|'"'''
        if len(url) > 243:
            url = url[:238]
        for char in not_safe_chars:
            url = url.replace(char, "")
        return url

    def get_filepath(self):
        download_folder = CONFIG["download_folder"]
        if download_folder.endswith("/"):
            download_folder = download_folder[:-1]
        filename = Template(CONFIG["filename_template"]).safe_substitute(
                ALBUM = self.song.album,
                ARTIST = self.song.artist,
                TITLE = self.get_safe_path(self.song.name))
        if "${TRACK}" in filename:
            # need to load stearm info
            self.song.load_streaming()
            filename = filename.safe_substitute(TRACK = self.song.providerId[-2:])
        filepath = "%s/%s.mp3" % (download_folder, filename)
        return filepath

    def download_cover(self):
        self.song.down_status = "正在获取封面地址"
        self.song.load_streaming()
        if self.song.albumThumbnailLink == "":
            self.song.albumThumbnailLink = "获取封面地址失败"
            return

        filepath = "%s/cover.jpg" % os.path.dirname(self.get_filepath())

        if os.path.exists(filepath):
            self.song.down_status = "封面已存在"
            return

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        try:
            self.song.down_status = "下载封面中"
            urlretrieve(self.song.albumThumbnailLink, filepath)
            self.song.down_status = "下载封面完成"
        except:
            traceback.print_exc()

    def download_lyric(self):
        self.song.down_status = "正在获取歌词地址"
        self.song.load_streaming()
        if self.song.lyricsUrl == "":
            self.song.down_status = "获取歌词地址失败"
            return

        # remove ".mp3" extension
        filepath = "%s.lrc" % self.get_filepath()[:-4]

        if os.path.exists(filepath):
            self.song.down_status = "歌词文件已存在"
            return

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        try:
            self.song.down_status = "下载歌词中"
            urlretrieve(self.song.lyricsUrl, filepath)
            self.song.down_status = "下载歌词完成"
        except:
            traceback.print_exc()

    def download_mp3(self):
        self.song.down_status = "正在获取地址"
        self.song.load_download()
        if self.song.downloadUrl == "":
            self.song.down_status = "获取地址失败"
            return

        if os.path.exists(self.mp3_filepath):
            self.song.down_status = "文件已存在"
            self.song.down_process = "100%"
            return

        if not os.path.exists(os.path.dirname(self.mp3_filepath)):
            os.makedirs(os.path.dirname(self.mp3_filepath))

        print "Downloading %s" % self.song.name
        print self.song.downloadUrl
        print self.mp3_filepath
        try:
            self.song.down_status = "下载中"
            urlretrieve(self.song.downloadUrl, self.mp3_filepath, self.update_progress)
            self.song.down_status = "下载完成"
        except:
            traceback.print_exc()

    def update_progress(self, block, block_size, total_size):
        self.song.down_speed = sizeread(os.stat(self.mp3_filepath).st_size \
                / (time.time() - self.start_time)) + '/s'
        if not self.song.size:
            self.song.size = sizeread(total_size)
        downloaded_size = block * block_size
        percent = float(downloaded_size) / total_size
        if percent >= 1:
            self.song.down_progress = 100
        elif percent <= 0:
            self.song.down_progress = 0
        elif percent < 0.1:
            self.song.down_progress = int(str(percent)[3:4])
        else:
            self.song.down_progress = int(str(percent)[2:4])

if __name__ == '__main__':
    #print CONFIG
    from core import *
    import sys, time

    #print DirArtist("beyond").load_songs()
    #sys.exit()

    from PyQt4.QtCore import QTimer
    from PyQt4.QtGui import QMainWindow, QApplication, QProgressBar, QStatusBar

    song = Song("S68007e9f02848823")

    def callback():
        print 'haha'

    class win(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            self.resize(200, 50)
            self.createStatusBar()
            self.timer = QTimer()
            self.timer.setInterval(1000)
            self.pb = QProgressBar(self.statusBar())
            self.pb.resize(190,30)
            self.pb.setRange(0, 100)
            self.pb.setValue(0)
            self.thr = Scratcher(song)
            self.thr.start()
            self.timer.timeout.connect(self.update_progress_bar)
            self.timer.start()
            self.song = song
            thr = mythread(self)
            thr.callback = callback
            thr.start()
            self.show()

        def createStatusBar(self):
            sb = QStatusBar()
            sb.setFixedHeight(40)
            self.setStatusBar(sb)

        def update_progress_bar(self):
            if self.thr.isRunning() and self.pb.value() != self.song.down_progress:
                print self.song.down_speed, self.song.size
                self.pb.setValue(self.song.down_progress)
            elif not self.thr.isRunning():
                self.pb.setValue(100)
                self.timer.stop()
                del(self.timer)

    app = QApplication(sys.argv)
    w = win()
    sys.exit(app.exec_())

