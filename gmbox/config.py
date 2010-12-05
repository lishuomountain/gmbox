#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import gtk
import platform
import glib

def get_module_path():
    if hasattr(sys, "frozen"):
        module_path = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
    else:
        module_path = os.path.dirname(unicode(os.path.abspath(__file__), sys.getfilesystemencoding()))
    return module_path

MODULE_PATH = get_module_path()

def create_icon_dict():
    icon_names = ["gmbox", "song", "songlist", "directory", "refresh", "info"]
    icon_dict = {}
    for name in icon_names:
        icon_path = "%s/pixbufs/%s.png" % (MODULE_PATH, name)
        icon = gtk.gdk.pixbuf_new_from_file(icon_path)
        icon_dict[name] = icon
    return icon_dict

ICON_DICT = create_icon_dict()

def get_download_folder():
    download_folder = glib.get_user_special_dir(glib.USER_DIRECTORY_MUSIC)
    if download_folder is None:
        download_folder = os.path.expanduser("~/Music")
    return download_folder

# default config
CONFIG = {
    # regular
    "download_folder": get_download_folder(),
    "filename_template" : "${ALBUM}/${ARTIST} - ${TITLE}",
    "download_cover" : True,
    "download_lyric" : True,
    "show_status_icon" : True,
    # player
    "player_use_internal" : True,
    "player_path" : "vlc",
    "player_single" : "--one-instance ${URL}",
    "player_multi" : "--one-instance ${URLS}",
    # downloader
    "downloader_use_internal" : True,
    "downloader_path" : "wget",
    "downloader_single" : "${URL} -O ${FILEPATH}",
    "downloader_multi" : "${URL} -O ${FILEPATH}",
}

def get_config_folder():
    config_folder = "%s/gmbox" % glib.get_user_config_dir()
    if config_folder is None:
        config_folder = "%s/config/" % MODULE_PATH
    return config_folder

CONFIG_FOLDER = get_config_folder()

def load_config_file(): 
    config_file_path = "%s/gmbox.conf" % CONFIG_FOLDER

    if not os.path.exists(config_file_path):
        return
    
    config_file = open(config_file_path) 
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
    if not os.path.exists(CONFIG_FOLDER):
        os.mkdir(CONFIG_FOLDER)
        
    config_file_path = "%s/gmbox.conf" % CONFIG_FOLDER
    config_file = open(config_file_path, "w")
    for key, value in CONFIG.items():
        config_file.write("%s=%s\n" % (key, value))
    config_file.flush()
    config_file.close()
