#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_module_folder():
    import sys
    import os
    parent_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.dirname(parent_path) + "/googlemusic/"
    sys.path.append(module_path)

if __name__ == '__main__':
    try:
        import googlemusic
    except:
        get_module_folder()

    from gmbox import gmbox
    gmbox.main()
