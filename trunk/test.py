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
        self.window.set_default_size(800, 600)
        self.window.connect('destroy', gtk.main_quit)      
	self.window.show_all();

def main():
    win = MainWindow();
    gtk.main()


if __name__ == '__main__':
    main()
