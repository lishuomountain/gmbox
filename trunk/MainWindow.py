#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk


class MainWindow(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self)

        self.connect('destroy', gtk.main_quit)      
        self.set_title('GMBox')
        self.set_default_size(800, 600)



def main():
    win = MainWindow();
    win.show_all()
    gtk.main()


if __name__ == '__main__':
    main()
