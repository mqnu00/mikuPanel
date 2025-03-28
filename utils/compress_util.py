import os
import tarfile

def compress_folder_to_tar_gz(source_folder, output_file):
    """
    将指定文件夹压缩为 .tar.gz 文件

    :param source_folder: 要压缩的文件夹路径
    :param output_file: 输出的 .tar.gz 文件路径
    """
    # 确保输出文件的路径是有效的
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 创建 tar.gz 文件
    with tarfile.open(output_file, "w:gz") as tar:
        # 遍历文件夹并添加到 tar 归档中
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算相对路径
                relative_path = os.path.relpath(file_path, start=source_folder)
                tar.add(file_path, arcname=relative_path)

    # print(f"文件夹 '{source_folder}' 已成功压缩为 '{output_file}'")


def extract_tar_gz(tar_gz_file, target_dir):
    """
    解压 tar.gz 文件到指定目录
    :param tar_gz_file: tar.gz 文件的路径
    :param target_dir: 解压目标目录
    """
    try:
        # 打开 tar.gz 文件
        with tarfile.open(tar_gz_file, "r:gz") as tar:
            # 解压到指定目录
            tar.extractall(path=target_dir)
            print(f"文件已成功解压到 {target_dir}")
    except FileNotFoundError:
        print(f"文件 {tar_gz_file} 不存在")
    except tarfile.TarError as e:
        print(f"解压文件时出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == '__main__':

    # 示例用法
    source_folder = "/home/lzh/program/py-code/mikuPanel/plugins/dockerManager"  # 替换为你的文件夹路径
    output_file = "/home/lzh/program/py-code/mikuPanel//plugins/dockerManager.tar.gz"  # 替换为输出的 tar.gz 文件路径
    # compress_folder_to_tar_gz(source_folder, output_file)
    extract_tar_gz(output_file, source_folder)