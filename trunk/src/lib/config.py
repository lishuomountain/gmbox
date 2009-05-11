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


from xml.dom import minidom
import codecs
import os

# more work:
# 1.ConfigFile inherit from minidom
# 2.Use logging modudle instead of print sentence
# 3.Get music dir from preference tab
# 4.more comments make other's work better
# 5.take some attribute open and close more
# 6.maybe ini file is better!!!


musicdir=userhome+'/Music/google_music/top100/'
playlist_path=gmbox_home+'default.xml'
gmbox_home=userhome+'/.gmbox/'

class ConfigFile():
    '''读写配置文件'''
    def __init__(self):

        configfile = os.path.expanduser('~/.gmbox/gmboxrc')
        
        if os.path.exists(configfile):
            print "found config file 'gmboxrc' , begin to init..."
            self.xmldoc = minidom.parse(configfile)
            self.set_musicdir()
            self.set_playlist_path()
        else:
            print "No config file 'gmboxrc' found, so create it..."
            self.init_configfile()
            

    def init_configfile(self):

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

        root = self.xmldoc.documentElement
        #node = root.getElementById('e1')
        #node = root.getElementsByTagName('music_dir')
        #node = root.firstChild
        #musicdir = node.data
        musicdir = self.getTagText(root,"music_dir")
        print u'歌曲目录:',musicdir

        
    def set_playlist_path(self):
        
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
