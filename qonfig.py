#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Name:     qonfig.py
# Author:   xiooli <xioooli[at]yahoo.com.cn>
# Licence:  GPLv3
# Version:  110224

''' configure module for Gmbox-Qt
'''
import sys, os, glib

CONFIG_FILE = 'gmbox-qt.conf'

def get_module_path():
    if hasattr(sys, "frozen"):
        module_path = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
    else:
        module_path = os.path.dirname(unicode(os.path.abspath(__file__), sys.getfilesystemencoding()))
    return module_path

MODULE_PATH = get_module_path()

def get_default_player():
    # use phonon by default
    return

def get_download_folder():
    download_folder = glib.get_user_special_dir(glib.USER_DIRECTORY_MUSIC)
    if download_folder is None:
        download_folder = os.path.expanduser("~/Music")
    return download_folder

# default config
CONFIG = {
    # regular
    "download_folder": './music', #get_download_folder(),
    "filename_template" : "${ALBUM}/${ARTIST} - ${TITLE}",
    "download_cover" : True,
    "download_lyric" : True,
    "show_status_icon" : True,
    # player
    "player_use_internal" : False,
    "player_path" : get_default_player(),
    "player_single" : "${URL}",
    "player_multi" : "${URLS}",
    # downloader
    "downloader_use_internal" : True,
    "downloader_path" : None,
    "downloader_single" : "${URL}",
    "downloader_multi" : "${URLS}",
}

def get_config_folder():
    config_folder = "%s/gmbox" % glib.get_user_config_dir()
    if config_folder is None:
        config_folder = "%s/config/" % MODULE_PATH
    return config_folder

CONFIG_FOLDER = get_config_folder()

def load_config_file():
    config_file_path = "%s/%s" %(CONFIG_FOLDER, CONFIG_FILE)

    if not os.path.exists(config_file_path):
        return CONFIG

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
        if value in ["False", "false", "None", "none", "no", "0"]:
            value = False
        CONFIG[key] = value
    return CONFIG

def save_config_file():
    if not os.path.exists(CONFIG_FOLDER):
        os.mkdir(CONFIG_FOLDER)
    line_end = '\n'
    if sys.platform.startswith('win'):
        line_end = '\r\n'

    config_file_path = "%s/%s" %(CONFIG_FOLDER, CONFIG_FILE)
    config_file = open(config_file_path, "w")
    for key, value in CONFIG.items():
        config_file.write("%s=%s%s" % (key, value, line_end))
    config_file.flush()
    config_file.close()
