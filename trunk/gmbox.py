#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re,urllib,urllib2,sys,os
from HTMLParser import HTMLParser

reload(sys)
sys.setdefaultencoding('utf8')
songlist={
u'华语新歌':('chinese_new_songs_cn',100),
u'欧美新歌':('ea_new_songs_cn',100),
u'华语热歌':('chinese_songs_cn',200)
}
urltemplate="http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d"

def unistr(m):
    return unichr(int(m.group(1)))

class ListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'id':''}
        self.tmpsong=self.songtemplate.copy()
        self.isa=0
        self.insongtable=0
        self.tdclass=''
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.isa=1
            if self.insongtable and self.tdclass == 'Download BottomBorder':
                for (n,v) in attrs:
                    if n=='onclick':
                        #self.tmpsong['link']=re.match(r'.*"(.*)".*"(.*)".*',v,re.S).group(1)
                        self.tmpsong['id']=re.match(r'.*id%3D(.*?)\\x26.*',v,re.S).group(1)
                        
        if tag == 'table':
            for (n,v) in attrs:
                if n=='id' and v=='song_list':
                    self.insongtable=1
        if self.insongtable and tag == 'td':
            for (n,v) in attrs:
                if n=='class':
                    self.tdclass=v

    def handle_endtag(self, tag):
        if tag == 'a':
            self.isa=0
        if tag == 'table':
            self.insongtable=0

    def handle_data(self, data):
        if self.insongtable and self.isa:
            if self.tdclass == 'Title BottomBorder':
                self.tmpsong['title']=data
            elif self.tdclass == 'Artist BottomBorder':
                if  self.tmpsong['artist']:
                    self.tmpsong['artist']+=u'、'+data
                else:
                    self.tmpsong['artist']=data
            elif self.tdclass == 'Download BottomBorder':
                self.songlist.append(self.tmpsong.copy())
                self.tmpsong=self.songtemplate.copy()
                
    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist])
    
#    def downloadall(self):
#        for song in self.songlist:
        
class SongParser(HTMLParser):
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

class Download:
    def __init__(self, remote_uri, local_uri):
        if os.path.exists(local_uri):
            print local_uri,u'已存在!'
        else:
            print u'正在下载:',local_uri
            urllib.urlretrieve(remote_uri, local_uri+'.downloading', self.update_progress)
            os.rename(local_uri+'.downloading', local_uri)
            print
    def update_progress(self, blocks, block_size, total_size):
        if total_size>0 :
            percentage = float(blocks) / (total_size/block_size+1) * 100
            print '\r['+''.join(['=' for i in range((int)(percentage/2))])+'>'+ \
                ''.join([' ' for i in range((int)(50-percentage/2))])+ \
                (']  %0.2f%%' % percentage),
        
        
class Lists:
    def __init__(self,stype):
        self.songlist=[]
        if stype in songlist:
            p=ListParser()
            for i in range(0,songlist[stype][1],25):
                html=urllib2.urlopen(urltemplate%(songlist[stype][0],i)).read()
                p.feed(re.sub(r'&#([0-9]{5});',unistr,html))
            self.songlist=p.songlist
        else:
            #raise Exception
            print "Error stype."

    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist])
        
l=Lists(u'华语新歌')
#print l

for song in l.songlist:
    local_uri=song['title']+'-'+song['artist']+'.mp3'
    if os.path.exists(local_uri):
        print local_uri,u'已存在!'
        continue
    songurl="http://www.google.cn/music/top100/musicdownload?id="+song['id']
    s=SongParser()
    s.feed(urllib2.urlopen(songurl).read())
    Download(s.url,local_uri)
    
