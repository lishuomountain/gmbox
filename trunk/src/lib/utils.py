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


import logging
import os,sys,re

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
    
def find_image_or_data(file_name,basedir=None,dirname='pixbufs'):
    """Using the iamge_name, search in the common places. Return the path for
    the image or None if the image couldn't be found."""

    # the order is the priority, so keep global paths before local paths
    if not basedir:
        current_dir = os.path.abspath(os.path.dirname(__file__))
    else:
        current_dir = basedir
    common_paths = [
            os.path.join(current_dir, '..', dirname),
            os.path.join(current_dir, '..', '..', dirname),
            os.path.join(current_dir, dirname),
            os.path.join(sys.prefix, 'share', 'gmbox', dirname)]

    for path in common_paths:
        filename = os.path.join(path, file_name)
        if os.access(filename, os.F_OK):
            return filename
    print 'not found:',file_name
    return None

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

def deal_input(str):
    if os.name=='nt':
        return str.decode('GBK')
    else:
        return str.decode('UTF-8')

def get_attrs_value_by_name(attrs, name):
    if not attrs:
        return None
    (n,v)=zip(*attrs)
    n,v=list(n),list(v)
    return v[n.index(name)] if name in n else None
    
entityref = re.compile('&([a-zA-Z][a-zA-Z0-9]*);')
entityrefs={
#"quot":unichr(34),
#"amp":unichr(38),
#"lt":unichr(60),
#"gt":unichr(62),
"nbsp":unichr(160),
"iexcl":unichr(161),
"cent":unichr(162),
"pound":unichr(163),
"curren":unichr(164),
"yen":unichr(165),
"brvbar":unichr(166),
"sect":unichr(167),
"uml":unichr(168),
"copy":unichr(169),
"ordf":unichr(170),
"laquo":unichr(171),
"not":unichr(172),
"shy":unichr(173),
"reg":unichr(174),
"macr":unichr(175),
"deg":unichr(176),
"plusmn":unichr(177),
"sup2":unichr(178),
"sup3":unichr(179),
"acute":unichr(180),
"micro":unichr(181),
"para":unichr(182),
"middot":unichr(183),
"cedil":unichr(184),
"sup1":unichr(185),
"ordm":unichr(186),
"raquo":unichr(187),
"frac14":unichr(188),
"frac12":unichr(189),
"frac34":unichr(190),
"iquest":unichr(191),
"Agrave":unichr(192),
"Aacute":unichr(193),
"Acirc":unichr(194),
"Atilde":unichr(195),
"Auml":unichr(196),
"Aring":unichr(197),
"AElig":unichr(198),
"Ccedil":unichr(199),
"Egrave":unichr(200),
"Eacute":unichr(201),
"Ecirc":unichr(202),
"Euml":unichr(203),
"Igrave":unichr(204),
"Iacute":unichr(205),
"Icirc":unichr(206),
"Iuml":unichr(207),
"ETH":unichr(208),
"Ntilde":unichr(209),
"Ograve":unichr(210),
"Oacute":unichr(211),
"Ocirc":unichr(212),
"Otilde":unichr(213),
"Ouml":unichr(214),
"times":unichr(215),
"Oslash":unichr(216),
"Ugrave":unichr(217),
"Uacute":unichr(218),
"Ucirc":unichr(219),
"Uuml":unichr(220),
"Yacute":unichr(221),
"THORN":unichr(222),
"szlig":unichr(223),
"agrave":unichr(224),
"aacute":unichr(225),
"acirc":unichr(226),
"atilde":unichr(227),
"auml":unichr(228),
"aring":unichr(229),
"aelig":unichr(230),
"ccedil":unichr(231),
"egrave":unichr(232),
"eacute":unichr(233),
"ecirc":unichr(234),
"euml":unichr(235),
"igrave":unichr(236),
"iacute":unichr(237),
"icirc":unichr(238),
"iuml":unichr(239),
"eth":unichr(240),
"ntilde":unichr(241),
"ograve":unichr(242),
"oacute":unichr(243),
"ocirc":unichr(244),
"otilde":unichr(245),
"ouml":unichr(246),
"divide":unichr(247),
"oslash":unichr(248),
"ugrave":unichr(249),
"uacute":unichr(250),
"ucirc":unichr(251),
"uuml":unichr(252),
"yacute":unichr(253),
"thorn":unichr(254),
"yuml":unichr(255),
"OElig":unichr(338),
"oelig":unichr(339),
"Scaron":unichr(352),
"scaron":unichr(353),
"Yuml":unichr(376),
"fnof":unichr(402),
"circ":unichr(710),
"tilde":unichr(732),
"Alpha":unichr(913),
"Beta":unichr(914),
"Gamma":unichr(915),
"Delta":unichr(916),
"Epsilon":unichr(917),
"Zeta":unichr(918),
"Eta":unichr(919),
"Theta":unichr(920),
"Iota":unichr(921),
"Kappa":unichr(922),
"Lambda":unichr(923),
"Mu":unichr(924),
"Nu":unichr(925),
"Xi":unichr(926),
"Omicron":unichr(927),
"Pi":unichr(928),
"Rho":unichr(929),
"Sigma":unichr(931),
"Tau":unichr(932),
"Upsilon":unichr(933),
"Phi":unichr(934),
"Chi":unichr(935),
"Psi":unichr(936),
"Omega":unichr(937),
"alpha":unichr(945),
"beta":unichr(946),
"gamma":unichr(947),
"delta":unichr(948),
"epsilon":unichr(949),
"zeta":unichr(950),
"eta":unichr(951),
"theta":unichr(952),
"iota":unichr(953),
"kappa":unichr(954),
"lambda":unichr(955),
"mu":unichr(956),
"nu":unichr(957),
"xi":unichr(958),
"omicron":unichr(959),
"pi":unichr(960),
"rho":unichr(961),
"sigmaf":unichr(962),
"sigma":unichr(963),
"tau":unichr(964),
"upsilon":unichr(965),
"phi":unichr(966),
"chi":unichr(967),
"psi":unichr(968),
"omega":unichr(969),
"thetasym":unichr(977),
"upsih":unichr(978),
"piv":unichr(982),
"ensp":unichr(8194),
"emsp":unichr(8195),
"thinsp":unichr(8201),
"zwnj":unichr(8204),
"zwj":unichr(8205),
"lrm":unichr(8206),
"rlm":unichr(8207),
"ndash":unichr(8211),
"mdash":unichr(8212),
"lsquo":unichr(8216),
"rsquo":unichr(8217),
"sbquo":unichr(8218),
"ldquo":unichr(8220),
"rdquo":unichr(8221),
"bdquo":unichr(8222),
"dagger":unichr(8224),
"Dagger":unichr(8225),
"bull":unichr(8226),
"hellip":unichr(8230),
"permil":unichr(8240),
"prime":unichr(8242),
"Prime":unichr(8243),
"lsaquo":unichr(8249),
"rsaquo":unichr(8250),
"oline":unichr(8254),
"frasl":unichr(8260),
"euro":unichr(8364),
"image":unichr(8465),
"weierp":unichr(8472),
"real":unichr(8476),
"trade":unichr(8482),
"alefsym":unichr(8501),
"larr":unichr(8592),
"uarr":unichr(8593),
"rarr":unichr(8594),
"darr":unichr(8595),
"harr":unichr(8596),
"crarr":unichr(8629),
"lArr":unichr(8656),
"uArr":unichr(8657),
"rArr":unichr(8658),
"dArr":unichr(8659),
"hArr":unichr(8660),
"forall":unichr(8704),
"part":unichr(8706),
"exist":unichr(8707),
"empty":unichr(8709),
"nabla":unichr(8711),
"isin":unichr(8712),
"notin":unichr(8713),
"ni":unichr(8715),
"prod":unichr(8719),
"sum":unichr(8721),
"minus":unichr(8722),
"lowast":unichr(8727),
"radic":unichr(8730),
"prop":unichr(8733),
"infin":unichr(8734),
"ang":unichr(8736),
"and":unichr(8743),
"or":unichr(8744),
"cap":unichr(8745),
"cup":unichr(8746),
"int":unichr(8747),
"there4":unichr(8756),
"sim":unichr(8764),
"cong":unichr(8773),
"asymp":unichr(8776),
"ne":unichr(8800),
"equiv":unichr(8801),
"le":unichr(8804),
"ge":unichr(8805),
"sub":unichr(8834),
"sup":unichr(8835),
"nsub":unichr(8836),
"sube":unichr(8838),
"supe":unichr(8839),
"oplus":unichr(8853),
"otimes":unichr(8855),
"perp":unichr(8869),
"sdot":unichr(8901),
"lceil":unichr(8968),
"rceil":unichr(8969),
"lfloor":unichr(8970),
"rfloor":unichr(8971),
"lang":unichr(9001),
"rang":unichr(9002),
"loz":unichr(9674),
"spades":unichr(9824),
"clubs":unichr(9827),
"hearts":unichr(9829),
"diams":unichr(9830)
}
def entityrefstr(m):
    '''给re.sub做第二个参数,返回&eacute;等对应的中文'''
    if m.group(1) in entityrefs:
        return entityrefs[m.group(1)]
    else:
        return '&'+m.group(1)+';'

