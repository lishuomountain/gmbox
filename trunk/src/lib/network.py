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


import os, sys
import urllib2
import re
import logging

from const import *
from parser import ListParser
from core import Abs_Lists
from utils import unistr

log = logging.getLogger('lib.network')

# this variable should read from preference
userhome = os.path.expanduser('~')
musicdir=userhome+'/Music/google_music/top100/'

# should write to const
urltemplate="http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d"
searchtemplate="http://www.google.cn/music/search?q=%E5%A4%A9%E4%BD%BF%E7%9A%84%E7%BF%85%E8%86%80&aq=f"
lyricstemplate='http://g.top100.cn/7872775/html/lyrics.html?id=S8ec32cf7af2bc1ce'


class download:
    '''下载文件的类'''
    def __init__(self, remote_uri, filename, mode=1):
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


    @classmethod
    def get_list(self,stype):
        '''获取特定榜单'''

        if stype in songlists:
            p=ListParser()
            log.debug('Begining retrieve list : ' + stype)
            #sys.stdout.flush()
            for i in range(0, songlists[stype][1], 25):
                #try:
                    html=urllib2.urlopen(urltemplate%(songlists[stype][0],i)).read()
                    p.feed(re.sub(r'&#([0-9]{2,5});',unistr,html))
                    
                    #print '.',
                    #sys.stdout.flush()
                #except:
                #    print 'Error! Maybe the internet is not well...'
                #    return
            return p.songlist
            #print 'done!'
        else:
            #raise Exception
            log.debug('Unknow list:"'+str(stype))
