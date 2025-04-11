#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/04/11 09:46
# @Author  : ZhangJun
# @FileName: mailtool.py

from utils.log import log as log
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailTool(object):
    _smtp_server = f'smtp.gmail.com'
    _smtp_port = 587
    _sender_email = f'tls.delivery.management.tools@gmail.com'
    _sender_password = f'ciqq wcci pbln ocqs'

    def send_email(self,receiver_email, subject, body):
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = self._sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            # 连接到SMTP服务器
            server = smtplib.SMTP(self._smtp_server, self._smtp_port)
            server.starttls()  # 启用TLS加密
            server.login(self._sender_email, self._sender_password)
            server.send_message(msg)
            server.quit()
            log.debug("邮件发送成功！")
        except Exception as e:
            log.debug(f"邮件发送失败：{e}")

if __name__ == '__main__':
    mailtool = MailTool()
    mailtool.send_email("Jun.Zhang1@ibm.com","crtool测试邮件","这是一封测试邮件，发送自 Python。")