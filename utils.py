#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Name:     utils.py
# Author:   xiooli <xioooli[at]yahoo.com.cn>
# Licence:  GPLv3
# Version:  110224

''' 
'''
import urllib
def myurlencode(string):
    return urllib.quote(string.encode('utf8'))
