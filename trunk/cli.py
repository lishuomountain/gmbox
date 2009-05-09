#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''gmbox的命令行界面'''
import sys
from gmbox import *

def deal_input(str):
    if os.name=='nt':
        return str.decode('GBK')
    else:
        return str.decode('UTF-8')
#既然只有国内可以使用google music,就不考虑国际化了,提示都用中文.
class CLI:
    '''解析命令行参数'''
    def __init__(self):
        self.currentlist=u'华语新歌'
        self.l=None
        if len(sys.argv)==1:
            '''交互模式'''
            self.welcome()
            ConfigFile()
            while 1:
                command=raw_input('gmbox>')
                if command =='exit':
                    return
                else:
                    self.deal_command(command)
        else:
            '''命令行模式'''
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
                self.error()
    
    def deal_command(self,command):
        if command.split()[0]=='lists':
            self._lists()
        elif command.split()[0]=='list':
            if len(command.split()) > 1:
                self.currentlist=deal_input(command.split()[1])
            self._list()
        elif command.split()[0]=='search':
            if len(command.split()) > 1:
                key=deal_input(command.split()[1])
                self._search(key)
            else:
                print u'用法: search 关键字'
        elif command.split()[0]=='down':
            if not self.l:
                print u'执行down命令前需先执行list或者search命令'
                return
            if len(command.split()) > 1:
                if command.split()[1]=='all':
                    self.l.downall()
            else:
                print u'用法: down all 或者 down n1 n2 ...'
            
        elif command.split()[0]=='help':
            self.help()
        else:
            print u'未知命令:',command,u'需要帮助请输入 help'
        
    def _lists(self):
        print u'目前gmbox支持以下列表: '+u'、'.join(['"%s"'%key for key in Lists().songlists])
    def _list(self):
        self.l=Lists()
        self.l.get_list(self.currentlist)
        self.l.listall()
        print self.currentlist,u'包含以上',len(self.l.songlist),u'首歌.'
    def _search(self,key):
        self.l=SearchLists()
        self.l.get_list(key)
        self.l.listall()
        
    def welcome(self):
        print u"欢迎使用 gmbox!"
        print u"更多信息请访问 http://code.google.com/p/gmbox/"
        print u"可以输入 'help' 查看支持的命令"

    def help(self):
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
        print u" down  all       下载上次list命令指定的榜单的所有歌曲,需要先执行list"
        print u" down  0 2 ...   下载上次list命令指定的榜单的指定歌曲,需要先执行list"

    def error(self):
        print sys.argv[0],": invalid option -- ",sys.argv[1]
        print "Try '",sys.argv[0]," --help' for more information"

if __name__ == '__main__':
    CLI()
    
