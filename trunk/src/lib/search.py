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
