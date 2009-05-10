#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''gmbox核心'''
import re,urllib,urllib2,sys,os,time
from HTMLParser import HTMLParser
import thread
from stat import *

from xml.dom import minidom
import codecs

reload(sys)
sys.setdefaultencoding('utf8')


if os.name=='posix':
    #player="mplayer"
    player="mpg123"
if os.name=='nt':
    player="mpxplay.exe"
userhome = os.path.expanduser('~')
musicdir=userhome+'/Music/google_music/top100/'
gmbox_home=userhome+'/.gmbox/'
if os.path.exists(musicdir)==0:
    os.makedirs(musicdir)   #递归创建目录  mkdir是创建最后一层目录！amoblin
if os.path.exists(gmbox_home)==0:
    os.makedirs(gmbox_home)
playlist_path=gmbox_home+'default.xml'

urltemplate="http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d"
searchtemplate="http://www.google.cn/music/search?q=%E5%A4%A9%E4%BD%BF%E7%9A%84%E7%BF%85%E8%86%80&aq=f"
lyricstemplate='http://g.top100.cn/7872775/html/lyrics.html?id=S8ec32cf7af2bc1ce'

play_over=1  #标志信号量：自动播放完毕还是被打断，默认自动播放完

def unistr(m):
    '''给re.sub做第二个参数,返回&#nnnnn;对应的中文'''
    return unichr(int(m.group(1)))

def sizeread(size):
    '''传入整数,传出B/KB/MB'''
    #FIXME:这个有现成的函数没?
    if size>1024*1024:
        return '%0.2fMB' % (float(size)/1024/1024)
    elif size>1024:
        return '%0.2fKB' % (float(size)/1024)
    else:
        return '%dB' % size

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

class Download:
    '''下载文件的类'''
    def __init__(self, remote_uri, filename,mode=1):
        '''下载模式 1 和 试听(缓存)模式 0'''
        #这里不用检测是否文件已存在了,上边的downone或play已检测了
        if mode:
            print u'正在下载:',filename
        else:
            print u'正在缓冲:',filename
        local_uri=musicdir+filename
        cache_uri=local_uri+'.downloading'
        self.T=self.startT=time.time()
        (self.D,self.speed)=(0,0)
        urllib.urlretrieve(remote_uri, cache_uri, self.update_progress)
        speed=os.stat(cache_uri).st_size/(time.time()-self.startT)
        if mode:
            '''下载模式'''
            print '\r['+''.join(['=' for i in range(50)])+ \
                '] 100.00%%  %s/s       '%sizeread(speed)
            os.rename(cache_uri, local_uri)
            if os.name=='posix':
                '''在Linux下转换到UTF 编码，现在只有comment里还是乱码'''
                os.system('mid3iconv -e gbk "'+local_uri + '"')
        else:
            print '\r['+''.join(['=' for i in range(50)])+ \
                '] 100.00%%  %s/s       '%sizeread(speed)
            '''试听模式  由于此下载进程未设信号量，一旦运行，除了终止程序暂无终止办法，所以肯定会下载完全，所以保存'''
            os.rename(cache_uri, local_uri)
            if os.name=='posix':
                '''在Linux下转换到UTF 编码，现在只有comment里还是乱码'''
                os.system('mid3iconv -e gbk "'+local_uri + '"')

    def update_progress(self, blocks, block_size, total_size):
        '''处理进度显示的回调函数'''
        if total_size>0 :
            percentage = float(blocks) / (total_size/block_size+1) * 100
            if int(time.time()) != int(self.T):
                self.speed=(blocks*block_size-self.D)/(time.time()-self.T)
                (self.D,self.T)=(blocks*block_size,time.time())
            print '\r['+''.join(['=' for i in range((int)(percentage/2))])+'>'+ \
                ''.join([' ' for i in range((int)(50-percentage/2))])+ \
                (']  %0.2f%%  %s/s    ' % (percentage,sizeread(self.speed))),
        
class Abs_Lists:
    '''Lists,FileList,PlayList 的抽象类'''
    def __init__(self):
        self.songlist=[]
        self.loop_number=0  #信号量
        self.songtemplate={
            'id':'',
            'title':'',
            'artist':'',
            'album':'',
            'status':''
        }
        self.tmplist=self.songtemplate.copy()

    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist])

    def listall(self):
        print '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist])

    def directly_down(self,uri,i):
        '''直接下载，用于试听中得到最终下载地址后调用'''
        filename = self.get_filename(i)
        local_uri=musicdir+filename
        Download(uri,filename,0)

    def play(self,i=0):
        '''试听，播放'''
        uri=''
        global play_over
        filename=self.get_filename(i)
        print "preparing ",filename
        local_uri=musicdir+filename
        if os.path.exists(local_uri):
            print filename,u'已存在!'
            print "directly play..."
            play_over=0 #通知原来播放线程，你已被打断，退出吧，别保存！
            if os.name=='posix':
                os.system("pkill "+player)
            os.system(player+' "'+local_uri+'"')
            return
        uri = self.find_final_uri(i)
        if uri:
            thread.start_new_thread(self.directly_down,(uri,i,))
            cache_uri=local_uri+'.downloading'
            if os.name=='posix':
                os.system("pkill "+player)
            play_over=0 #通知原来播放线程，你已被打断，退出吧，别保存！
            time.sleep(2)   #应该选一个恰当的值...
            play_over=1
            print "here play_over is ",play_over
            if os.name=='posix':
                os.system('mid3iconv -e gbk "'+cache_uri +'"')
            os.system(player+' "'+cache_uri+'"')

            '''自动播放完成后保存，播到一半切换歌曲则不保存'''
            if play_over:   
                '''可能意外自动终止，比如上面sleep时间不够长等，然后就保存，'''
                #os.rename(cache_uri, local_uri)
                print "it seems like you love this song, so save file ",filename
            else:
                print "the song was interrupted..."
                play_over=1 #恢复默认自动播放完毕状态
        else:
            print "Error, maybe the page is protected..."

    def autoplay(self,start=0):
        '''从当前首开始依次播放'''
        flag=1
        print "begin to play",self.get_title(start)
        while start < len(self.songlist) and self.loop_number < 2:   #loop_number为信号量
            if flag==1:
                print "set loop number"
                self.loop_number = self.loop_number + 1
                flag=0
            self.play(start)
            print "begin next"
            start = start + 1
            #self.current_path = self.current_path + 1
        self.loop_number = self.loop_number - 1

    def get_filename(self,i=0):
        song=self.songlist[i]
        filename=song['title']+'-'+song['artist']+'.mp3'
        return filename

    def get_title(self,i=0):
        song=self.songlist[i]
        return song['title']

    def get_artist(self,i=0):
        song=self.songlist[i]
        return song['artist']

    def get_id(self,i=0):
        song=self.songlist[i]
        return song['id']

    def down_lyrics(self,i=0):
        lyrics_uri_template='http://g.top100.cn/7872775/html/lyrics.html?id=%s'
        p=LyricsParser()
        print u'正在获取"'+key+u'"的歌词',
        print search_uri_template%key
        html=urllib2.urlopen(search_uri_template%key).read()
        #print html
        p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
        self.songlist=p.songlist
        print 'done!'
        
    def find_final_uri(self,i=0):
        '''找到最终真实下载地址，以供下一步DownLoad类下载'''
        song=self.songlist[i]
        songurl="http://www.google.cn/music/top100/musicdownload?id="+song['id']
        try:
            text = urllib2.urlopen(songurl).read()
        except:
            print "Reading URL Error: %s" % local_uri
            return
        s=SongParser()
        s.feed(text)
        return s.url

    def downone(self,i=0):
        '''下载榜单中的一首歌曲 '''
        filename = self.get_filename(i)
        localuri = musicdir + filename
        if os.path.exists(localuri):
            print filename,u'已存在!'
            return
        url=self.find_final_uri(i)
        if url:
            Download(url,filename,1)
        else:   #下载页有验证码时url为空
            print u'出错了,也许是google加了验证码,请换IP后再试或等24小时后再试...'

    def downall(self):
        '''下载榜单中的所有歌曲'''
        [self.downone(i) for i in range(len(self.songlist))]

    def download(self,songids=[]):
        '''下载榜单的特定几首歌曲,传入序号的列表指定要下载的歌'''
        [self.downone(i) for i in songids if i in range(len(self.songlist))]
            
class Lists(Abs_Lists):
    '''榜单类,可以自动处理分页的榜单页面'''
    def __init__(self):
        Abs_Lists.__init__(self)

        self.songlists={
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

    def get_list(self,stype):
        '''获取特定榜单'''
        if stype in self.songlists:
            p=ListParser()
            print u'正在获取"'+stype+u'"的歌曲列表',
            sys.stdout.flush()
            for i in range(0,self.songlists[stype][1],25):
            #for i in range(0,25,25):
                try:
                    html=urllib2.urlopen(urltemplate%(self.songlists[stype][0],i)).read()
                    p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
                    print '.',
                    sys.stdout.flush()
                except:
                    print 'Error! Maybe the internet is not well...'
                    return
            self.songlist=p.songlist
            print 'done!'
        else:
            #raise Exception
            print u'未知列表:"'+str(stype)+u'",仅支持以下列表: '+u'、'.join(
            ['"%s"'%key for key in self.songlists])

 
class SearchLists(Abs_Lists):
    '''google music 搜索'''
    def __init__(self):
        Abs_Lists.__init__(self)

    def get_list(self,key):
        key = re.sub((r'\ '),'+',key)
        search_uri_template = 'http://www.google.cn/music/search?q=%s&aq=f'
        p=ListParser()
        print u'正在获取"'+key+u'"的搜索结果列表'
        html=urllib2.urlopen(search_uri_template%key).read()
        #print html
        p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
        self.songlist=p.songlist
        print 'done!'

class DownloadLists(Abs_Lists):
    '''下载列表管理'''
    def __init__(self):
        Abs_Lists.__init__(self)

    def get_list(self):
        pass

    def add(self,title,artist,id):
        self.tmplist['artist']=artist
        self.tmplist['title']=title
        self.tmplist['id']=id
        self.songlist.append(self.tmplist.copy())
        self.tmplist=self.songtemplate.copy()
        self.downone(len(self.songlist)-1)

class FileList(Abs_Lists):
    '''本地文件列表'''
    def __init__(self,top):
        Abs_Lists.__init__(self)

    def get_list(self,top):
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
        if os.path.basename(file).split('.')[-1]=='cache':
            print 'ignoring '+os.path.basename(file)
            return
        if os.path.basename(file).split('.')[-1]=='downloading':
            print 'ignoring '+os.path.basename(file)
            return
        self.tmplist['artist']=os.path.basename(file).split('-')[1].split('.')[0]
        self.tmplist['title']=os.path.basename(file).split('-')[0]
        self.tmplist['id']=len(self.songlist)
        self.songlist.append(self.tmplist.copy())
        self.tmplist=self.songtemplate.copy()
        print 'adding '+os.path.basename(file)

    def delete_file(self,i):
        filename=self.get_filename()
        filename = unicode(filename,'utf8')
        local_uri = musicdir + filename
        os.remove(local_uri)

class PlayList(Abs_Lists):
    '''读写歌词文件'''
    #def __init__(self,config_file=gmbox_home+'default.xml'):
    def __init__(self,config_file=playlist_path):
        Abs_Lists.__init__(self)

        if os.path.exists(config_file):
            self.xmldoc = minidom.parse(config_file)
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
            f = file(config_file,'w')
            writer = codecs.lookup('utf-8')[3](f)
            self.xmldoc.writexml(writer)
            writer.close
        self.root = self.xmldoc.documentElement

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

    def delete(self,index):
        item = self.getElementByIndex(index)
        self.root.removeChild(item)
        f = file(gmbox_home+'default.xml','w')
        writer = codecs.lookup('utf-8')[3](f)
        self.xmldoc.writexml(writer)
        writer.close

    def get_information(self,index):
        items = self.xmldoc.getElementsByTagName('item')
        print "the first item is :"
        print items[index].toxml()
    def getElementByIndex(self,index):
        items = self.xmldoc.getElementsByTagName('item')
        return items[index]

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

class ConfigFile:
    '''读写配置文件'''
    def __init__(self,configfile=gmbox_home+"gmboxrc"):
        if os.path.exists(configfile):
            print "found config file 'gmboxrc' , begin to init..."
            self.xmldoc = minidom.parse(configfile)
            self.set_musicdir()
            self.set_playlist_path()
        else:
            print "No config file 'gmboxrc' found, so create it..."
            self.init_configfile()

    def init_configfile(self):
        global musicdir
        global playlist_path

        impl = minidom.getDOMImplementation()
        self.xmldoc = impl.createDocument(None, 'gmbox_config', None)
        root = self.xmldoc.documentElement
        node = self.xmldoc.createElement("music_dir")
        node.setAttribute("id","e1")
        text = self.xmldoc.createTextNode(musicdir)
        node.appendChild(text)
        root.appendChild(node)
        node = self.xmldoc.createElement("playlist_path")
        node.setAttribute("id","e2")
        text = self.xmldoc.createTextNode(playlist_path)
        node.appendChild(text)
        root.appendChild(node)
        f = file(gmbox_home+'gmboxrc','w')
        writer = codecs.lookup('utf-8')[3](f)
        #self.xmldoc.writexml(writer,"  ", "","\n    ","UTF-8")
        #self.xmldoc.writexml(writer,"  ", "","\n","UTF-8")
        self.xmldoc.writexml(writer)
        writer.close

    def set_keybing(self):
        actions = self.xmldoc.getElementsByTagName('action')
        for action in actions:
            name = item.getAttribute('name')
    def set_musicdir(self):
        global musicdir
        root = self.xmldoc.documentElement
        #node = root.getElementById('e1')
        #node = root.getElementsByTagName('music_dir')
        #node = root.firstChild
        #musicdir = node.data
        musicdir = self.getTagText(root,"music_dir")
        print u'歌曲目录:',musicdir

    def set_playlist_path(self):
        global playlist_path
        root = self.xmldoc.documentElement
        #node = root.getElementByTagId('e2')
        #node = root.getElementsByTagName('playlist_path')
        #node = root.firstChild
        #playlist_path = node.data
        playlist_path = self.getTagText(root,"playlist_path")
        print u'播放列表:',playlist_path

    def getTagText(self,root,tag):
        '''得到文本节点的值'''
        node = root.getElementsByTagName(tag)[0]
        rc = ""
        for node in node.childNodes:
            #if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

if __name__ == '__main__':
    print u"请勿直接执行此文件,图选界面请执行MainWindow.py,命令行界面请执行cli.py"
    
