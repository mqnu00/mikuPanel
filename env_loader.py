import pathlib
import pprint

from dotenv import load_dotenv
import os


def load_environment_variables():
    # 根据环境变量或手动设置来决定加载哪个 .env 文件
    current_path = pathlib.Path(__file__).parent
    dev_path = current_path / ".env.development"
    prod_path = current_path / ".env.production"
    env_file = prod_path if os.getenv('FLASK_ENV') == 'production' else dev_path
    load_dotenv(env_file)


load_environment_variables()
# 获取所有环境变量
env_vars = os.environ

# for i in env_vars:
#     print(i, env_vars[i])

FRONTEND_PATH = env_vars.get("FRONTEND_PATH")
BACKEND_PATH = env_vars.get("BACKEND_PATH")
LOG_PATH = env_vars.get("LOG_PATH")
