import subprocess


def run_command(command, stdin_content: str = None):
    """
    运行命令并传递标准输入
    :param command: 要运行的命令（列表形式）
    :param stdin_content: 关键字参数，其中 'stdin' 用于传递标准输入内容
    """

    # 使用 subprocess.run 运行命令，并传递标准输入
    result = subprocess.run(
        command,
        input=stdin_content,  # 传递标准输入内容
        capture_output=True,  # 捕获标准输出和错误输出
        text=True  # 以文本形式返回输出内容
    )

    # 检查命令是否成功执行
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"命令执行失败，返回码：{result.returncode} \n 脚本执行错误 {result.stderr}")


# 示例：运行一个命令并传递标准输入
if __name__ == "__main__":
    command = ["/home/lzh/program/py-code/mikuPanel/tests/install-docker.sh"]  # 使用 cat 命令作为示例
    stdin_content = "-s docker --mirror Aliyun"
    print(run_command(command))
