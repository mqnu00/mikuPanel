import json
import os.path
import pathlib


class PathInfo:

    parent: str
    dirname: str
    dirtype: str
    size: int | None = None
    permission: str
    modify_timestamp: int
    owner: str
    group: str

    def __init__(self, path: str):
        p = pathlib.Path(path)
        self.parent = str(p.parent)
        self.dirname = str(p.name)
        self.dirtype = check_path_type(path)
        if self.dirtype == 'file':
            self.size = p.stat().st_size
        self.modify_timestamp = int(p.stat().st_mtime)
        self.owner = p.owner()
        self.group = p.group()
        self.permission = oct(p.stat().st_mode)[-3:]

    def __str__(self):
        return json.dumps(self.__dict__)



def is_path_exist(func):
    def wrapper(*args, **kwargs):
        import inspect
        func_params = inspect.signature(func).parameters
        # 将位置参数转换为关键字参数
        param_names = list(func_params.keys())
        unified_kwargs = {param_names[i]: arg for i, arg in enumerate(args)}

        # 合并原有的关键字参数
        unified_kwargs.update(kwargs)
        path = unified_kwargs.get('path')
        if os.path.exists(path):
            return func(*args, **kwargs)
        else:
            raise Exception(f"path {path} not exist")

    return wrapper


def path_concat(parent, name):
    p = pathlib.Path(parent)
    p = p / name
    return str(p)


@is_path_exist
def check_path_type(path):
    p = pathlib.Path(path)
    if p.is_dir():
        return "dir"
    elif p.is_file():
        return "file"
    else:
        return "others"


@is_path_exist
def get_file_list(path):
    p = pathlib.Path(path)
    if p.is_dir():
        return {
            "nowPath": path,
            "list": [PathInfo(str(p)) for p in p.iterdir()]
        }
    elif p.is_file():
        return get_file_list(str(p.parent))
    else:
        raise Exception(f'{p} not dir')


@is_path_exist
def get_file_content(path):
    p = pathlib.Path(path)
    if p.is_file():
        with open(p) as f:
            content = f.read()
        return content
    else:
        raise Exception(f'{p} not file')


@is_path_exist
def save_file(path, file_content):
    p = pathlib.Path(path)
    with open(p, 'w') as f:
        f.write(file_content)


if __name__ == '__main__':
    print(get_file_list('/home/lzh/.zshrc'))
