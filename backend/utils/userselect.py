#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/04/03 10:12
# @Author  : ZhangJun
# @FileName: userselect.py

import os
import traceback
from utils.log import log as log


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEF_DIR = os.path.join(BASE_DIR, 'construct')

class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class UserSelect(object):
    def __init__(self):
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        log.debug(apppath)

if __name__ == '__main__':
    us = UserSelect()

