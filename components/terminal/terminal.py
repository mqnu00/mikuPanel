import json
from utils.log_util import log
import paramiko


class SSHInfo(object):

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.port = port
        self.username = username
        self.password = password


class Terminal(object):

    def __init__(self, ssh_info: SSHInfo):
        self.client = paramiko.SSHClient()
        self.ssh_info = ssh_info

    def connect_to_terminal(self, timeout=5 * 60):
        # 自动添加策略，保存服务器的主机名和密钥信息
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接SSH服务端，以用户名和密码进行认证
        self.client.connect(hostname=self.ssh_info.host, port=self.ssh_info.port, username=self.ssh_info.username,
                            password=self.ssh_info.password)
        self.chan = self.client.invoke_shell('xterm')
        self.chan.settimeout(timeout)

    def send_to_terminal(self, msg):
        if self.chan.closed:
            return False
        else:
            recv_info: dict = json.loads(msg)
            recv_type = recv_info.get('type')
            if recv_type == 'resize':
                self.chan.resize_pty(width=recv_info.get("cols"), height=recv_info.get("rows"))
            elif recv_type == 'cmd':
                self.chan.send(recv_info.get('msg').encode('utf8'))
            if self.chan.closed:
                return False
            return True

    def recv_from_terminal(self):
        if self.chan.closed:
            return False
        else:
            msg = self.chan.recv(4096)
            return msg.decode('utf8')

    def close(self):
        self.chan.close()
        self.client.close()

