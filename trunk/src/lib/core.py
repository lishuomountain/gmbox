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

import os, sys, copy, time, re, logging, urllib, urllib2

from parser import *
from const import *
from utils import unistr,sizeread


log = logging.getLogger('lib.core')

# this variable should read from preference
userhome = os.path.expanduser('~')
musicdir=os.path.join(userhome,'Music','google_music','top100')

class Gmbox:
    '''core class
    1. hold songlist and and check to see which and where to download
    '''
    
    def __init__(self):
        self.songlist = None
        self.loop_number=0  #信号量
        self.cached_list={}

    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist])

    def listall(self):
        print '\n'.join(['Num=%d Title="%s" Artist="%s" ID="%s"'%
            (self.songlist.index(song)+1,song['title'],song['artist'],song['id']) 
            for song in self.songlist])

    def directly_down(self,uri,i):
        '''直接下载，用于试听中得到最终下载地址后调用'''
        filename = self.get_filename(i)
        local_uri=os.path.join(musicdir,filename)
        self.download(uri,filename,0)

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
        
        #try:
        text = urllib2.urlopen(songurl).read()
        #except:
        #    log.debug('Reading URL Error')#: %s" % local_uri
        #    return
        s=SongParser()
        s.feed(text)
        return s.url

    def downone(self,i=0,callback=None):
        '''下载榜单中的一首歌曲 '''
        
        filename = self.get_filename(i)
        localuri = os.path.join(musicdir,filename)
        
        if os.path.exists(localuri):
            print filename,u'已存在!'
            return
        
        url = self.find_final_uri(i)
        if url:
            self.download(url,filename,1,callback=callback)
        else:   #下载页有验证码时url为空
            print '出错了,也许是google加了验证码,请换IP后再试或等24小时后再试...'

    def downall(self):
        '''下载榜单中的所有歌曲'''
        [self.downone(i) for i in range(len(self.songlist))]

    def down_listed(self,songids=[],callback=None):
        '''下载榜单的特定几首歌曲,传入序号的列表指定要下载的歌'''
        [self.downone(i,callback) for i in songids if i in range(len(self.songlist))]
            
    
    def download(self, remote_uri, filename, mode=1, callback=None):
        '''下载模式 1 和 试听(缓存)模式 0'''
        #这里不用检测是否文件已存在了,上边的downone或play已检测了
        if mode:
            print u'正在下载:',filename
        else:
            print u'正在缓冲:',filename
        local_uri=os.path.join(musicdir,filename)
        cache_uri=local_uri+'.downloading'
        self.T=self.startT=time.time()
        (self.D,self.speed)=(0,0)
        c=callback if callback else self.update_progress
        c(-1,0,0) #-1做为开始信号
        urllib.urlretrieve(remote_uri, cache_uri, c)
        c(-2,0,0) #-2做为结束信号
        speed=os.stat(cache_uri).st_size/(time.time()-self.startT)
        #下载和试听模式都一样
        if callback==None:
            print '\r['+''.join(['=' for i in range(50)])+ \
                '] 100.00%%  %s/s       '%sizeread(speed)
        os.rename(cache_uri, local_uri)
        if os.name=='posix':
            '''在Linux下转换到UTF 编码，现在只有comment里还是乱码'''
            os.system('mid3iconv -e gbk "'+local_uri + '"')

    def update_progress(self, blocks, block_size, total_size):
        # used by download method
        '''处理进度显示的回调函数'''
        if total_size > 0 and blocks >= 0:
            percentage = float(blocks) / (total_size/block_size+1) * 100
            if int(time.time()) != int(self.T):
                self.speed=(blocks*block_size-self.D)/(time.time()-self.T)
                (self.D,self.T)=(blocks*block_size,time.time())
            print '\r['+''.join(['=' for i in range((int)(percentage/2))])+'>'+ \
                ''.join([' ' for i in range((int)(50-percentage/2))])+ \
                (']  %0.2f%%  %s/s    ' % (percentage,sizeread(self.speed))),

    def get_list(self,stype):
        '''获取特定榜单'''
        if stype in self.cached_list:
            self.songlist=copy.copy(self.cached_list[stype])
            return
        
        if stype in songlists:
            p=ListParser()
            print u'正在获取"'+stype+u'"的歌曲列表',
            sys.stdout.flush()
            for i in range(0, songlists[stype][1], 25):
                try:
#                    r=urllib2.Request(urltemplate%(songlists[stype][0],i))
#                    r.add_header('User-Agent','Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
                    html=urllib2.urlopen(urltemplate%(songlists[stype][0],i)).read()
                    p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
                    print '.',
                    sys.stdout.flush()
                except urllib2.URLError:
                    print 'Error! Maybe the internet is not well...'
                    return
                except:
                    print 'Unknow Error! Please report to ...'
                    return
            print 'done!'
            self.songlist = p.songlist
            self.cached_list[stype]=copy.copy(p.songlist)
        else:
            #raise Exception
            print u'未知列表:"'+str(stype)+u'",仅支持以下列表: '+u'、'.join(
            ['"%s"'%key for key in songlists])
            log.debug('Unknow list:"'+str(stype))

    def search(self,key):
        if 's_'+key in self.cached_list:
            self.songlist=copy.copy(self.cached_list['s_'+key])
            return

        key = re.sub((r'\ '),'+',key)
        p=ListParser()
        print u'正在获取"'+key+u'"的搜索结果列表...',
        sys.stdout.flush()
        try:
            html=urllib2.urlopen(search_uri_template%key).read()
            p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
        except urllib2.URLError:
            print 'Error! Maybe the internet is not well...'
            return
        except:
            print 'Unknow Error! Please report to ...'
            return
        print 'done!'
        self.songlist=p.songlist
        self.cached_list['s_'+key]=copy.copy(p.songlist)
                    
        '''def play(self,i=0):
        #试听，播放
        uri=''
        global play_over
        filename=self.get_filename(i)
        print "preparing ",filename
        local_uri=os.path.join(musicdir,filename)
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

            #自动播放完成后保存，播到一半切换歌曲则不保存
            if play_over:   
                #可能意外自动终止，比如上面sleep时间不够长等，然后就保存，
                #os.rename(cache_uri, local_uri)
                print "it seems like you love this song, so save file ",filename
            else:
                print "the song was interrupted..."
                play_over=1 #恢复默认自动播放完毕状态
        else:
            print "Error, maybe the page is protected..."

    def autoplay(self,start=0):
        #从当前首开始依次播放
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
        self.loop_number = self.loop_number - 1'''
        
#全局实例化
gmbox=Gmbox()
