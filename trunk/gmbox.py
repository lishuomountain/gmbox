#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re,urllib,urllib2,sys,os,time
from HTMLParser import HTMLParser
import thread
from stat import *

#"""用sax解析xml歌曲列表"""
#import xml.parsers.expat

#还是用dom吧。。
from xml.dom import minidom
import codecs

reload(sys)
sys.setdefaultencoding('utf8')


if os.name=='posix':
    #player="mplayer"
    player="mpg123"
    userhome = os.path.expanduser('~')
    musicdir=userhome+'/Music/google_music/top100/'
    gmbox_home=userhome+'/.gmbox/'
if os.name=='nt':
    player="mpxplay.exe"
    userhome = 'C:'
    musicdir=userhome+'\Music\google_music\op100'
    gmbox_home=userhome+'\.gmbox'
if os.path.exists(musicdir)==0:
    os.mkdir(musicdir)
if os.path.exists(gmbox_home)==0:
    os.mkdir(gmbox_home)

songlists={
u'华语新歌':('chinese_new_songs_cn',100),
u'欧美新歌':('ea_new_songs_cn',100),
u'华语热歌':('chinese_songs_cn',200),
u'欧美热歌':('ea_songs_cn',200),
u'日韩热歌':('jk_songs_cn',200),
u'流行热歌':('pop_songs_cn',100),
u'摇滚热歌':('rock_songs_cn',100),
u'嘻哈热歌':('hip-hop_songs_cn',100),
u'影视热歌':('soundtrack_songs_cn',100),
u'民族热歌':('ethnic_songs_cn',100),
u'拉丁热歌':('latin_songs_cn',100),
u'R&B热歌':('rnb_songs_cn',100),
u'乡村热歌':('country_songs_cn',100),
u'民谣热歌':('folk_songs_cn',100),
u'灵歌热歌':('soul_songs_cn',100),
u'轻音乐热歌':('easy-listening_songs_cn',100),
u'爵士蓝调热歌':('jnb_songs_cn',100)
}
urltemplate="http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d"
searchtemplate="http://www.google.cn/music/search?q=%E5%A4%A9%E4%BD%BF%E7%9A%84%E7%BF%85%E8%86%80&aq=f"

def unistr(m):
    return unichr(int(m.group(1)))
def sizeread(size):
    if size>1024*1024:
        return '%0.2fMB' % (float(size)/1024/1024)
    elif size>1024:
        return '%0.2fKB' % (float(size)/1024)
    else:
        return '%dB' % size

class ListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'id':''}
        self.tmpsong=self.songtemplate.copy()
        (self.isa,self.ispan,self.insongtable,self.tdclass)=(0,0,0,'')
    
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
        if os.path.exists(musicdir+local_uri):
            print local_uri,u'已存在!'
        else:
            print u'正在下载:',local_uri
            self.T=self.startT=time.time()
            (self.D,self.speed)=(0,0)
            urllib.urlretrieve(remote_uri, musicdir+local_uri+'.downloading', self.update_progress)
            os.rename(musicdir+local_uri+'.downloading', musicdir+local_uri)
            os.system('mid3iconv -e gbk "'+musicdir+local_uri + '"')
            speed=os.stat(musicdir+local_uri).st_size/(time.time()-self.startT)
            print '\r['+''.join(['=' for i in range(50)])+ \
                '] 100.00%%  %s/s       '%sizeread(speed)
    def update_progress(self, blocks, block_size, total_size):
        if total_size>0 :
            percentage = float(blocks) / (total_size/block_size+1) * 100
            if int(time.time()) != int(self.T):
                self.speed=(blocks*block_size-self.D)/(time.time()-self.T)
                (self.D,self.T)=(blocks*block_size,time.time())
            print '\r['+''.join(['=' for i in range((int)(percentage/2))])+'>'+ \
                ''.join([' ' for i in range((int)(50-percentage/2))])+ \
                (']  %0.2f%%  %s/s    ' % (percentage,sizeread(self.speed))),
        
class Listen:
    def __init__(self, remote_uri, local_uri):
        self.remote_uri= remote_uri
        self.local_uri=local_uri
        thread.start_new_thread(self.download,(local_uri,))
        time.sleep(2)
        self.play(local_uri,)
        os.rename(musicdir+self.local_uri+'.cache', musicdir+self.local_uri)

    def play(self,a):
        newplay(self.local_uri,"true")

    def download(self,a):
            print u'正在缓冲:',self.local_uri
            self.T=self.startT=time.time()
            (self.D,self.speed)=(0,0)
            urllib.urlretrieve(self.remote_uri, musicdir+self.local_uri+'.cache', self.update_progress)
            speed=os.stat(musicdir+self.local_uri).st_size/(time.time()-self.startT)
            print '\r['+''.join(['=' for i in range(50)])+ \
                '] 100.00%%  %s/s       '%sizeread(speed)
    def update_progress(self, blocks, block_size, total_size):
        if total_size>0 :
            percentage = float(blocks) / (total_size/block_size+1) * 100
            if int(time.time()) != int(self.T):
                self.speed=(blocks*block_size-self.D)/(time.time()-self.T)
                (self.D,self.T)=(blocks*block_size,time.time())
            #print blocks
            #print total_size/block_size
            print '\r['+''.join(['=' for i in range((int)(percentage/2))])+'>'+ \
                ''.join([' ' for i in range((int)(50-percentage/2))])+ \
                (']  %0.2f%%  %s/s    ' % (percentage,sizeread(self.speed))),
        
class Lists:
    def __init__(self,stype):
        self.songlist=[]
        if stype in songlists:
            p=ListParser()
            print u'正在获取"'+stype+u'"的歌曲列表',
            sys.stdout.flush()
            for i in range(0,songlists[stype][1],25):
            #for i in range(0,25,25):
                html=urllib2.urlopen(urltemplate%(songlists[stype][0],i)).read()
                p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
                print '.',
                sys.stdout.flush()
            self.songlist=p.songlist
            print 'done!'
        else:
            #raise Exception
            print u'未知列表:"'+str(stype)+u'",仅支持以下列表: '+u'、'.join(
            ['"%s"'%key for key in songlists])

    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist]) \
            +u'\n共 '+str(len(self.songlist))+u' 首歌.'
        
    def downone(self,i=0):
        song=self.songlist[i]
        local_uri=song['title']+'-'+song['artist']+'.mp3'
        if os.path.exists(musicdir+local_uri):
            print local_uri,u'已存在!'
            return
        songurl="http://www.google.cn/music/top100/musicdownload?id="+song['id']
        s=SongParser()

        try:
            text = urllib2.urlopen(songurl).read()
        except:
            print "Reading URL Error: %s" % local_uri
            return

        s.feed(text)
        Download(s.url,local_uri)
        
    def listen(self,start=0):
        song=self.songlist[start]
        local_uri=song['title']+'-'+song['artist']+'.mp3'
        if os.path.exists(musicdir+local_uri):
            newplay(self.local_uri,'false')
            return
        songurl="http://www.google.cn/music/top100/musicdownload?id="+song['id']
        s=SongParser()

        try:
            text = urllib2.urlopen(songurl).read()
        except:
            print "Reading URL Error: %s" % local_uri

        s.feed(text)
        Listen(s.url,local_uri)

    def get_title(self,i=0):
        song=self.songlist[i]
        return song['title']

    def get_artist(self,i=0):
        song=self.songlist[i]
        return song['artist']

    def downall(self):
        for i in range(len(self.songlist)):
            self.downone(i)
    
    def download(self,songids=[]):
        for i in songids:
            self.downone(i)

class ListFile:
    def __init__(self,top):
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'id':''}
        self.tmplist=self.songtemplate.copy()
        self.walktree(top,self.visitfile)

    def walktree(self,top, callback):
        for log in os.listdir(top):
            pathname = os.path.join(top, log)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode):
                # It's a directory, recurse into it
                self.walktree(pathname, callback)
            elif S_ISREG(mode):
                # It's a file, call the callback function
                callback(pathname)
            else:
                # Unknown file type, print a message
                print 'Skipping %s' % pathname

    def visitfile(self,file):
        size = os.path.getsize(file)
        mt = time.ctime(os.stat(file).st_mtime);
        ct = time.ctime(os.stat(file).st_ctime);
        self.tmplist['artist']=os.path.basename(file).split('-')[1].split('.')[0]
        self.tmplist['title']=os.path.basename(file).split('-')[0]
        self.tmplist['id']=len(self.songlist)
        self.songlist.append(self.tmplist.copy())
        self.tmplist=self.songtemplate.copy()

    def get_title(self,i=0):
        song=self.songlist[i]
        return song['title']

    def get_artist(self,i=0):
        song=self.songlist[i]
        return song['artist']

    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist]) \
            +u'\n共 '+str(len(self.songlist))+u' 首歌.'

    def listen(self,start=0):
        song=self.songlist[start]
        local_uri=song['title']+'-'+song['artist']+'.mp3'
        print local_uri
        newplay(local_uri,"false")

class PlayList:
    def __init__(self):
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'id':''}
        self.tmplist=self.songtemplate.copy()

        """
        self.level = 0
        p = xml.parsers.expat.ParserCreate()  
        #p.StartElementHandler = start_element  
        #p.EndElementHandler = end_element  
        p.CharacterDataHandler = self.char_data  
        #p.returns_unicode = False
        f = file(gmbox_home+'default.xml')
        p.ParseFile(f)  
        f.close()  
        """
        if os.path.exists(gmbox_home+'default.xml'):
            self.xmldoc = minidom.parse(gmbox_home+'default.xml')
            items = self.xmldoc.getElementsByTagName('item')
            for item in items:
                title = item.getAttribute('title')
                artist = item.getAttribute('artist')
                id = item.getAttribute('id')
                self.tmplist['artist']=artist
                self.tmplist['title']=title
                self.tmplist['id']=id
                self.songlist.append(self.tmplist.copy())
                self.tmplist=self.songtemplate.copy()
        else:
            impl = minidom.getDOMImplementation()
            self.xmldoc = impl.createDocument(None, 'playlist', None)
            f = file(gmbox_home+'default.xml','w')
            writer = codecs.lookup('utf-8')[3](f)
            self.xmldoc.writexml(writer)
            writer.close
        self.root = self.xmldoc.documentElement

    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist]) \
            +u'\n共 '+str(len(self.songlist))+u' 首歌.'

    def add(self,title,artist,id):
        item = self.xmldoc.createElement('item')
        item.setAttribute('title',title)
        item.setAttribute('artist',artist)
        item.setAttribute('id',id)
        self.root.appendChild(item)
        f = file(gmbox_home+'default.xml','w')
        writer = codecs.lookup('utf-8')[3](f)
        self.xmldoc.writexml(writer)
        writer.close

    def get_title(self,i=0):
        song=self.songlist[i]
        return song['title']

    def get_artist(self,i=0):
        song=self.songlist[i]
        return song['artist']

    def listen(self,start=0):
        song=self.songlist[start]
        local_uri=song['title']+'-'+song['artist']+'.mp3'
        if os.path.exists(musicdir+local_uri):
            newplay(local_uri,'false')
            return
        songurl="http://www.google.cn/music/top100/musicdownload?id="+song['id']
        s=SongParser()

        try:
            text = urllib2.urlopen(songurl).read()
        except:
            print "Reading URL Error: %s" % local_uri

        s.feed(text)
        Listen(s.url,local_uri)

    """
    # 获取某节点名称及属性值集合
    def start_element(self,name, attrs):  
        print 'Start element:', name, attrs  
        self.level = self.level + 1  
      
    # 获取某节点结束名称  
    def end_element(self,name):  
        self.level = self.level - 1  
        print 'End element:', name  
          
    # 获取某节点中间的值  
    def char_data(self,file): 
        if(file== '\n'):
            return
        if(file.isspace()):
            return
        self.tmplist['artist']=os.path.basename(file).split('-')[1]
        self.tmplist['title']=os.path.basename(file).split('-')[0]
        self.tmplist['id']=len(self.songlist)
        self.songlist.append(self.tmplist.copy())
        self.tmplist=self.songtemplate.copy()
    """
class SearchParse(HTMLParser):
    """
    解析搜索结果页面
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlist=[]
        self.songtemplate={
            'title':'',
            'artist':'',
            'id':''}
        self.tmpsong=self.songtemplate.copy()
        (self.isa,self.ispan,self.insongtable,self.tdclass)=(0,0,0,'')
    
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

def newplay(uri,trylisten):
    if os.name=='posix':
        full_uri=musicdir+uri
        if trylisten=='true':
            full_uri=full_uri+'.cache'
        os.system('mid3iconv -e gbk "'+full_uri+'"')
        os.system('pkill '+player)
        os.system(player+' "'+full_uri+'"')
    if os.name == 'nt':
        full_uri=musicdir+uri
        if bool=='true':
            full_uri=full_uri+'.cache'
        pid = os.system('tasklist')
        os.system('taskkill '+pid)
        os.system('ntsd '+pid)
        os.system(player+' "'+musicdir+uri+'.cache"')

if __name__ == '__main__':
    l=Lists(u'华语新歌')
    #print l
    #l.download([0,2,6])
    l.downall()
