import asyncio
import json
import os
import pprint
import subprocess
import traceback

import aiohttp
import aiodocker
from aiodocker import DockerError

from utils.log_util import log


class DockerManager:
    def __init__(self):
        self.docker = aiodocker.Docker()

    async def install_docker(self):
        # 示例：使用 curl 安装 Docker
        # 注意：实际安装 Docker 通常需要更多步骤，这里仅提供一个简单的示例
        try:
            await asyncio.create_subprocess_shell(
                "curl -fsSL https://get.docker.com -o install-docker.sh && sudo sh install-docker.sh"
            )
            log.info("Docker 安装完成。")
            return {"result": True, "msg": "Docker 安装完成。"}
        except Exception as e:
            log.error(f"安装 Docker 时发生错误：{e}")
            return {"result": False, "msg": f"安装 Docker 时发生错误：{e}"}

    async def check_docker(self):
        try:
            await self.docker.images.list()
            return {"result": True, "msg": "Docker 已安装并且正在运行。"}
        except aiodocker.exceptions.DockerError as e:
            return {"result": False, "msg": "Docker 未安装或守护进程未启动。"}
        except Exception as e:
            return {"result": False, "msg": f"发生未知错误：{e}"}

    async def get_docker_networks(self, network_name=None):
        """
        获取 Docker 网络信息

        :param network_name: 可选，指定网络名称或ID。若为None则获取所有网络
        :return: dict {
            "result": bool,
            "msg": str,
            "data": list/dict  # 网络详细信息
        }
        """
        res = {
            "result": False,
            "msg": "初始化",
            "data": []
        }

        try:
            if network_name:
                # 获取单个网络信息
                log.info(f"正在查询网络 {network_name} 的详细信息...")
                network = await self.docker.networks.get(network_name)
                details = await network.show()

                formatted = {
                    "name": details["Name"],
                    "id": details["Id"],
                    "driver": details["Driver"],
                    "subnet": details["IPAM"]["Config"][0]["Subnet"] if details["IPAM"]["Config"] else "N/A",
                    "containers": [
                        {"id": cid, "ip": config["IPv4Address"]}
                        for cid, config in details["Containers"].items()
                    ]
                }

                res.update({
                    "result": True,
                    "msg": f"成功获取网络 {network_name} 的信息",
                    "data": formatted
                })
                log.info(f"网络 {network_name} 查询成功")
            else:
                # 获取所有网络列表
                log.info("正在查询所有Docker网络...")
                networks = await self.docker.networks.list()

                network_list = []
                for net in networks:
                    details = await (await self.docker.networks.get(net["Id"])).show()
                    network_list.append({
                        "name": details["Name"],
                        "id": details["Id"],
                        "driver": details["Driver"],
                        "created": details["Created"],
                        "subnet": details["IPAM"]["Config"][0]["Subnet"] if details["IPAM"]["Config"] else "N/A",
                        "gateway": details["IPAM"]["Config"][0].get("Gateway", "N/A") if details["IPAM"]["Config"] else "N/A",
                        "container_count": len(details["Containers"])
                    })

                res.update({
                    "result": True,
                    "msg": f"成功获取 {len(network_list)} 个网络",
                    "data": network_list
                })
                log.info(f"共查询到 {len(network_list)} 个网络")

        except aiodocker.exceptions.DockerError as e:
            error_msg = f"Docker操作失败: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": []
            })
            log.error(error_msg)
        except KeyError as e:
            error_msg = f"数据解析错误，缺少字段: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": []
            })
            log.error(error_msg)
        except Exception as e:
            error_msg = f"发生未预期错误: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": []
            })
            log.error(error_msg, exc_info=True)

        return res

    async def create_container(self, config):
        """
        创建 Docker 容器

        :param config: 容器配置字典
        :return: dict {
            "result": bool,
            "msg": str,
            "data": dict  # 容器详细信息
        }
        """
        res = {
            "result": False,
            "msg": "初始化",
            "data": {}
        }

        try:

            log.info(f"name: {config['name']}")
            # 创建容器
            container = await self.docker.containers.create(
                name=config["name"],
                config={
                    "HostConfig": config.get("host_config", {}),
                    "Image": config["image"],
                    "Env": config.get("env", []),
                    "ExposedPorts": config.get("exposed_ports", {}),
                    "Volumes": config.get("volumes", {}),
                    "Hostname": config.get("hostname", ""),
                    "RestartPolicy": config.get("restart_policy", {}),
                    "NetworkingConfig": {
                        "EndpointsConfig": {
                            config["host_config"]["network_mode"]: {
                                "IPAMConfig": {
                                    "IPv4Address": config.get("ip_address", "")
                                }
                            }
                        }
                    }
                },
                # detach=True  # 以分离模式运行容器
            )

            # 获取容器的详细信息
            container_details = await container.show()

            formatted = {
                "id": container_details["Id"],
                "name": container_details["Name"].lstrip("/"),  # 去掉名称前的斜杠
                "image": container_details["Config"]["Image"],
                "created": container_details["Created"],
                "status": container_details["State"]["Status"],
                "hostname": container_details["Config"]["Hostname"],
                "ports": container_details["NetworkSettings"]["Ports"],
                "ip_address": container_details["NetworkSettings"]["IPAddress"],
                "environment": container_details["Config"]["Env"],
                "volumes": container_details["Mounts"]
            }

            res.update({
                "result": True,
                "msg": f"容器创建成功，ID: {container_details['Id']}",
                "data": formatted
            })

        except DockerError as e:
            error_msg = f"Docker操作失败: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": {}
            })
        except KeyError as e:
            error_msg = f"数据解析错误，缺少字段: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": {}
            })
        except Exception as e:
            error_msg = f"发生未预期错误: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": {}
            })

        return res

    async def start_container(self, container_id: str) -> dict:
        """
        运行指定的Docker容器

        :param container_id: 容器ID或名称
        :return: dict {
            "result": bool,
            "msg": str,
            "data": dict  # 容器详细信息
        }
        """
        res = {
            "result": False,
            "msg": "初始化",
            "data": {}
        }

        try:
            # 获取容器对象
            container = await self.docker.containers.get(container_id)

            # 启动容器
            await container.start()

            # 获取更新后的容器状态
            container_details = await container.show()

            # 格式化返回数据（与create_container保持一致）
            formatted = {
                "id": container_details["Id"],
                "name": container_details["Name"].lstrip("/"),
                "image": container_details["Config"]["Image"],
                "created": container_details["Created"],
                "status": container_details["State"]["Status"],
                "hostname": container_details["Config"]["Hostname"],
                "ports": container_details["NetworkSettings"]["Ports"],
                "ip_address": container_details["NetworkSettings"]["IPAddress"],
                "environment": container_details["Config"]["Env"],
                "volumes": container_details["Mounts"]
            }

            res.update({
                "result": True,
                "msg": f"容器 {container_details['Name'].lstrip('/')} 启动成功",
                "data": formatted
            })
            log.info(f"容器启动成功: {container_id}")

        except aiodocker.exceptions.DockerError as e:
            error_status = getattr(e, "status", 500)

            if error_status == 404:
                error_msg = f"容器 {container_id} 不存在"
            elif error_status == 304:
                error_msg = f"容器 {container_id} 已经处于运行状态"
            elif error_status == 500:
                error_msg = f"容器启动失败: {str(e)}"
            else:
                error_msg = f"Docker操作失败: {str(e)}"

            res.update({
                "msg": error_msg,
                "data": {"docker_status": error_status}
            })
            log.warning(f"启动容器错误: {error_msg}")

        except Exception as e:
            error_msg = f"发生未预期错误: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": {}
            })
            log.exception("启动容器异常")

        return res

    async def stop_container(self, container_id: str, timeout: int = 10) -> dict:
        """
        停止运行指定的Docker容器

        :param container_id: 容器ID或名称
        :param timeout: 等待容器停止的超时时间（秒）
        :return: dict {
            "result": bool,
            "msg": str,
            "data": dict  # 容器详细信息
        }
        """
        res = {
            "result": False,
            "msg": "初始化",
            "data": {}
        }

        try:
            # 获取容器对象
            container = await self.docker.containers.get(container_id)
            current_state = await container.show()

            # 检查当前状态
            if current_state["State"]["Status"] not in ["running", "restarting"]:
                raise RuntimeError(f"容器当前状态为 {current_state['State']['Status']}，无法停止")

            # 停止容器
            await container.stop(timeout=timeout)

            # 获取更新后的容器状态
            container_details = await container.show()

            # 格式化返回数据（与create_container/start_container保持一致）
            formatted = {
                "id": container_details["Id"],
                "name": container_details["Name"].lstrip("/"),
                "image": container_details["Config"]["Image"],
                "created": container_details["Created"],
                "status": container_details["State"]["Status"],
                "hostname": container_details["Config"]["Hostname"],
                "ports": container_details["NetworkSettings"]["Ports"],
                "ip_address": container_details["NetworkSettings"]["IPAddress"],
                "environment": container_details["Config"]["Env"],
                "volumes": container_details["Mounts"],
                "exit_code": container_details["State"].get("ExitCode", -1)
            }

            res.update({
                "result": True,
                "msg": f"容器 {container_details['Name'].lstrip('/')} 已停止",
                "data": formatted
            })
            log.info(f"容器停止成功: {container_id}")

        except aiodocker.exceptions.DockerError as e:
            error_status = getattr(e, "status", 500)

            if error_status == 404:
                error_msg = f"容器 {container_id} 不存在"
            elif error_status == 304:
                error_msg = f"容器 {container_id} 已经处于停止状态"
            elif error_status == 500:
                error_msg = f"容器停止失败: {str(e)}"
            else:
                error_msg = f"Docker操作失败: {str(e)}"

            res.update({
                "msg": error_msg,
                "data": {"docker_status": error_status}
            })
            log.warning(f"停止容器错误: {error_msg}")

        except RuntimeError as e:
            res.update({
                "msg": str(e),
                "data": {"current_state": current_state["State"]["Status"]}
            })
            log.warning(f"容器状态不允许停止: {str(e)}")

        except Exception as e:
            error_msg = f"发生未预期错误: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": {}
            })
            log.exception("停止容器异常")

        return res

    async def get_container_logs(
            self,
            container_id: str,
            tail: int = 100,
            since: str = None,
            until: str = None,
            follow: bool = False,
            timestamps: bool = False,
            stream: bool = False
    ) -> dict:
        """
        获取Docker容器日志

        :param container_id: 容器ID或名称
        :param tail: 返回最后多少行日志（默认100）
        :param since: 返回此时间戳之后的日志（RFC3339格式）
        :param until: 返回此时间戳之前的日志（RFC3339格式）
        :param follow: 是否持续输出新日志（类似tail -f）
        :param timestamps: 是否包含时间戳
        :param stream: 是否以流式方式返回（适合大日志）
        :return: dict {
            "result": bool,
            "msg": str,
            "data": {
                "logs": str/list,  # 字符串或行列表
                "container_id": str,
                "warnings": list
            }
        }
        """
        res = {
            "result": False,
            "msg": "",
            "data": {
                "logs": "",
                "container_id": container_id,
                "warnings": []
            }
        }

        try:
            # 获取容器对象
            container = await self.docker.containers.get(container_id)
            container_info = await container.show()

            # 检查容器状态
            if container_info["State"]["Status"] not in ["running", "exited"]:
                raise RuntimeError(f"容器状态 {container_info['State']['Status']} 不支持日志查询")

            # 构建日志参数
            log_params = {
                "stdout": True,
                "stderr": True,
                "tail": str(tail),
                "timestamps": timestamps,
                "follow": follow
            }
            if since:
                log_params["since"] = since
            if until:
                log_params["until"] = until

            # 获取日志
            if stream:
                # 流式日志处理
                logs_stream = container.log(**log_params)
                res["data"]["logs"] = []  # 改为列表形式

                async for log_chunk in logs_stream:
                    if isinstance(log_chunk, bytes):
                        log_chunk = log_chunk.decode("utf-8", errors="replace")
                    res["data"]["logs"].append(log_chunk.strip())

                res["result"] = True
                res["msg"] = f"成功获取容器 {container_id} 的流式日志"
            else:
                # 普通日志获取
                logs = await container.log(**log_params)
                decoded_logs = []

                for log_entry in logs:
                    if isinstance(log_entry, bytes):
                        log_entry = log_entry.decode("utf-8", errors="replace")
                    decoded_logs.append(log_entry.strip())

                res["data"]["logs"] = "\n".join(decoded_logs) if not timestamps else decoded_logs
                res["result"] = True
                res["msg"] = f"成功获取容器 {container_id} 的日志（共 {len(decoded_logs)} 行）"

            # 捕获可能的警告信息
            if hasattr(container, "attrs") and "Warnings" in container.attrs:
                res["data"]["warnings"] = container.attrs["Warnings"]

        except aiodocker.exceptions.DockerError as e:
            error_status = getattr(e, "status", 500)

            if error_status == 404:
                error_msg = f"容器 {container_id} 不存在"
            elif error_status == 406:
                error_msg = f"容器 {container_id} 未运行，无法获取日志"
            else:
                error_msg = f"Docker操作失败: {str(e)}"

            res.update({
                "msg": error_msg,
                "data": {"docker_status": error_status}
            })
            log.warning(f"获取日志错误: {error_msg}")

        except RuntimeError as e:
            res.update({
                "msg": str(e),
                "data": {"current_state": container_info["State"]["Status"]}
            })
            log.warning(f"容器状态不支持日志查询: {str(e)}")

        except Exception as e:
            error_msg = f"获取日志时发生未知错误: {str(e)}"
            res.update({
                "msg": error_msg,
                "data": {}
            })
            log.exception("获取日志异常")

        return res

    async def create_network(self, network_config: dict) -> dict:
        """
        创建Docker网络（适配前端表单数据结构）

        :param network_config: 前端传入的网络配置，格式示例:
            {
                "Name": "my-network",
                "Driver": "bridge",
                "IPAM": {
                    "Config": [
                        {
                            "Subnet": "172.28.0.0/16",
                            "Gateway": "172.28.0.1"
                        },
                        {
                            "Subnet": "2001:db8::/64",
                            "Gateway": "fd00::1"
                        }
                    ]
                },
                "EnableIPv6": True
            }
        :return: {
            "result": bool,
            "msg": str,
            "data": {
                "id": str,         # 网络ID
                "name": str,       # 网络名称
                "warning": str     # 警告信息（如有）
            }
        }
        """
        response = {
            "result": False,
            "msg": "",
            "data": {}
        }

        try:
            # 验证必要参数
            if not network_config.get("Name"):
                raise ValueError("网络名称不能为空")

            # 构建创建参数
            create_kwargs = {
                "name": network_config["Name"],
                "driver": network_config.get("Driver", "bridge"),
                "check_duplicate": True  # 防止重复创建同名网络
            }

            # 处理IPAM配置
            if "IPAM" in network_config:
                create_kwargs["ipam"] = {
                    "driver": "default",
                    "config": network_config["IPAM"]["Config"]
                }

            # 处理IPv6配置
            if network_config.get("EnableIPv6", False):
                create_kwargs["enable_ipv6"] = True
                # 如果未提供IPv6配置但启用了IPv6，添加默认配置
                if not any(conf.get("Subnet", "").startswith("fd")
                           for conf in create_kwargs.get("ipam", {}).get("config", [])):
                    create_kwargs.setdefault("ipam", {}).setdefault("config", []).append({
                        "subnet": "fd00::/64",
                        "gateway": "fd00::1"
                    })

            # 调用Docker API创建网络
            network = await self.docker.networks.create(create_kwargs)

            # 构建返回数据
            response.update({
                "result": True,
                "msg": f"网络 {network_config['Name']} 创建成功",
                "data": {
                    "id": network.id,
                    "name": network_config["Name"],
                }
            })

        except aiodocker.exceptions.DockerError as e:
            error_msg = f"Docker操作失败: {e.message}" if hasattr(e, "message") else str(e)
            response.update({
                "msg": error_msg,
                "data": {"docker_error": e.status}
            })
            if e.status == 409:
                response["msg"] = f"网络名称 '{network_config.get('Name', '')}' 已存在"

        except ValueError as e:
            response["msg"] = f"参数错误: {str(e)}"

        except Exception as e:
            response["msg"] = f"创建网络时发生未知错误: {str(e)}"
            log.exception("创建网络异常")

        return response

    async def delete_network(self, network_identifier: str, force: bool = False) -> dict:
        """
        删除Docker网络

        :param network_identifier: 网络名称或ID
        :param force: 是否强制删除（删除正在使用的网络）
        :return: {
            "result": bool,
            "msg": str,
            "data": {
                "id": str,         # 被删除的网络ID
                "name": str,       # 被删除的网络名称
                "warnings": list   # 删除过程中的警告信息
            }
        }
        """
        response = {
            "result": False,
            "msg": "",
            "data": {
                "id": "",
                "name": "",
                "warnings": []
            }
        }

        try:
            # 参数校验
            if not network_identifier:
                raise ValueError("网络标识不能为空")

            # 获取网络对象
            network = await self.docker.networks.get(network_identifier)
            network_info = await network.show()

            # 检查网络是否正在被使用
            if not force and network_info.get("Containers"):
                containers = list(network_info["Containers"].keys())
                raise RuntimeError(
                    f"网络 {network_info['Name']} 正在被 {len(containers)} 个容器使用。"
                    "请先移除容器或使用强制删除。"
                )

            # 执行删除操作
            await network.delete()

            # 构建成功响应
            response.update({
                "result": True,
                "msg": f"网络 {network_info['Name']} 删除成功",
                "data": {
                    "id": network.id,
                    "name": network_info["Name"],
                    "warnings": network_info.get("Warning", [])
                }
            })
            log.info(f"成功删除网络: {network_info['Name']}({network.id})")

        except aiodocker.exceptions.DockerError as e:
            error_status = getattr(e, "status", 500)
            error_msg = f"删除网络失败: {str(e)}"

            if error_status == 404:
                error_msg = f"网络 {network_identifier} 不存在"
            elif error_status == 403:
                error_msg = "没有权限删除该网络"
            elif error_status == 409:
                error_msg = "网络正在被使用，拒绝删除"

            response.update({
                "msg": error_msg,
                "data": {"docker_status": error_status}
            })
            log.warning(f"删除网络错误: {error_msg}")

        except ValueError as e:
            response["msg"] = f"参数错误: {str(e)}"
            log.warning(f"参数校验失败: {str(e)}")

        except RuntimeError as e:
            response.update({
                "msg": str(e),
                "data": {
                    "requires_force": True,
                    "container_count": len(network_info.get("Containers", {}))
                }
            })
            log.warning(f"网络正在使用: {str(e)}")

        except Exception as e:
            response["msg"] = f"删除网络时发生未知错误: {str(e)}"
            log.exception("删除网络异常")

        return response

    async def pull_docker_image(self, repository, image_name):
        """
        拉取 Docker 镜像并显示实时进度

        :param repository: 仓库地址，例如 'docker.io' 或 'localhost:5000'
        :param image_name: 镜像名称，例如 'ubuntu' 或 'nginx:latest'
        :return: dict
        """
        res = {
            "result": False,
            "msg": "成功",
            "details": []
        }

        repository = repository.replace("https://", "").replace("http://", "")

        # 拼接完整的镜像路径
        full_image_name = f"{repository}/{image_name}" if repository else image_name

        try:
            log.info(f"正在从仓库 {repository or '默认仓库'} 拉取镜像 {image_name}...")

            await self.docker.images.pull(full_image_name)

            log.info(f"镜像 {full_image_name} 拉取成功")
            res["result"] = True
            res["msg"] = f"已成功拉取镜像：{full_image_name}"

        except aiodocker.exceptions.DockerError as e:
            error_msg = f"拉取镜像失败：{str(e)}"
            res["msg"] = error_msg
            log.error(error_msg)
        except Exception as e:
            error_msg = f"发生错误：{str(e)}"
            res["msg"] = error_msg
            log.error(error_msg)
        finally:
            return res

    async def remove_image(self, image_id, force=False):
        """
        根据 Image ID 删除 Docker 镜像

        :param image_id: 要删除的镜像ID（完整或短ID）
        :param force: 是否强制删除（即使有容器正在使用）
        :return: dict
        """
        res = {
            "result": False,
            "msg": "",
            "deleted": None
        }

        try:
            log.info(f"正在尝试通过ID删除镜像: {image_id} (force={force})")

            await self.docker.images.delete(image_id, force=force)

            log.info(f"镜像ID {image_id} 删除成功")
            res.update({
                "result": True,
                "msg": f"镜像ID {image_id} 删除成功",
                "deleted": {
                    "id": image_id
                }
            })

        except aiodocker.exceptions.DockerError as e:
            error_msg = f"通过ID删除镜像 {image_id} 失败: {str(e)}"
            res["msg"] = error_msg
            log.error(error_msg)

            # 处理特定错误情况
            if "image is referenced in multiple repositories" in str(e):
                res["msg"] = f"镜像 {image_id} 被多个仓库引用，请先删除相关标签"
            elif "image is being used by running container" in str(e):
                res["msg"] = f"镜像 {image_id} 正在被容器使用，请先停止相关容器或使用 force=True"
            elif "No such image" in str(e):
                res["msg"] = f"镜像ID {image_id} 不存在"

        except Exception as e:
            error_msg = f"通过ID删除镜像 {image_id} 时发生未知错误: {str(e)}"
            res["msg"] = error_msg
            log.error(error_msg)

        finally:
            return res

    async def test_source(self, source_url):
        """
        使用 aiohttp 异步测试 Docker 镜像源的连通性
        :param source_url: 镜像源的 URL，例如 'https://docker.mirrors.ustc.edu.cn/v2/_catalog'
        :return: 是否连通
        """
        res = {
            "status": False,
            "sourceUrl": source_url,
            "msg": "成功"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source_url, timeout=10) as response:
                    if response.status != 200:
                        res["msg"] = f"镜像源不可用，状态码：{response.status}"
                    else:
                        res["status"] = True
        except asyncio.TimeoutError:
            res["msg"] = "请求超时"
        except aiohttp.ClientError as e:
            res["msg"] = f"请求失败：{e}"
        except Exception as e:
            res["msg"] = f"意外错误：{e}"
        finally:
            return res

    async def get_docker_images(self):
        try:
            images = await self.docker.images.list()
            return {"images": [image for image in images]}
        except Exception as e:
            log.error(f"获取 Docker 镜像时发生错误：{e}")
            return {"images": []}

    async def add_docker_source(self, source_url):
        res = {
            "result": False,
            "msg": "成功"
        }
        daemon_json_path = "/etc/docker/daemon.json"
        try:
            # 如果文件不存在，创建一个空的配置
            if not os.path.exists(daemon_json_path):
                with open(daemon_json_path, "w") as file:
                    json.dump({}, file)

            # 读取现有的配置
            with open(daemon_json_path, "r") as file:
                daemon_config = json.load(file)

            # 添加新的镜像源
            if "registry-mirrors" not in daemon_config:
                daemon_config["registry-mirrors"] = []
            if source_url not in daemon_config["registry-mirrors"]:
                daemon_config["registry-mirrors"].append(source_url)

            # 写回配置文件
            with open(daemon_json_path, "w") as file:
                json.dump(daemon_config, file, indent=4)
            await self.restart_docker_service()
            res["result"] = True
            res["msg"] = f"已成功添加镜像源：{source_url}"
        except Exception as e:
            res["msg"] = f"添加镜像源失败：{e}"
        finally:
            return res

    async def remove_docker_source(self, source_url):
        res = {
            "result": False,
            "msg": "成功"
        }
        daemon_json_path = "/etc/docker/daemon.json"
        try:
            # 如果文件不存在，说明没有配置，直接返回
            if not os.path.exists(daemon_json_path):
                res["msg"] = f"镜像源 {source_url} 不存在"
                return res

            # 读取现有的配置
            with open(daemon_json_path, "r") as file:
                daemon_config = json.load(file)

            # 检查并删除指定的镜像源
            if "registry-mirrors" in daemon_config:
                if source_url in daemon_config["registry-mirrors"]:
                    daemon_config["registry-mirrors"].remove(source_url)
                    # 如果删除后镜像源列表为空，可以选择删除整个键
                    if not daemon_config["registry-mirrors"]:
                        del daemon_config["registry-mirrors"]
                    # 写回配置文件
                    with open(daemon_json_path, "w") as file:
                        json.dump(daemon_config, file, indent=4)
                    await self.restart_docker_service()
                    res["result"] = True
                    res["msg"] = f"已成功删除镜像源：{source_url}"
                else:
                    res["msg"] = f"镜像源 {source_url} 不存在"
            else:
                res["msg"] = f"镜像源 {source_url} 不存在"
        except Exception as e:
            res["msg"] = f"删除镜像源失败：{e}"
        finally:
            return res

    async def restart_docker_service(self):
        try:
            # 使用 systemctl 命令重启 Docker 服务
            reload_p = await asyncio.create_subprocess_shell("sudo systemctl daemon-reload")
            await reload_p.wait()
            reload_p = await asyncio.create_subprocess_shell("sudo systemctl restart docker")
            await reload_p.wait()
            # await self.close()
            # self.docker = aiodocker.Docker()

            log.info("Docker 服务已成功重启")
        except Exception as e:
            log.error(f"重启 Docker 服务失败：{e}")

    async def get_docker_sources(self):
        try:
            info = await self.docker.system.info()

            return {
                "sources": [{"downloadUrl": source_url.rstrip('/')} for source_url in
                            info.get("RegistryConfig", {}).get("Mirrors", [])]
            }
        except Exception as e:
            log.error(f"获取 Docker 镜像源时发生错误：{e}")
            return {"sources": []}

    async def list_all_containers(self):
        """
        获取所有容器列表（包含运行中和已停止的），返回精简信息：
        - id: 容器完整ID
        - short_id: 短ID（前12位）
        - name: 容器名称（去掉 `/` 前缀）
        - image: 使用的镜像
        - status: 状态描述（如 "Up 2 hours"）
        - state: 运行状态（"running", "exited", "paused" 等）
        - ip: 容器的IP地址（仅当运行时返回）

        :return: dict {result: bool, msg: str, containers: list}
        """
        res = {
            "result": False,
            "msg": "",
            "containers": []
        }

        try:
            log.info("正在获取所有容器列表...")
            containers = await self.docker.containers.list(all=True)  # 包含停止的容器

            res["containers"] = await asyncio.gather(
                *[self._format_container_info(container) for container in containers])
            res.update({
                "result": True,
                "msg": f"成功获取 {len(res['containers'])} 个容器",
            })
            log.info(f"获取到 {len(res['containers'])} 个容器")

        except Exception as e:
            res["msg"] = f"获取容器列表失败: {str(e)}"
            log.error(res["msg"])

        return res

    async def _format_container_info(self, container):
        """
        格式化单个容器的信息（内部方法）
        """
        # 获取基础信息（不调用 container.show() 以提升性能）
        info = {
            "id": container.id,
            "short_id": container.id[:12],
            "name": container["Names"][0].lstrip("/") if container["Names"] else "",
            "image": container["Image"],
            "status": container["Status"],
            "state": container["State"],
            "ports": [],
            "mounts": []
        }

        pprint.pprint(container["Ports"])

        # 只有运行中的容器才查询IP
        if info["state"] == "running":
            try:
                details = await container.show()
                networks = details["NetworkSettings"]["Networks"]
                info["ip"] = next((net["IPAddress"] for net in networks.values()), None)

                # 从详细数据中添加更完整的端口信息
                if "Ports" in details["NetworkSettings"]:
                    for port, mappings in details["NetworkSettings"]["Ports"].items():
                        if mappings:  # 如果有端口映射
                            for mapping in mappings:
                                port_info = {
                                    "private_port": int(port.split("/")[0]),
                                    "public_port": int(mapping["HostPort"]),
                                    "type": port.split("/")[1] if "/" in port else "tcp",  # 默认tcp
                                    "host_ip": mapping["HostIp"] or "0.0.0.0"
                                }
                                info["ports"].append(port_info)

                # 处理挂载卷信息
                if "Mounts" in details:
                    for mount in details["Mounts"]:
                        mount_info = {
                            "source": mount.get("Source", ""),
                            "destination": mount.get("Destination", ""),
                            "mode": mount.get("Mode", ""),
                            "type": mount.get("Type", "")
                        }
                        info["mounts"].append(mount_info)
            except Exception:
                info["ip"] = None
        else:
            info["ip"] = None

        return info

    async def close(self):
        await self.docker.close()


if __name__ == '__main__':
    async def main():
        manager = DockerManager()
        try:
            pprint.pprint(await manager.get_docker_networks())
            pass
            # 拉取镜像
            # result = await manager.pull_docker_image("docker.xuanyuan.me", "hello-world:latest")
            # await manager.monitor_docker()
            # 添加镜像源
            # result = await manager.add_docker_source("https://docker.xuanyuan.me")
            # print(result)
            # 获取镜像源
            # sources = await manager.get_docker_sources()
            # print(sources)
        finally:
            await manager.close()


    asyncio.run(main())
