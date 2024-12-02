# SMTP 配置
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.log_util import log

smtp_server = 'smtp.163.com'  # SMTP服务器地址
smtp_port = 587  # SMTP端口号，通常是587或465
smtp_username = 'mqnu000@163.com'  # SMTP用户名（通常是邮箱地址）
smtp_password = 'RDebNDs8mMxyWqzE'  # SMTP密码


# 发送邮件
def send_email(
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        subject,
        body,
        receive_email=None,
        is_ssl=False
):
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


if __name__ == '__main__':
    send_email(
        smtp_server='smtp.qq.com',
        smtp_port=456,
        smtp_username='647983952@qq.com',
        smtp_password='wyxnsbbehildbcea',

    )
