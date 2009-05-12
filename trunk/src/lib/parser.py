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


import re
from HTMLParser import HTMLParser
import logging

log = logging.getLogger('lib.parser')


class ListParser(HTMLParser):
    '''解析榜单列表页面的类'''
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'album':'',
            'id':''}
        self.tmpsong=self.songtemplate.copy()
        (self.isa,self.ispan,self.isb,self.insongtable,self.tdclass)=(0,0,0,0,'')
    
    def handle_starttag(self, tag, attrs):
        '''处理标签开始的函数'''
        
        if tag == 'a':
            self.isa=1
            if self.insongtable and self.tdclass == 'Icon BottomBorder':
                (n,v)=zip(*attrs)
                if v[n.index('title')]==u'下载':
                    self.tmpsong['id']=re.match(r'.*id%3D(.*?)\\x26.*',v[n.index('onclick')],re.S).group(1)
                    self.songlist.append(self.tmpsong)
        if tag == 'table':
            for (n,v) in attrs:
                if n=='id' and v=='song_list':
                    self.insongtable=1
        if self.insongtable and tag == 'td':
            for (n,v) in attrs:
                if n=='class':
                    self.tdclass=v
                    if v=='Title BottomBorder':
                        self.tmpsong=self.songtemplate.copy()
        if tag == 'span':
            self.ispan=1
        if tag == 'b':
            self.isb=1

    def handle_endtag(self, tag):
        '''处理标签结束的函数'''
        
        if tag == 'a':
            self.isa=0
        if tag == 'table':
            self.insongtable=0
        if tag == 'span':
            self.ispan=0
        if tag == 'b':
            self.isb=0

    def handle_data(self, data):
        '''处理html节点数据的函数'''
        
        if self.insongtable and (self.isa or self.ispan or self.isb):
            if self.tdclass == 'Title BottomBorder':
                self.tmpsong['title']+=data
            elif self.tdclass == 'Artist BottomBorder':
                self.tmpsong['artist']+=(u'、' if self.tmpsong['artist'] else '') + data
            elif self.tdclass == 'Album BottomBorder':
                self.tmpsong['album']=data
                
    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist]) \
            +u'\n共 '+str(len(self.songlist))+u' 首歌.'

    
class SongParser(HTMLParser):
    '''解析歌曲页面,得到真实的歌曲下载地址'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.url=''
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (n,v) in attrs:
                if n=='href' and re.match(r'/music/top100/url.*',v):
                    self.url='http://www.google.cn'+v
    def __str__(self):
        return self.url

class LyricsParser(HTMLParser):
    '''解析歌词页面 '''
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'album':'',
            'id':''}
        self.tmpsong=self.songtemplate.copy()
        (self.isa,self.ispan,self.insongtable,self.tdclass)=(0,0,0,'')
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.isa=1
            if self.insongtable and self.tdclass == 'Icon BottomBorder':
                (n,v) =zip(*attrs)
                if v[n.index('title')]==u'下载':
                    self.tmpsong['id']=re.match(r'.*id%3D(.*?)\\x26.*',v[n.index('onclick')],re.S).group(1)
                    self.songlist.append(self.tmpsong)
                    self.tmpsong=self.songtemplate.copy()
        if tag == 'table':
            for (n,v) in attrs:
                if n=='id' and v=='song_list':
                    self.insongtable=1
        if self.insongtable and tag == 'td':
            for (n,v) in attrs:
                if n=='class':
                    self.tdclass=v
        if tag == 'span':
            self.ispan=1

    def handle_endtag(self, tag):
        if tag == 'a':
            self.isa=0
        if tag == 'table':
            self.insongtable=0
        if tag == 'span':
            self.ispan=0

    def handle_data(self, data):
        if self.insongtable and (self.isa or self.ispan):
            if self.tdclass == 'Title BottomBorder':
                self.tmpsong['title']=data
            elif self.tdclass == 'Artist BottomBorder':
                self.tmpsong['artist']+=(u'、' if self.tmpsong['artist'] else '') + data
            elif self.tdclass == 'Album BottomBorder':
                self.tmpsong['album']+=(u'、' if self.tmpsong['album'] else '') + data
                
    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist])
