#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:15
# @Author  : ZhangJun
# @FileName: globals.py

from sqlalchemy_database import AsyncDatabase, Database
from fastapi_user_auth.admin import AuthAdminSite
from fastapi_user_auth.auth import Auth
from fastapi_user_auth.auth.backends.jwt import JwtTokenStore

from core.settings import settings
from utils.log import log as log
from core import i18n as _

# 创建异步数据库引擎
async_db = AsyncDatabase.create(
    url=settings.database_url_async,
    session_options={
        "expire_on_commit": False,
    },
)
# 创建同步数据库引擎
sync_db = Database.create(
    url=settings.database_url,
    session_options={
        "expire_on_commit": False,
    },
)

auth = Auth(db=async_db, token_store=JwtTokenStore(secret_key=settings.secret_key))
site = AuthAdminSite(settings, engine=async_db, auth=auth)
auth = site.auth
site.UserAuthApp.page_schema.sort = -99


