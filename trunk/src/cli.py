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
from lib.core import *
from lib.const import *
from lib.utils import *
#from lib.config import *
reload(sys)
sys.setdefaultencoding('utf8')

# need more work:
# write a interface transparent layer to import gtk and cli module

#既然只有国内可以使用google music,就不考虑国际化了,提示都用中文.
class CLI(cmd.Cmd):
    '''解析命令行参数'''
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.currentlist=u'华语新歌'
#        self._welcome()
        self.prompt = "gmbox> "
#            ConfigFile()

    def default(self,line):
        print line,u' 不支持的命令!'

    def help_lists(self):
        print u'用法: lists\n查看支持的榜单名.'
    def do_lists(self,arg):
        print u'目前gmbox支持以下列表: '+u'、'.join(['"%s"'%key for key in songlists])
    def help_list(self):
        print u'用法: list  <榜单名>\n列出榜单名的所有歌曲,默认列出上次list的榜单或话语新歌.'
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
    def help_search(self):
        print u'用法: search  关键字\n搜索关键字'
    def do_search(self,arg):
        arg=deal_input(arg)
        if arg != '':
            gmbox.search(arg)
            gmbox.listall()
        else:
            self.help_search()
    def help_downall(self):
        print u'用法: downall\n下载上次list或search的所有歌曲'
    def do_downall(self,arg):
        if self._candown():
            gmbox.downall()
    def help_down(self):
        print u'用法: down num1 [num2 [num3 ...]]\n下载上次list或search的所有歌曲中的一部分,从1开始计数'
    def do_down(self,arg):
        if self._candown():
            k=[]
            try:
                [k.append(int(t)-1) for t in arg.split()]
            except ValueError:
                print u'down 后面要加数字序号.'
            k=list(set(k))
            if len(k) > 0:
                gmbox.down_listed(k)
            else:
                print u'down 后面要加数字序号.'
        
    def help_exit(self):
        print u'用法: exit\n退出gmbox.'
    def do_exit(self,arg):
        sys.exit(0)
    def do_EOF(self,arg):
        print
        sys.exit(0)
        
    def _candown(self):
        if not gmbox.songlist:
            print u'执行down或downall命令前,需先执行list或search命令'
            return False
        else:
            return True

    def _help(self):
        print u"gmbox命令行模式:"
        print u"用法: ",sys.argv[0],u"[选项]..."
        print u" -s                  查看支持的榜单名."
        print u" -l  榜单名          列出榜单名的所有歌曲"
        print u" -d  榜单名 all      下载榜单名的所有歌曲"
        print u" -d  榜单名 0 2 ...  下载榜单名的所有歌曲"
        print u"gmbox交互模式(直接执行gmbox将进入交互模式):"
        print u" lists           查看支持的榜单名."
        print u" list  <榜单名>  列出榜单名的所有歌曲"
        print u" search  关键字  搜索关键字"
        print u" down  all       下载上次list或search得到的所有歌曲"
        print u" down  1 3 ...   下载上次list或search得到的所有歌曲中的一部分,从1开始计数"

    def error(self):
        print sys.argv[0],": invalid option -- ",sys.argv[1]
        print "Try '",sys.argv[0]," --help' for more information"

if __name__ == '__main__':
    if len(sys.argv)==1:
        '''交互模式'''
        cli=CLI()
        cli.cmdloop(u"欢迎使用 gmbox!\n更多信息请访问 http://code.google.com/p/gmbox/\n可以输入 'help' 查看支持的命令")
    else:
        pass
        """'''命令行模式''
            if sys.argv[1]=='-s':
                self._lists()
            elif sys.argv[1]=='-l':
                if len(sys.argv)==3:
                    if os.name=='nt':
                        self.currentlist=sys.argv[2].encode('GBK')
                    else:
                        self.currentlist=sys.argv[2].decode('UTF-8')
                self._list()
            elif sys.argv[1]=='-d':
                list_name = u'华语新歌'
                index=0
                if len(sys.argv)==3:
                    index = sys.argv[2]
                l=Lists()
                l.get_list(list_name)
                #l.downone(int(index))
                #l.download([0,2,6])
                l.downall()
            elif sys.argv[1] == '-s':
                key = '周杰伦'
                l=SearchLists()
                l.get_list(key)
                l.listall()
            elif sys.argv[1]=='-t':
                '''input your function to test here'''
                playlist = PlayList()
                playlist.play(0)
                #playlist.get_information(0)
                #ele = playlist.getElementByIndex(0).getAttribute("id")
                #print ele
                #playlist.delete(ele)
            elif sys.argv[1]=='-h' or sys.argv[1] == '--help':
                self.help()
            else:
                self.error()"""
    
