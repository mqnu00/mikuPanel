import importlib
import os
import py_compile
import glob
import shutil


def compile_and_rename_python_files(directory, target_directory):
    # 确保目标目录存在
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # 遍历目录中的所有 .py 文件
    for py_file in glob.glob(os.path.join(directory, '*.py')):
        # 编译 Python 文件
        compiled_file_path = py_compile.compile(py_file)

        # 移除版本标签，构造新的文件名
        new_compiled_file_path = os.path.join(target_directory,
                                              os.path.basename(compiled_file_path).split('.', 2)[0] + '.pyc')

        # 移动编译后的文件到目标目录，并重命名
        shutil.move(compiled_file_path, new_compiled_file_path)
        print(f"Compiled and moved {compiled_file_path} to {new_compiled_file_path}")




# 使用示例
if __name__ == "__main__":
    # source_directory = '/home/lzh/program/py-code/mikuPanel/components/dockerManager'
    # target_directory = '/home/lzh/program/py-code/mikuPanel/plugins/dockerManager'
    # compile_and_rename_python_files(source_directory, target_directory)
    pyc_file_path = "/home/lzh/program/py-code/mikuPanel/plugins/dockerManager/dockerManager"

    # from plugins.dockerManager import dockerManager
    #
    # print(dockerManager.DockerManager.check_docker())

    dod = importlib.import_module("plugins.dockerManager.dockerManager")
    print(dod.DockerManager.check_docker())