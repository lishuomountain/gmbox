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

'''GUI的设置界面'''

import gtk
from lib.config import config
from lib.core import gmbox

class ConfigTable(gtk.Table):
    '''设置界面'''
    def __init__(self):
        '''初始化设置界面'''
        gtk.Table.__init__(self, 10, 2)
        self.current_line = 0
        
        tmp_label = gtk.Label('\n设置\n')
        tmp_label.set_use_markup(True)
        self.attach_line(tmp_label)
    
        hb_savedir = gtk.HBox(False, 0)
        options_savedir = gtk.Entry()
        options_savedir.set_text(config.item['savedir'])
        options_savedir.set_sensitive(False)
        bt_savedir = gtk.Button('浏览...')
        bt_savedir.connect('clicked', self.config_savedir, options_savedir)

        hb_savedir.pack_start(options_savedir, True, True)
        hb_savedir.pack_start(bt_savedir, False, False)
        
        self.attach_line(gtk.Label(u'    歌曲下载目录:  '), hb_savedir)

        options_id3utf8 = gtk.CheckButton(u'将ID3信息转换为UTF8(对windows用户无效)')
        options_id3utf8.set_active(config.item['id3utf8'])
        options_id3utf8.connect('toggled', self.config_id3utf8)
        self.attach_line(gtk.Label(u''), options_id3utf8)

        options_makeartistdir = gtk.CheckButton(u'下载时建立歌手目录')
        options_makeartistdir.set_active(config.item['makeartistdir'])
        options_makeartistdir.connect('toggled', self.config_makeartistdir)
        self.attach_line(gtk.Label(u''), options_makeartistdir)

        options_makealbumdir = gtk.CheckButton(u'下载专辑时下载到各自的目录')
        options_makealbumdir.set_active(config.item['makealbumdir'])
        options_makealbumdir.connect('toggled', self.config_makealbumdir)
        self.attach_line(gtk.Label(u''), options_makealbumdir)

        options_addalbumnum = gtk.CheckButton(u'下载专辑时，在歌名前放置目录序号')
        options_addalbumnum.set_active(config.item['addalbumnum'])
        options_addalbumnum.connect('toggled', self.config_addalbumnum)
        self.attach_line(gtk.Label(u''), options_addalbumnum)
        
        options_lyric = gtk.CheckButton(u'下载歌曲时同时下载歌词')
        options_lyric.set_active(config.item['lyric'])
        options_lyric.connect('toggled', self.config_lyric)
        self.attach_line(gtk.Label(u''), options_lyric)
        
        options_cover = gtk.CheckButton(u'下载专辑时同时下载专辑封面')
        options_cover.set_active(config.item['cover'])
        options_cover.connect('toggled', self.config_cover)
        self.attach_line(gtk.Label(u''), options_cover)

        options_localdir = gtk.Entry()
        options_localdir.set_text('此功能尚未实现.')
        options_localdir.set_sensitive(False)
        self.attach_line(gtk.Label(u'本地歌曲目录'), options_localdir)

        self.previewLabel = gtk.Label()
        self.attach_line(gtk.Label(u'文件名预览'), self.previewLabel)
        self.refresh_pre()
        
    def attach_line(self, obj1, obj2=None):
        if obj2:
            self.attach(obj1, 0, 1, self.current_line, self.current_line + 1, 
                gtk.SHRINK, gtk.SHRINK)
            self.attach(obj2, 1, 2, self.current_line, self.current_line + 1, 
                yoptions=gtk.SHRINK)
        else:
            self.attach(obj1, 0, 2, self.current_line, self.current_line + 1, 
                gtk.SHRINK, gtk.SHRINK)
        self.current_line += 1

    def config_savedir(self, widget, entry):
        dialog = gtk.FileChooserDialog("Open..", None,
               gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK) 
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            config.savedir_changed(dialog.get_filename())
            entry.set_text(dialog.get_filename())
        elif response == gtk.RESPONSE_CANCEL:
            print '取消'
        dialog.destroy()
        
    def config_id3utf8(self, widget):
        config.id3utf8_changed(widget.get_active())

    def refresh_pre(self):
        v = u'歌曲下载路径：' + \
            gmbox.setup_file_info(u'歌名', u'歌手', False, u'专辑名', u'专辑歌手', 1)[0] \
            + '\n' + u'专辑下载路径：' + \
            gmbox.setup_file_info(u'歌名', u'歌手', True, u'专辑名', u'专辑歌手', 1)[0]
        self.previewLabel.set_text(v)
    
    def config_makealbumdir(self, widget):
        config.makealbumdir_changed(widget.get_active())
        self.refresh_pre()

    def config_makeartistdir(self, widget):
        config.makeartistdir_changed(widget.get_active())
        self.refresh_pre()

    def config_addalbumnum(self, widget):
        config.addalbumnum_changed(widget.get_active())
        self.refresh_pre()
        
    def config_lyric(self, widget):
        config.lyric_changed(widget.get_active())
        self.refresh_pre()
        
    def config_cover(self, widget):
        config.cover_changed(widget.get_active())
        self.refresh_pre()
