# SMTP 配置
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.log_util import log

smtp_server_info = {
    "SMTP_PORT": 25,
    "SMTP_SSL_PORT": 465,
    "smtp": {
        'qq': 'smtp.qq.com',
        '163': 'smtp.163.com',
        '126': 'smtp.126.com',
        'google': 'smtp.gmail.com',
        'wecom': 'smtp.exmail.qq.com',
        'aliyun': 'smtp.qiye.aliyun.com',
    }}

# 发送邮件
def send_email(
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        subject,
        body,
        receive_email: str=None,
        is_ssl=False
):

    """
    邮件发送 smtp。

    :param smtp_server: SMTP服务器地址。
    :param smtp_port: SMTP服务器端口号。
    :param smtp_username: SMTP服务器用户名。
    :param smtp_password: SMTP服务器密码。
    :param subject: 邮件主题。
    :param body: 邮件正文。
    :param receive_email: 收件人邮箱地址。默认为None，表示发给自己。
    :param is_ssl: 是否使用SSL加密连接，默认为False。

    :return: 邮件是否发送成功
    """

    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = receive_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))
    print(message)

    server = None
    if is_ssl:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # server.starttls()  # 启用安全传输模式
    else:
        server = smtplib.SMTP(smtp_server, smtp_port)

    try:
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(smtp_username, [smtp_username], text)
        server.quit()
        log.info("邮件发送成功")
    except Exception as e:
        log.exception(e)
        return False
    return True


if __name__ == '__main__':
    from password import qq_email_password

    send_email(
        smtp_server='smtp.qq.com',
        smtp_port=465,
        smtp_username='647983952@qq.com',
        smtp_password=qq_email_password,
        subject="你好",
        body="你好",
        is_ssl=True
    )
