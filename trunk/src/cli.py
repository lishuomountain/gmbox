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

'''gmbox的命令行界面'''
import sys,copy,cmd
from optparse import OptionParser
from lib.core import *
 
reload(sys)
sys.setdefaultencoding('utf8')

#既然只有国内可以使用google music,就不考虑国际化了,提示都用中文.
class CLI(cmd.Cmd):
    '''解析命令行参数'''
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.currentlist=u'华语新歌'
        self.currentalbumlist=u'影视新碟'
        self.prompt = "gmbox> "

    def default(self,line):
        print line,u' 不支持的命令!'

    def help_lists(self):
        print u'用法: lists\n查看支持的榜单名.'
    def do_lists(self,arg=None):
        print u'目前gmbox支持以下列表: '+u'、'.join(['"%s"'%key for key in songlists])
    def help_albums(self):
        print u'用法: albums\n查看支持的专辑列表名.'
    def do_albums(self,arg=None):
        print u'目前gmbox支持以下专辑列表: '+u'、'.join(['"%s"'%key for key in albums_lists])
    def help_list(self):
        print u'用法: list  <榜单名>\n列出榜单名的所有歌曲,默认列出上次list的榜单或华语新歌.'
    def do_list(self,arg):
        arg=deal_input(arg)
        if arg != '':
            if arg in songlists:
                self.currentlist=arg
            else:
                print u'未知列表:"'+arg+u'"'
                return
        gmbox.get_list(self.currentlist)
        gmbox.listall()
        print self.currentlist,u'包含以上',len(gmbox.songlist),u'首歌.'
    def help_albumslist(self):
        print u'用法: albumslist  <专辑列表名>\n列出专辑列表的所有专辑,默认列出上次albumslist的专辑或影视新碟.'
    def do_albumslist(self,arg):
        arg=deal_input(arg)
        if arg != '':
            if arg in albums_lists:
                self.currentalbumlist=arg
            else:
                print u'未知列表:"'+arg+u'"'
                return
        gmbox.get_album_IDs(self.currentalbumlist)
        gmbox.listallalbum()
        print self.currentalbumlist,u'包含以上',len(gmbox.albumlist),u'个专辑.'
    def help_search(self):
        print u'用法: search  关键字\n搜索关键字'
    def do_search(self,arg):
        arg=deal_input(arg)
        if arg != '':
            gmbox.search(arg)
            gmbox.listall()
        else:
            self.help_search()
    def help_searchalbum(self):
        print u'用法: searchalbum  关键字\n以关键字搜索专辑'
    def do_searchalbum(self,arg):
        arg=deal_input(arg)
        if arg != '':
            gmbox.searchalbum(arg)
            gmbox.listallalbum()
        else:
            self.help_searchalbum()
    def help_downall(self):
        print u'用法: downall\n下载上次list或search的所有歌曲'
    def do_downall(self,arg=None):
        if self._candown():
            gmbox.downall()
            
    def help_downalbum(self):
        print u'用法: downalbum 专辑所在页面URL'
        print u'例子: downalbum http://www.google.cn/music/album?id=Bc21fbc4302aa9dd4'
        
    def do_downalbum(self,arg):
        if self._candownalbum():
            k=[]
            try:
                [k.append(int(t)-1) for t in arg.split()]
            except ValueError:
                print u'downalbum 后面要加数字序号.'
                return
            k=list(set(k))
            if len(k) > 0:
                gmbox.downalbums(k)
            else:
                print u'downalbum 后面要加数字序号.'
            
        """if len(arg.split()) != 1:
            self.help_downalbum()
        else:
            self.albumurl = arg.split()[0]
            gmbox.downalbum(self.albumurl)"""
        
    def help_down(self):
        print u'用法: down num1 [num2 [num3 ...]]\n下载上次list或search的所有歌曲中的一部分,从1开始计数'
    def do_down(self,arg):
        if self._candown():
            k=[]
            try:
                [k.append(int(t)-1) for t in arg.split()]
            except ValueError:
                print u'down 后面要加数字序号.'
                return
            k=list(set(k))
            if len(k) > 0:
                gmbox.down_listed(k)
            else:
                print u'down 后面要加数字序号.'
    def help_config(self):
        print u'用法: config 选项 参数:\nconfig savedir 目录        设置歌曲保存路径\n\
config id3utf8 True|False  设置是否转换ID3信息到UTF-8编码'
    def do_config(self,arg):
        if arg == '':
            print config.item
        else:
            if len(arg.split()) != 2:
                self.help_config()
            else:
                if arg.split()[0]=='savedir':
                    config.savedir_changed(arg.split()[1])
                elif arg.split()[0]=='id3utf8':
                    config.id3utf8_changed(arg.split()[1])
                else:
                    self.help_config()
        
    def help_exit(self):
        print u'用法: exit\n退出gmbox.'
    def do_exit(self,arg):
        sys.exit(0)
    def do_EOF(self,arg):
        print
        sys.exit(0)
    def do_printconfig(self,arg):
        print config.item
    def _candown(self):
        if not gmbox.songlist:
            print u'执行down或downall命令前,需先执行list或search命令'
            return False
        else:
            return True
    def _candownalbum(self):
        if not gmbox.albumlist:
            print u'执行downalbum或downalbumall命令前,需先执行albumslist或searchalbum命令'
            return False
        else:
            return True

def BatchMode():
    parser = OptionParser(version='%prog '+VERSION, prog='gmbox', 
        description=u'不加参数运行可以进入交互模式.否则进入批处理模式,执行参数指定的相应动作后退出.')
    parser.add_option('-b', '--bang', action="store_true", dest='bang', help=u'列出所有支持的榜单名,并退出')
    parser.add_option('-l', '--list', dest='list', metavar=u'榜单名', help=u'列出榜单歌曲')
    parser.add_option('-s', '--search', dest='search', metavar=u'关键词', help=u'搜索关键词')
    parser.add_option('-p', '--print', action="store_true", dest='print', default=True, help=u'search(-s)或list(-l)后的动作,仅打印,默认.')
    parser.add_option('-a', '--downall', action="store_true", dest='downall', help=u'search(-s)或list(-l)后下载全部歌曲.')
    parser.add_option('-d', '--down', action="store", dest='down', metavar=u'"1 3 6"', help=u'search(-s)或list(-l)后下载部分歌曲.后面跟歌曲序号(注意需要引号)')
#    parser.add_option('-m', '--downalbum', dest='downalbum', metavar=u'专辑页面URL', help=u'下载专辑')
    (options, args) = parser.parse_args()
    
    cli=CLI()
    if options.bang:
        cli.do_lists()
    else:
        if options.search:
            cli.do_search(options.search)
        elif options.list:
            cli.do_list(options.list)
        elif options.downalbum:
            cli.do_downalbum(options.downalbum)
        if not(options.search or options.list) and (options.downall or options.down):
            print u'downall(-a)或down(-d)需要配合search(-s)或list(-l)使用.'
            return
        if options.downall:
            cli.do_downall()
        elif options.down:
            cli.do_down(options.down)
            

if __name__ == '__main__':
    if len(sys.argv)==1:
        '''交互模式'''
        cli=CLI()
        cli.cmdloop(u"欢迎使用 gmbox!\n更多信息请访问 http://code.google.com/p/gmbox/\n可以输入 'help' 查看支持的命令")
    else:
        BatchMode()
