#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import gtk
import gtk.glade
#import pygtk

class MainWindow():
    def __init__(self):

	self.gladefile="gmbox.glade"
	self.xml=gtk.glade.XML(self.gladefile)
	self.window = self.xml.get_widget("window_main")

        self.window.set_title('GMBox')
	self.window.show_all();
        self.window.connect('destroy', gtk.main_quit)      

def main():
    win = MainWindow();
    gtk.main()


if __name__ == '__main__':
    main()
