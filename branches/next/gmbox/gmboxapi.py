#!/usr/bin/env python
# -*- coding: utf-8 -*-

# exaile-plugin-gmbox - exaile plugin to support google.cn music
# Copyright (C) 2010 muzuiget
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

from lib.core import *
from lib.const import *
from gmlist import listing_const_dict

class GmBoxAPI(Gmbox):
    
    def find_final_uri(self, id):
        '''找到最终真实下载地址，以供下一步DownLoad类下载'''
        songurl = song_url_template % (id,)
        html = self.get_url_html(songurl)
        captcha = captcha_reg.findall(html)
        if captcha:
            print '杯具，google让你输入验证码了。。。换个IP或者等等再试吧。'
            return None
        else:
            s = SongParser()
            s.feed(html)
            return s.url
        
    def get_stream_url(self, sid):
        '''获取试听版下载地址，按照flash播放器所用的歌词xml信息'''
        sig = hashlib.md5(flash_player_key + sid).hexdigest()
        xml_url = song_streaming_url_template % (sid, sig)
        try:
            xml_string = self.get_url_html(xml_url, False)
            dom = minidom.parseString(xml_string)
            url = dom.getElementsByTagName('songUrl')[0].childNodes[0].data
        except:
            return None
        return url
        
    def get_list(self, stype, page=1):
        '''获取特定榜单'''
        self.downalbumnow = False
        cache_key = 'l_' + stype + str(page)
        if cache_key in self.cached_list:
            self.songlist = copy.copy(self.cached_list[cache_key])
            return
        
        if stype in listing_const_dict:
            p = ListParser()
            print u'正在获取"' + stype + u'"的歌曲列表',
            sys.stdout.flush()
#           for i in range(0, songlists[stype][1], 25):
            i = (page - 1) * 25
            html = self.get_url_html(list_url_template % (listing_const_dict[stype], i))
            p.feed(html)
            print '.',
            sys.stdout.flush()
#            if callback:
#                callback( int(i / 25) + 1, (songlists[stype][1] / 25) )
            print 'done!'
            self.songlist = p.songlist
            self.cached_list[cache_key] = copy.copy(p.songlist)
            return self.check_if_has_more(html)
        else:
            #TODO:raise Exception
            print u'未知列表:"' + str(stype) + u'",仅支持以下列表: ' + u'、'.join(
            ['"%s"' % key for key in songlists])
            log.debug('Unknow list:"' + str(stype))
            return None
            
    def get_album_IDs(self, albumlist_name, page=1):
        '''获取专辑列表中的专辑ID'''
        cache_key = 'aid_' + albumlist_name + str(page)
        if cache_key in self.cached_list:
            self.albumlist = copy.copy(self.cached_list[cache_key])
            return
        if albumlist_name in listing_const_dict:
            p = AlbumListParser()
            print u'正在获取"' + albumlist_name + u'"的专辑列表',
            sys.stdout.flush()
#            for i in range(0, albums_lists[albumlist_name][1], 10):
            i = (page - 1) * 10
            html = self.get_url_html(albums_list_url_template % (listing_const_dict[albumlist_name], i))
            p.feed(html)
            print '.',
            sys.stdout.flush()
#            if callback:
#                callback(int(i / 10) + 1, (albums_lists[albumlist_name][1] / 10))
            print 'done!'
            self.albumlist = p.albumlist
            self.cached_list[cache_key] = copy.copy(p.albumlist)
            return self.check_if_has_more(html)
        else:
            #TODO:raise Exception
            print u'未知专辑列表:"' + str(albumlist_name) + u'",仅支持以下列表: ' + u'、'.join(
            ['"%s"' % key for key in albums_lists])
            return None
        
    def get_albumlist(self, id):
        '''获取专辑的信息，包括专辑名、歌手名和歌曲列表'''
        albumid = id
        self.downalbumnow = True
        if 'a_' + albumid in self.cached_list:
            self.songlist = copy.copy(self.cached_list['a_' + albumid][0])
            self.albuminfo = copy.copy(self.cached_list['a_' + albumid][1])
            return
        
        #p = ListParser()
        p = XmlAlbumParser()
        print u'正在获取专辑信息',
        sys.stdout.flush()
        #html = self.get_url_html(album_song_list_url_template%albumid)
        #p.feed(html)
        #统一用get_url_html读取数据,日后如果要换user-agent之类也方便维护
        xml = self.get_url_html(xml_album_song_list_url_template % albumid, need_pre_deal=False)
        p.feed(xml)

        print 'done!'
        self.songlist = p.songlist
        self.albuminfo = p.albuminfo
        self.cached_list['a_' + albumid] = copy.copy((p.songlist, p.albuminfo))
        
    def search(self, key, page=1):
        '''搜索关键字'''
        self.downalbumnow = False
        cache_key = 's_' + key + str(page)
        if cache_key in self.cached_list:
            self.songlist = copy.copy(self.cached_list[cache_key])
            return

        key = re.sub((r'\ '), '+', key)
        p = ListParser()
        print u'正在获取"' + key + u'"的搜索结果列表...',
        sys.stdout.flush()
        pnum = (page - 1) * 20
        html = self.get_url_html(search_url_template % (key, pnum))
        p.feed(html)
        sys.stdout.flush()
        print 'done!'
        self.songlist = p.songlist
        self.cached_list[cache_key] = copy.copy(p.songlist)
        return self.check_if_has_more(html)
        
    def searchalbum(self, key, page=1):
        '''搜索关键字'''
        cache_key = 'said_' + key + str(page)
        if cache_key in self.cached_list:
            self.albumlist = copy.copy(self.cached_list[cache_key])
            return

        key = re.sub((r'\ '), '+', key)
        p = AlbumListParser()
        print u'正在获取"' + key + u'"的专辑搜索结果列表...',
        sys.stdout.flush()
        pnum = (page - 1) * 20
        html = self.get_url_html(albums_search_url_template % (key, pnum))
        p.feed(html)
        sys.stdout.flush()
        print 'done!'
        self.albumlist = p.albumlist
        self.cached_list[cache_key] = copy.copy(p.albumlist)
        return self.check_if_has_more(html)
        
    def check_if_has_more(self, html):
        '''相当与Gmbox的__get_pnum_by_html方法'''
        if re.match(r'.*href="(.*?)" id="next_page"', html, re.S):
            return True
        else:
            return False

gmboxapi = GmBoxAPI()
songlists_dict = songlists
albumslists_dict = albums_lists

if __name__ == "__main__":
    print gmboxapi.get_stream_url("S1ac80d75942c4de2")

