import base64
import logging
import poplib
import pprint

import email
import smtplib
import imaplib
import sys
import time
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from utils.log_util import log

# from email_utils.read import get_email_header, get_email_content

import email
import pprint
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage


# 假设你已经有了一个电子邮件的原始内容，这里我们用一个字符串来模拟
# 通常这个内容会从文件、数据库或者网络请求中获取
# with open(r"C:\Users\mqnu00\Downloads\IXBJZKYA-0315.eml", "rb") as f:
# with open(r"D:\program\python\code\test\email\check.eml", "rb") as f:
#     raw_email = f.read()

def get_email_header(raw_email):
    # 使用BytesParser解析原始邮件内容
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)

    # pprint.pprint(msg.__dict__)

    # 获取邮件的头部信息
    from_ = msg['From']
    to_ = msg['To']
    subject = msg['Subject']
    date_header = msg['Date']

    return from_, to_, subject, date_header


def get_email_content(raw_email):
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)
    # 检查邮件是否包含多部分内容
    if msg.is_multipart():
        # 遍历邮件的每一部分
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            # 检查内容类型是否为文本
            if part.get_content_type() == 'text/plain':
                # 获取邮件正文
                email_body = part.get_payload(decode=True).decode(part.get_content_charset())
                print("Email Body:")
                print(email_body)
            if part.get('Content-Disposition') is None:
                continue
            # 检查是否是附件
            if 'attachment' in part.get('Content-Disposition'):
                # 获取附件的文件名
                filename = part.get_filename()
                if not filename:
                    continue
                # 获取附件的内容
                attachment_content = part.get_payload(decode=True)
                # 保存附件到文件
                with open(filename, 'wb') as f:
                    f.write(attachment_content)
                print(f"Attachment {filename} saved.")
    else:
        # 如果邮件不是多部分内容，直接打印邮件正文
        payload = msg.get_payload(decode=True)
        email_body = payload.decode(msg.get_content_charset())
        print("Email Body:")
        print(email_body)


# SMTP 配置
# smtp_server = 'smtp.163.com'  # SMTP服务器地址
# smtp_port = 587  # SMTP端口号，通常是587或465
# smtp_username = 'mqnu000@163.com'  # SMTP用户名（通常是邮箱地址）
# smtp_password = 'RDebNDs8mMxyWqzE'  # SMTP密码


# # IMAP 配置
# imap_server = 'imap.163.com'  # IMAP服务器地址
# imap_port = 993  # IMAP端口号，通常是993
# imap_username = 'mqnu000@163.com'  # IMAP用户名（通常是邮箱地址）
# imap_password = 'RDebNDs8mMxyWqzE'  # IMAP密码


# 发送邮件
def send_email(
        smtp_server,
        smtp_port,
        smtp_username,
        smtp_password,
        subject,
        body):

    try:

        message = MIMEMultipart()
        message['From'] = smtp_username
        message['To'] = smtp_username
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # server.starttls()  # 启用安全传输模式
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(smtp_username, [smtp_username], text)
        server.quit()
    except Exception as e:

        log.exception('邮件发送失败')


# 接收邮件
def receive_email_imap(
        imap_server,
        imap_port: int,
        imap_username,
        imap_password,
        is_ssl: bool,
        box: str,
        search_query: str,
        encode: str = None):
    msg = []
    if is_ssl:
        server = imaplib.IMAP4_SSL(imap_server, imap_port)
        server.login(imap_username, imap_password)
    else:
        server = imaplib.IMAP4(imap_server, imap_port)
        server.login(imap_username, imap_password)
    imap_id = ("name", "1", "version", "2", "vendor", "3")
    typ, data = server.xatom('ID', '("' + '" "'.join(imap_id) + '")')

    server.select(box)  # 选择收件箱
    # 构建搜索查询
    # 日期
    # SINCE "11-Nov-2024" 表示从2024年11月11日之后
    # BEFORE "13-Nov-2024" 表示在2024年11月13日之前
    # search_query = '(SINCE "11-Nov-2024" BEFORE "13-Nov-2024")'
    # 收发件人 不支持
    # search_query = '(FROM "mqnu000@163.com")'
    # 主题包含 不支持
    # search_query = '(SUBJECT "更安全、更高效、更强大，尽在QQ邮箱APP")'
    # search_query = '(SUBJECT "明明就")'
    # 正文包含 不支持
    # search_query = '(BODY "12345678910")'
    # 全部
    # search_query = '(ALL)'
    # 已读
    # search_query = '(SEEN)'
    # search_query = '( AND SUBJECT "蓝桥杯"  BODY "得塔")'

    print(search_query)

    # 执行搜索
    if encode:
        status, messages = server.search(encode, search_query.encode(encode))
    else:
        status, messages = server.search(None, search_query)
    if status == 'OK':
        # messages[0] 包含邮件ID列表
        print(messages[0])
        for num in reversed(messages[0].split()):
            status, msg_data = server.fetch(num, '(RFC822)')
            if status == 'OK':
                # 处理邮件内容
                # 例如，解析邮件、打印邮件主题等
                msg = get_email_header(msg_data[0][1])
                logging.info(msg)
                # return None
                # msg.append(msg_data[0][1])
    else:
        print('No messages found.')

    # 关闭连接
    server.close()
    server.logout()
    return msg


import datetime


def search_query_generator(
        before=None,
        since=None,
        subject=None,
        body: str = None,
        from_addr=None,
        to_addr=None,
        seen: bool = None
):
    """
    生成 IMAP 搜索查询字符串。
    默认返回所有邮件

    :param before: 字符串或 datetime.date，邮件接收日期之前的邮件。
    :param since: 字符串或 datetime.date，邮件接收日期之后的邮件。
    :param subject: 包含特定关键词的邮件主题。
    :param body: 包含特定关键词的邮件正文。
    :param from_addr: 发件人地址。
    :param to_addr: 收件人地址。
    :param seen: 是否已读，None表示所有邮件。
    :return: 格式化的 IMAP 搜索查询字符串。
    """
    query_parts = []

    # 将日期转换为 IMAP 需要的格式
    if isinstance(before, datetime.date):
        before = before.strftime("%d-%b-%Y")
    if isinstance(since, datetime.date):
        since = since.strftime("%d-%b-%Y")
    print(before, since)

    # 添加日期条件
    if before:
        query_parts.append(f'BEFORE "{before}"')
    if since:
        query_parts.append(f'SINCE "{since}"')

    # 添加主题条件
    if subject:
        query_parts.append(f'SUBJECT "{subject}"')

    if body:
        query_parts.append(f'BODY "{body}"')

    # 添加发件人条件
    if from_addr:
        query_parts.append(f'FROM "{from_addr}"')

    # 添加收件人条件
    if to_addr:
        query_parts.append(f'TO "{to_addr}"')

    # 添加是否已读
    if seen is not None:
        if seen:
            query_parts.append(f'SEEN')
        else:
            query_parts.append(f'UNSEEN')

    # 组合所有条件
    if query_parts:
        return '({})'.format(' '.join(query_parts))
    else:
        return '(ALL)'  # 默认返回所有邮件


def receive_email_pop3(
        host,
        port,
        is_ssl: bool,
        username,
        password,

):
    pop_server = poplib.POP3_SSL(host=host, port=port, timeout=10) if is_ssl else poplib.POP3(host=host, port=port,
                                                                                              timeout=10)
    try:
        pop_server.user(username)
    except Exception:
        raise Exception("邮箱账户不存在")
    try:
        pop_server.pass_(password)
    except Exception:
        traceback.print_exc()
        return

    resp, mails, octets = pop_server.list()
    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    i = 0
    while i < 10:
        resp, lines, octets = pop_server.retr(index)

        # lines存储了邮件的原始文本的每一行,
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        # 稍后解析出邮件:
        msg = Parser().parsestr(msg_content)
        # print(msg)
        print(msg.get('From'))
        print(msg.get('To'))
        i = i + 1
        index = index - 1


if __name__ == '__main__':
    # 示例使用

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | Line %(lineno)d | %(message)s |'
    )

    search_query = search_query_generator(
        # since=datetime.date(2024, 11, 20),
        # before=datetime.date(2024, 11, 21),
        # since=None,
        # before=None,
        # subject="123",
        # body='456',
        # from_addr="mqnu000@163.com",
        # to_addr="mqnu000@gmail.com",
        # seen=False,
        # seen=True
    )

    print(search_query)

    # msg = receive_email_imap(
    #     imap_server='imap.qq.com',  # IMAP服务器地址
    #     imap_port=993,  # IMAP端口号，通常是993
    #     imap_username='647983952@qq.com',  # IMAP用户名（通常是邮箱地址）
    #     imap_password='wyxnsbbehildbcea',  # IMAP密码
    #     is_ssl=True,
    #     box='inbox',
    #     # box='sent',
    #     search_query=search_query,
    #     encode='utf-8'
    # )

    # msg = receive_email_imap(
    #     imap_server='imap.163.com',  # IMAP服务器地址
    #     imap_port=143,  # IMAP端口号，通常是993
    #     imap_username='mqnu000@163.com',  # IMAP用户名（通常是邮箱地址）
    #     imap_password='RDebNDs8mMxyWqzE',  # IMAP密码
    #     is_ssl=False,
    #     box='inbox',
    #     search_query=search_query,
    #     encode='utf-8'
    # )

    # msg = receive_email_imap(
    #     imap_server='imap.126.com',
    #     imap_port=993,
    #     imap_username='mqnu000@126.com',
    #     imap_password='SPR4gLffrpa99ZZq',
    #     is_ssl=True,
    #     box='inbox',
    #     search_query=search_query,
    #     encode='utf-8'
    # )

    # msg = receive_email_imap(
    #     imap_server='imap.gmail.com',
    #     imap_port=143,
    #     imap_username='mqnu000@gmail.com',
    #     imap_password='uavplamyucugjkbg',
    #     is_ssl=False,
    #     box='inbox',
    #     search_query=search_query,
    #     encode='utf8'
    # )
    #
    # msg = receive_email_imap(
    #     imap_server='imap.qiye.aliyun.com',
    #     imap_port=993,
    #     imap_username='heixiaosun@i-i.ai',
    #     imap_password='FT4nNIM46GhMCE5S',
    #     is_ssl=True,
    #     box='inbox',
    #     search_query=search_query,
    #     # encode='utf-8'
    # )

    # msg = receive_email_imap(
    #     imap_server='imap.qiye.aliyun.com',
    #     imap_port=993,
    #     imap_username='leize@i-i.ai',
    #     imap_password='5nk2BsBCVx3n6Do0',
    #     is_ssl=True,
    #     box='inbox',
    #     search_query=search_query,
    #     # encode='utf-8'
    # )

    # msg = receive_email_imap(
    #     imap_server='imap.aliyun.com',
    #     imap_port=143,
    #     imap_username='mqnu000@aliyun.com',
    #     imap_password='112233lzh.lzh',
    #     is_ssl=False,
    #     box='inbox',
    #     search_query=search_query,
    #     # encode='utf-8'
    # )

    # for i in msg:
    #
    #     logging.info(get_email_header(i))
    #     print('', flush=True)

    # print(get_email_content(i))

    # receive_email_pop3(
    #     host='pop.qiye.aliyun.com',
    #     port=995,
    #     is_ssl=True,
    #     username='leize@i-i.ai',
    #     password='5nk2BsBCVx3n6Do0'
    # )

    # receive_email_imap(
    #         imap_server='imap.hwmail.com.cn',
    #         imap_port=993,
    #         imap_username='rpa@snwj.com',
    #         imap_password='c253ajIwMTlAeHh6eCA=',
    #         is_ssl=True,
    #         box='inbox',
    #         search_query=search_query,
    #         # encode='utf-8'
    # )

    # receive_email_pop3(
    #     host='pop.hwmail.com.cn',
    #     port=995,
    #     is_ssl=True,
    #     username='rpa@snwj.com',
    #     password='c253ajIwMTlAeHh6eCA='
    # )

    receive_email_imap(
        imap_server='imap.sparkspace.huaweicloud.com',
        imap_port=993,
        imap_username='mqnu111@mqnu.fun',
        imap_password='atB3qrgzHY6WzEQu',
        is_ssl=True,
        box='inbox',
        search_query=search_query,
        # encode='utf-8'
    )
