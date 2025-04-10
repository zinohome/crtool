#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2023 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2023
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi._compat import ModelField
from fastapi_amis_admin.admin import AdminAction
from fastapi_amis_admin.crud import CrudEnum
from fastapi_amis_admin.crud.base import SchemaFilterT, SchemaUpdateT
from fastapi_amis_admin.crud.parser import TableModelParser
from fastapi_amis_admin.utils.pydantic import model_fields
from fastapi_user_auth.auth.models import User
from fastapi_user_auth.globals import auth
from pydantic._internal._decorators import mro
from sqlalchemy import Select, or_, and_, desc

from apps.admin.swiftadmin import SwiftAdmin
from core.globals import site
from typing import List, Optional, TYPE_CHECKING, Union, Dict, Any
from fastapi_amis_admin import admin, amis
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider
from starlette.requests import Request
import simplejson as json
from fastapi_amis_admin.utils.translation import i18n as _
from utils.log import log as log
from apps.admin.models.changerequest import Changerequest


class ChangerequestAdmin(SwiftAdmin):
    group_schema = "Changerequest"
    page_schema = PageSchema(label='ChangeRequest', page_title='ChangeRequest', icon='fa fa-server', sort=96)
    model = Changerequest
    pk_name = 'id'
    list_per_page = 20
    list_display = []
    search_fields = []
    parent_class = None
    tabsMode = TabsModeEnum.card
    admin_action_maker = [
        lambda self: AdminAction(
            admin=self,
            name="copy",
            tooltip="复制",
            flags=["item"],
            getter=lambda request: self.get_duplicate_action(request, bulk=False),
        ),
        lambda self: AdminAction(
            admin=self,
            name="review",
            tooltip="审批",
            flags=["item"],
            getter=lambda request: self.get_review_action(request, bulk=False),
        )
    ]
    createactions = [
        {
            "type": "button",
            "actionType": "cancel",
            "icon": "fa fa-reply",
            "label": "取消",
            "primary": False
        },
        {
            "type": "button",
            "icon": "fa fa-file",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Draft",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "暂存",
            "primary": True
        },
        {
            "type": "button",
            "icon": "fa fa-arrow-up",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Submitted",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "提交",
            "primary": False
        }
    ]

    readactions = [
        {
            "type": "button",
            "actionType": "cancel",
            "icon": "fa fa-reply",
            "label": "取消",
            "primary": False
        }
    ]

    reviewactions = [
        {
            "type": "button",
            "actionType": "cancel",
            "icon": "fa fa-reply",
            "label": "取消",
            "primary": False
        },
        {
            "type": "button",
            "icon": "fa fa-arrow-right",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Approved",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "审批",
            "primary": True
        },
        {
            "type": "button",
            "icon": "fa fa-arrow-left",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Returned",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "驳回",
            "primary": False
        },
        {
            "type": "button",
            "icon": "fa fa-stop-circle",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Completed",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "完成",
            "primary": False
        }
    ]

    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        # 启用批量新增
        self.enable_bulk_create = False
        # 启用查看
        self.schema_read = None
        # 设置form弹出类型  Drawer | Dialog
        self.action_type = 'Drawer'
    async def get_select(self, request: Request) -> Select:
        #user = await auth.get_current_user(request)
        #log.debug(user)
        #log.debug(request.user)
        stmt = await super().get_select(request)
        return stmt.order_by(desc(Changerequest.update_time))
    async def get_create_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        if not bulk:
            if self.action_type == 'Drawer':
                return ActionType.Drawer(
                    icon="fa fa-plus pull-left",
                    label=_("Create"),
                    level=LevelEnum.primary,
                    drawer=Drawer(
                        title=_("Create") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_create_form(request, bulk=bulk),
                    ),
                )
            else:
                return ActionType.Dialog(
                    icon="fa fa-plus pull-left",
                    label=_("Create"),
                    level=LevelEnum.primary,
                    dialog=Dialog(
                        title=_("Create") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_create_form(request, bulk=bulk),
                    ),
                )
        if self.action_type == 'Drawer':
            return ActionType.Dialog(
                icon="fa fa-plus pull-left",
                label=_("Bulk Create"),
                level=LevelEnum.primary,
                dialog=Dialog(
                    title=_("Bulk Create") + " - " + _(self.page_schema.label),
                    id="form_setvalue",
                    position="right",
                    showCloseButton=False,
                    actions=self.createactions,
                    overlay=False,
                    closeOnOutside=True,
                    size=SizeEnum.full,
                    resizable=True,
                    width="900px",
                    body=await self.get_create_form(request, bulk=bulk),
                ),
            )
        else:
            return ActionType.Dialog(
                icon="fa fa-plus pull-left",
                label=_("Bulk Create"),
                level=LevelEnum.primary,
                dialog=Dialog(
                    title=_("Bulk Create") + " - " + _(self.page_schema.label),
                    id="form_setvalue",
                    position="right",
                    showCloseButton=False,
                    actions=self.createactions,
                    overlay=False,
                    closeOnOutside=True,
                    size=SizeEnum.full,
                    resizable=True,
                    width="900px",
                    body=await self.get_create_form(request, bulk=bulk),
                ),
            )

    async def get_read_action(self, request: Request) -> Optional[Action]:
        if not self.schema_read:
            return None
        if self.action_type == 'Drawer':
            return ActionType.Drawer(
                icon="fas fa-eye",
                tooltip=_("View"),
                drawer=Drawer(
                    title=_("View") + " - " + _(self.page_schema.label),
                    position="right",
                    showCloseButton=False,
                    actions=self.readactions,
                    overlay=False,
                    closeOnOutside=True,
                    size=SizeEnum.lg,
                    resizable=True,
                    width="900px",
                    body=await self.get_read_form(request),
                ),
            )
        else:
            return ActionType.Dialog(
                icon="fas fa-eye",
                tooltip=_("View"),
                dialog=Dialog(
                    title=_("View") + " - " + _(self.page_schema.label),
                    position="right",
                    showCloseButton=False,
                    actions=self.readactions,
                    overlay=False,
                    closeOnOutside=True,
                    size=SizeEnum.lg,
                    resizable=True,
                    width="900px",
                    body=await self.get_read_form(request),
                ),
            )

    async def get_update_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        if not bulk:
            if self.action_type == 'Drawer':
                return ActionType.Drawer(
                    icon="fa fa-pencil",
                    tooltip=_("Update"),
                    drawer=Drawer(
                        title=_("Update") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_update_form(request, bulk=bulk),
                    ),
                )
            else:
                return ActionType.Dialog(
                    icon="fa fa-pencil",
                    tooltip=_("Update"),
                    dialog=Dialog(
                        title=_("Update") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_update_form(request, bulk=bulk),
                    ),
                )
        elif self.bulk_update_fields:
            if self.action_type == 'Drawer':
                return ActionType.Dialog(
                    label=_("Bulk Update"),
                    dialog=Dialog(
                        title=_("Bulk Update") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_update_form(request, bulk=True),
                    ),
                )
            else:
                return ActionType.Dialog(
                    label=_("Bulk Update"),
                    dialog=Dialog(
                        title=_("Bulk Update") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_update_form(request, bulk=True),
                    ),
                )
        else:
            return None

    async def get_print_action(self, request: Request) -> Optional[Action]:
        if not self.schema_read:
            return None
        actiontype = ActionType.Dialog(
            icon="fas fa-print",
            tooltip=_("Print"),
            dialog=Dialog(
                title=_(self.page_schema.label),
                size=SizeEnum.lg,
                showCloseButton=False,
                actions=[
                    {
                        "type": "button",
                        "actionType": "cancel",
                        "label": "取消",
                        "Style": {
                            ".noprint": {
                                "display": "none"
                            }
                        },
                        "primary": False
                    },
                    {
                        "type": "button",
                        "label": "打印",
                        "onEvent": {
                            "click": {
                                "actions": [
                                    {
                                        "actionType": "custom",
                                        "ignoreError": False,
                                        "script": "doAction(window.print());"
                                    }
                                ]
                            }
                        },
                        "wrapperCustomStyle": {
                            ".noprint": {
                                "display": "none"
                            }
                        },
                        "primary": True
                    }
                ],
                body=await self.get_print_form(request),
            ),
        )
        return actiontype

    async def get_print_form(self, request: Request) -> Form:
        p_form = await super().get_read_form(request)
        return p_form

    async def get_read_form(self, request: Request) -> Form:
        r_form = await super().get_read_form(request)
        # 构建主表Read
        formtab = amis.Tabs(tabsMode='card')
        formtab.tabs = []
        fieldlist = []
        for item in r_form.body:
            if item.name != self.pk_name:
                fieldlist.append(item)
        fld_dict = {item.name: item for item in fieldlist}
        customer_fld_lst = []
        customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
        customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
        customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
        customer_fld_lst.append(Divider())
        customer_fld_lst.append(
            Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
        customer_fld_lst.append(Divider())
        customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
        basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
        ssr_fld_lst = []
        ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
        ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
        ssr_fld_lst.append(Divider())
        ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
        proj_fld_lst = []
        proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
        proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
        proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
        proj_fld_lst.append(Divider())
        projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
        cr_fld_lst = []
        cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
        cr_fld_lst.append(Group(body=[fld_dict["end_date"], fld_dict["begin_date"]]))
        proj_fld_lst.append(Divider())
        cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
        cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
        cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
        cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
        cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
        cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
        cr_fld_lst.append(Divider())
        cr_fld_lst.append(Group(body=[fld_dict["category"]]))
        cr_fld_lst.append(Divider())
        cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
        crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
        review_fld_lst = []
        review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
        review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
        review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
        review_fld_lst.append(Divider())
        reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
        formtab.tabs.append(basictabitem)
        formtab.tabs.append(ssrtabitem)
        formtab.tabs.append(projtabitem)
        formtab.tabs.append(crtabitem)
        formtab.tabs.append(reviewtabitem)
        r_form.body = formtab
        return r_form

    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
        c_form = await super().get_create_form(request, bulk)
        c_form.preventEnterSubmit=True
        user = await auth.get_current_user(request)
        if not bulk:
            # 构建主表Create
            formtab = amis.Tabs(tabsMode='card')
            formtab.tabs = []
            fieldlist = []
            for item in c_form.body:
                fieldlist.append(item)
            fld_dict = {item.name: item for item in fieldlist}
            customer_fld_lst = []
            customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(
                Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
            basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
            ssr_fld_lst = []
            fld_dict["ssr"].value = user.username
            ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
            ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
            ssr_fld_lst.append(Divider())
            ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
            proj_fld_lst = []
            proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
            proj_fld_lst.append(Divider())
            projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
            cr_fld_lst = []
            fld_dict["onsite_engineer"].value = user.username
            cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
            cr_fld_lst.append(Group(body=[fld_dict["end_date"], fld_dict["begin_date"]]))
            proj_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["category"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
            crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
            review_fld_lst = []
            review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
            review_fld_lst.append(Divider())
            reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
            formtab.tabs.append(basictabitem)
            formtab.tabs.append(ssrtabitem)
            formtab.tabs.append(projtabitem)
            formtab.tabs.append(crtabitem)
            formtab.tabs.append(reviewtabitem)
            c_form.body = formtab
        return c_form

    async def get_update_form(self, request: Request, bulk: bool = False) -> Form:
        u_form = await super().get_update_form(request, bulk)
        u_form.preventEnterSubmit = True
        if not bulk:
            # 构建主表Update
            formtab = amis.Tabs(tabsMode='card')
            formtab.tabs = []
            fieldlist = []
            for item in u_form.body:
                fieldlist.append(item)
            fld_dict = {item.name: item for item in fieldlist}
            customer_fld_lst = []
            customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(
                Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
            basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
            ssr_fld_lst = []
            ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
            ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
            ssr_fld_lst.append(Divider())
            ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
            proj_fld_lst = []
            proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
            proj_fld_lst.append(Divider())
            projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
            cr_fld_lst = []
            cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
            cr_fld_lst.append(Group(body=[fld_dict["end_date"], fld_dict["begin_date"]]))
            proj_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["category"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
            crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
            review_fld_lst = []
            review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
            review_fld_lst.append(Divider())
            reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
            formtab.tabs.append(basictabitem)
            formtab.tabs.append(ssrtabitem)
            formtab.tabs.append(projtabitem)
            formtab.tabs.append(crtabitem)
            formtab.tabs.append(reviewtabitem)
            u_form.body = formtab
        return u_form

    async def get_duplicate_form_inner(self, request: Request, bulk: bool = False) -> Form:
        extra = {}
        if not bulk:
            api = f"post:{self.router_path}/item"
            fields = model_fields(self.schema_model).values()
            # fields = model_fields(BaseCrud._create_schema_update()).values()
            if self.schema_read:
                extra["initApi"] = f"get:{self.router_path}/item/${self.pk_name}"
        d_form = Form(
            api=api,
            name="create",
            body=await self._conv_modelfields_to_formitems(request, fields, CrudEnum.create),
            **extra,
        )
        if not bulk:
            # 构建主表Create
            formtab = amis.Tabs(tabsMode='card')
            formtab.tabs = []
            fieldlist = []
            for item in d_form.body:
                fieldlist.append(item)
            fld_dict = {item.name: item for item in fieldlist}
            customer_fld_lst = []
            customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(
                Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
            basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
            ssr_fld_lst = []
            ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
            ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
            ssr_fld_lst.append(Divider())
            ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
            proj_fld_lst = []
            proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
            proj_fld_lst.append(Divider())
            projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
            cr_fld_lst = []
            cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
            cr_fld_lst.append(Group(body=[fld_dict["end_date"], fld_dict["begin_date"]]))
            proj_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["category"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
            crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
            review_fld_lst = []
            review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
            review_fld_lst.append(Divider())
            reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
            formtab.tabs.append(basictabitem)
            formtab.tabs.append(ssrtabitem)
            formtab.tabs.append(projtabitem)
            formtab.tabs.append(crtabitem)
            formtab.tabs.append(reviewtabitem)
            d_form.body = formtab
        return d_form

    async def get_duplicate_form(self, request: Request, bulk: bool = False) -> Form:
        d_form = await self.get_duplicate_form_inner(request, bulk)
        d_form.preventEnterSubmit = True
        return d_form

    async def get_duplicate_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        if not bulk:
            if self.action_type == 'Drawer':
                return ActionType.Drawer(
                    icon="fa fa-copy",
                    tooltip=_("复制"),
                    drawer=Drawer(
                        title=_("复制") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_duplicate_form(request, bulk=bulk),
                    ),
                )
            else:
                return ActionType.Dialog(
                    icon="fa fa-copy",
                    tooltip=_("复制"),
                    dialog=Dialog(
                        title=_("复制") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_duplicate_form(request, bulk=bulk),
                    ),
                )
        else:
            return None

    async def get_review_form(self, request: Request, bulk: bool = False) -> Form:
        r_form = await super().get_update_form(request, bulk)
        r_form.preventEnterSubmit = True
        if not bulk:
            # 构建主表Update
            formtab = amis.Tabs(tabsMode='card')
            formtab.tabs = []
            fieldlist = []
            for item in r_form.body:
                if item.name not in ["tsg_onsite", "tsg_comments"]:
                    item.disabled = True
                fieldlist.append(item)
            fld_dict = {item.name: item for item in fieldlist}
            customer_fld_lst = []
            customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(
                Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
            basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
            ssr_fld_lst = []
            ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
            ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
            ssr_fld_lst.append(Divider())
            ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
            proj_fld_lst = []
            proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
            proj_fld_lst.append(Divider())
            projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
            cr_fld_lst = []
            cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
            cr_fld_lst.append(Group(body=[fld_dict["end_date"], fld_dict["begin_date"]]))
            proj_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["category"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
            crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
            review_fld_lst = []
            review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
            review_fld_lst.append(Divider())
            reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
            formtab.tabs.append(basictabitem)
            formtab.tabs.append(ssrtabitem)
            formtab.tabs.append(projtabitem)
            formtab.tabs.append(crtabitem)
            formtab.tabs.append(reviewtabitem)
            r_form.body = formtab
        return r_form

    async def get_review_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        if not bulk:
            if self.action_type == 'Drawer':
                return ActionType.Drawer(
                    icon="fa fa-share-alt",
                    tooltip=_("审批"),
                    drawer=Drawer(
                        title=_("Review") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.reviewactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_review_form(request, bulk=bulk),
                    ),
                )
            else:
                return ActionType.Dialog(
                    icon="fa fa-share-alt",
                    tooltip=_("审批"),
                    dialog=Dialog(
                        title=_("Review") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.reviewactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_review_form(request, bulk=bulk),
                    ),
                )
        elif self.bulk_update_fields:
            if self.action_type == 'Drawer':
                return ActionType.Dialog(
                    label=_("Bulk Review"),
                    dialog=Dialog(
                        title=_("Bulk Review") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.reviewactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_review_form(request, bulk=True),
                    ),
                )
            else:
                return ActionType.Dialog(
                    label=_("Bulk Review"),
                    dialog=Dialog(
                        title=_("Bulk Review") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.reviewactions,
                        overlay=False,
                        closeOnOutside=True,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_review_form(request, bulk=True),
                    ),
                )
        else:
            return None
    async def on_create_pre(
            self,
            request: Request,
            obj: SchemaUpdateT,
            item_id: Union[List[str], List[int]],
            **kwargs,
    ) -> Dict[str, Any]:
        data = await super().on_update_pre(request, obj, item_id)
        data['create_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data

    async def on_update_pre(
            self,
            request: Request,
            obj: SchemaUpdateT,
            item_id: Union[List[str], List[int]],
            **kwargs,
    ) -> Dict[str, Any]:
        data = await super().on_update_pre(request, obj, item_id)
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data