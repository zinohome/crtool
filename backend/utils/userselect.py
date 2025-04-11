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
        self.ssr_dict = None
        self.SDM = None
        self.sdm_dict = None
        self.TSG = None
        self.tsg_dict = None
        self.TSGLeader = None
        self.leader_dict = None
        self.leader_emails_str = None
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        jsonpath = os.path.abspath(os.path.join(apppath, 'userselect.json'))
        try:
            with open(jsonpath, 'r', encoding="utf-8") as app_file:
                content = app_file.read()
            user_obj = json.loads(content)
            self.SSR = user_obj['SSR']
            self.ssr_dict = {ssr["id"]: ssr for ssr in self.SSR}
            self.SDM = user_obj['SDM']
            self.sdm_dict = {sdm["id"]: sdm for sdm in self.SDM}
            self.TSG = user_obj['TSG']
            self.tsg_dict = {tsg["id"]: tsg for tsg in self.TSG}
            self.TSGLeader = user_obj['TSGLeader']
            self.leader_dict = {leader["id"]: leader for leader in self.TSGLeader}
            self.leader_emails_str = ", ".join([leader["email"] for leader in self.TSGLeader])
        except Exception as exp:
            print('Exception at UserSelect.__init__() %s ' % exp)
            traceback.print_exc()

    def find_tsg_email_by_id(self, target_id):
        leader_info = self.tsg_dict.get(target_id)
        if leader_info:
            return leader_info["email"]
        else:
            return "yangq@cn.ibm.com"

if __name__ == '__main__':
    userselect = UserSelect()
    log.debug(userselect.SSR)
    log.debug(userselect.SDM)
    log.debug(userselect.TSG)
    log.debug(userselect.TSGLeader)
    log.debug(userselect.ssr_dict)
    log.debug(userselect.sdm_dict)
    log.debug(userselect.tsg_dict)
    log.debug(userselect.leader_dict)
    log.debug(userselect.leader_emails_str)
    log.debug(userselect.find_tsg_email_by_id('duxincun@cn.ibm.com'))

