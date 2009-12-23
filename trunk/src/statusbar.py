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


import gtk
class Statusbar(gtk.Statusbar):
    '''主窗口下面的状态栏'''
    def __init__(self):
        gtk.Statusbar.__init__(self)
        self.textbox = gtk.Label('')
        self.progress = gtk.ProgressBar()
        self.pack_start(self.textbox, True, True)
        self.pack_start(self.progress, False, False)

statusbar = Statusbar()
