#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import traceback

# @Time    : 2025/03/04 10:49
# @Author  : ZhangJun
# @FileName: apis.py

from fastapi import APIRouter
from fastapi_amis_admin.globals.deps import SyncSess, AsyncSess
from sqlalchemy import text

from core.globals import site

from utils.log import log as log

router = APIRouter()


@router.get('/hello')
async def hello(name: str = '') -> str:
    return f'hello {name}'


@router.get("/test_sync_db", summary="测试同步数据库操作")
def test_sync_db(sess: SyncSess):
    # obj=sess.get(...)
    # do something
    pass

@router.get("/crtool/get_sdm_list", summary="从数据库获取已输入的SDM姓名")
async def get_sdm_list(sess: SyncSess):
    # obj=sess.get(...)
    # do something
    sdm_list = []
    try:
        result = await site.engine.execute(text("SELECT DISTINCT local_sdm FROM changerequest"))
        rows = result.fetchall()
        result_list = [dict(row._asdict())['local_sdm'] for row in rows]
        sdm_list = [{"label": name, "value": name} for name in result_list]
    except Exception as e:
        log.error('SQL query Error !')
        traceback.print_exc()
    return sdm_list


@router.get("/test_async_db", summary="测试异步数据库操作")
async def test_async_db(sess: AsyncSess):
    # obj=await sess.get(...)
    # do something
    pass

# from fastapi_user_authuser_auth.globals.deps import CurrentUser
#
# @router.get("/get_user", summary="获取当前登录用户")
# async def get_user(user: CurrentUser):
#     return user