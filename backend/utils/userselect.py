#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/04/03 10:12
# @Author  : ZhangJun
# @FileName: userselect.py

import os
import traceback
import simplejson as json
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
        self.SSR = None
        self.SDM = None
        self.TSG = None
        self.TSGLeader = None
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        jsonpath = os.path.abspath(os.path.join(apppath, 'userselect.json'))
        try:
            with open(jsonpath, 'r', encoding="utf-8") as app_file:
                content = app_file.read()
            user_obj = json.loads(content)
            self.SSR = user_obj['SSR']
            self.SDM = user_obj['SDM']
            self.TSG = user_obj['TSG']
            self.TSGLeader = user_obj['TSGLeader']
        except Exception as exp:
            print('Exception at UserSelect.__init__() %s ' % exp)
            traceback.print_exc()


if __name__ == '__main__':
    userselect = UserSelect()
    log.debug(userselect.SSR)
    log.debug(userselect.SDM)
    log.debug(userselect.TSG)
    log.debug(userselect.TSGLeader)

