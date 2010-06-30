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

class QuitDialog(gtk.MessageDialog):
    '''退出确认对话框'''
    def __init__(self, title, message):
        gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO)
        self.set_markup('<big><b>%s</b></big>' % title)
        self.format_secondary_markup(message)

class InfoDialog(gtk.MessageDialog):
    '''验证码信息对话框'''
    def __init__(self, title, message):
        gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
        self.set_markup('<big><b>%s</b></big>' % title)
        self.format_secondary_markup(message)

if __name__ == '__main__':
    dialog = InfoDialog(u'杯具啊', u'由于你短时间下载太多，Google让你输入验证码了。换个IP或者等24小时再试吧。')
    dialog.run()
    dialog.destroy()
