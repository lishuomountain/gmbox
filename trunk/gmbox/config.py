#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import gtk

def get_module_path():
    if hasattr(sys, "frozen"):
        module_path = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
    else:
        module_path = os.path.dirname(unicode(os.path.abspath(__file__), sys.getfilesystemencoding()))
    return module_path

MODULE_PATH = get_module_path()

def create_icon_dict():
    icon_names = ["song", "songlist", "directory", "refresh"]
    icon_dict = {}
    for name in icon_names:
        icon_path = "%s/pixbufs/%s.png" % (MODULE_PATH, name)
        icon = gtk.gdk.pixbuf_new_from_file(icon_path)
        icon_dict[name] = icon
    return icon_dict

ICON_DICT = create_icon_dict()

def get_download_foler():
    # check program folder writable, otherwise use home foler
    if os.access(MODULE_PATH, os.W_OK):
        return "%s/download" % MODULE_PATH
    else:
        return os.path.expanduser("~/music")

# default config
CONFIG = {
    # regular
    "download_folder": get_download_foler(),
    "filename_template" : "${ALBUM}/${ARTIST} - ${TITLE}",
    "use_internal_player" : False,
    "use_internal_downloader" : True,
    "download_cover" : True,
    "download_lyric" : True,
    # player
    "player_path" : "vlc",
    "player_single" : "--one-instance ${URL}",
    "player_multi_type" : "septate",
    "player_septate" : "--one-instance ${URLS}",
    "player_poll" : "--one-instance ${URL}",
    "player_tempfile" : "--one-instance ${FILEPATH}",
    # downloader
    "downloader_path" : "wget",
    "downloader_single" : "${URL} -O ${FILEPATH}",
    "downloader_multi_type" : "septate",
    "downloader_septate" : "${URLS}",
    "downloader_poll" : "${URL} -O ${FILEPATH}",
    "downloader_tempfile" : "${FILEPATH}",
}

CONFIG_PATHS = [
    "%s/gmbox.cfg" % MODULE_PATH,
    os.path.expanduser("~/.gmbox.cfg")
]

def load_config_file():
    for path in CONFIG_PATHS:        
        if os.path.exists(path):        
            config_file = open(path)
            text = config_file.read()
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if line == "":
                    continue                
                key, value = line.split("=", 1)
                if value in ["True", "true", "yes", "1"]:
                    value = True
                if value in ["False", "false", "no", "0"]:
                    value = False
                CONFIG[key] = value   

def save_config_file():
    for path in CONFIG_PATHS:
        if os.access(os.path.dirname(path), os.W_OK):
            config_file = open(path, "w")
            for key, value in CONFIG.items():
                config_file.write("%s=%s\n" % (key, value))
            config_file.flush()
            config_file.close()
            break
