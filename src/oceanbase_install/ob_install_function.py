import socket
import subprocess
import os
import time
import logging
import uuid
import yaml
import tempfile

logger = logging.getLogger("oceanbase_mcp_server")


def is_docker_available():
    """
    检查当前系统是否存在可执行的Docker环境。

    Returns:
        bool: 如果Docker命令可执行返回True，否则返回False。
    """
    try:
        # 使用subprocess运行docker --version命令
        # 设置stdout和stderr为DEVNULL以避免输出干扰
        # check=True会在返回码非零时抛出CalledProcessError异常
        subprocess.run(
            ["docker", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        # 命令存在但执行失败（如权限问题）
        return False
    except FileNotFoundError:
        # Docker命令不存在
        return False
    except Exception as e:
        # 其他异常情况（如超时，但通常不会发生）
        return False


def start_oceanbase_with_log_check(
    container_name: str = "oceanbase" + uuid.uuid4().hex,
    root_password: str = "root",
    port: int = 2881,
    image: str = "oceanbase/oceanbase-ce:latest",
    timeout: int = 240,
    check_interval: int = 5,
    log_keyword: str = "boot success",
) -> str:
    """
    启动 OceanBase 数据库容器并通过日志检测启动状态

    Args:
        container_name (str): 容器名称 (默认: "oceanbase")
        root_password (str): root 用户密码 (默认: "root")
        port (int): 宿主机映射端口 (默认: 2881)
        image (str): Docker 镜像 (默认: oceanbase/oceanbase-ce:latest)
        timeout (int): 最大等待时间（秒）(默认: 120)
        check_interval (int): 日志检查间隔（秒）(默认: 5)
        log_keyword (str): 成功启动的日志关键词 (默认: "boot success")

    Returns:
        str: 容器ID

    Raises:
        RuntimeError: 如果启动过程失败
    """

    def _get_container_logs(container: str) -> str:
        """获取容器日志"""
        result = subprocess.run(
            ["docker", "logs", container],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        return result.stdout.lower()

    try:
        # 启动容器
        run_cmd = [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "-p",
            f"{port}:2881",
            "-e",
            "MODE=SLIM",
            "-e",
            f"MYSQL_ROOT_PASSWORD={root_password}",
            image,
        ]

        result = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()
        logger.info(f"🟢 容器已启动 | ID: {container_id}")
        return f"OceanBase Docker启动成功，容器id为：{container_id}"
        # 日志检测循环
        # start_time = time.time()
        # logger.info(f"🔍 开始检测启动日志 (关键词: '{log_keyword}')...")

        # while (time.time() - start_time) < timeout:
        #     # 获取容器状态
        #     inspect_result = subprocess.run(
        #         ["docker", "inspect", "--format={{.State.Status}}", container_name],
        #         capture_output=True,
        #         text=True,
        #     )
        #     container_status = inspect_result.stdout.strip()

        #     if container_status != "running":
        #         raise RuntimeError(f"容器状态异常: {container_status}")

        #     # 获取新增日志
        #     logs = _get_container_logs(container_name)
        #     if log_keyword.lower() in logs:
        #         logger.info(f"✅ 检测到启动成功标识: '{log_keyword}'")
        #         logger.info(f"⏱️ 启动耗时: {int(time.time() - start_time)} 秒")
        #         logger.debug(
        #             f"🔗 连接信息: mysql -h127.0.0.1 -P{port} -uroot -p{root_password}"
        #         )
        #         return "OceanBase Docker启动成功，container_id为：" + container_id

        #     logger.info(f"⏳ 等待启动 ({int(time.time() - start_time)}/{timeout}s)...")
        #     time.sleep(check_interval)

        # 超时处理
        # logs = _get_container_logs(container_name)
        # error_msg = [
        #     "🚨 启动超时，可能原因:",
        #     f"1. 镜像下载慢: 尝试手动执行 docker pull {image}",
        #     f"2. 资源不足: OceanBase 需要至少 2GB 内存",
        #     f"3. 查看完整日志: docker logs {container_name}",
        #     "--- 最后 50 行日志 ---",
        #     "\n".join(logs.splitlines()[-50:]),
        # ]
        # raise RuntimeError("\n".join(error_msg))

    except subprocess.CalledProcessError as e:
        error_lines = [
            "🚨 容器启动失败:",
            f"命令: {' '.join(e.cmd)}",
            f"错误: {e.stderr.strip() or '无输出'}",
        ]
        if "port is already allocated" in e.stderr.lower():
            error_lines.append(f"解决方案: 更换端口或停止占用 {port} 端口的进程")
        raise RuntimeError("\n".join(error_lines)) from e

    except Exception as e:
        raise RuntimeError(f"未知错误: {str(e)}") from e


def check_internet_connection(timeout=3) -> str:
    """
    检测当前环境是否具有公网连接能力
    :param timeout: 超时时间（秒）
    :return: bool 是否连通
    """
    test_servers = [
        ("8.8.8.8", 53),  # Google DNS
        ("114.114.114.114", 53),  # 114 DNS
        ("223.5.5.5", 53),  # AliDNS
    ]

    for host, port in test_servers:
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.close()
            return "当前环境具有公网连接能力"
        except (socket.error, OSError):
            continue
    return "失败！当前环境没有公网连接能力"


def install_obd(sudo_user=True, password="") -> str:
    """
    执行OceanBase All in One在线安装
    :param sudo_user: 是否使用管理员权限安装
    :param password: 可选sudo密码（安全风险提示）
    :return: 安装结果和obd路径元组 (bool, str)
    https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
    https://www.oceanbase.com/docs/community-observer-cn-10000000000096602
    """
    if is_obd_available():
        return f"OBD 安装成功，opd_path: {os.path.expanduser('~/.oceanbase-all-in-one/obd/usr/bin/obd')}"
    install_cmd = (
        'bash -c "$(curl -s https://obbusiness-private.oss-cn-shanghai.aliyuncs.com/download-center'
        '/opensource/oceanbase-all-in-one/installer.sh)"'
    )

    try:
        if sudo_user:
            if not password:
                return "用户和密码不可以为空"

            # 管理员模式安装
            subprocess.run(
                f"echo {password} | sudo -S {install_cmd}",
                shell=True,
                check=True,
                universal_newlines=True,
                encoding="utf-8",
            )
            obd_path = os.path.expanduser("~/.oceanbase-all-in-one/obd/usr/bin/obd")
        else:
            # Not Support now
            obd_path = os.path.expanduser("~/.oceanbase-all-in-one/obd/usr/bin/obd")

        # 设置环境变量
        env_script = os.path.expanduser("~/.oceanbase-all-in-one/bin/env.sh")
        subprocess.run(
            f"source {env_script}", shell=True, executable="/bin/bash", check=True
        )

        return f"OBD 安装成功，opd_path: {obd_path}"

    except subprocess.CalledProcessError as e:
        return f"OBD 安装失败: {e.returncode}  {e.stderr} "


def generate_ob_config(
    servers, global_config=None, server_common_config=None, user_config=None
):
    if not global_config:
        global_config = {
            "memory_limit": "4G",
            "system_memory": "1G",
            "datafile_size": "2G",
            "datafile_next": "2G",
            "datafile_maxsize": "20G",
            "log_disk_size": "14G",
            "cpu_count": 4,
            "production_mode": False,
            "enable_syslog_wf": False,
            "max_syslog_file_count": 4,
        }

    if not server_common_config:
        server_common_config = {
            "mysql_port": 2881,
            "rpc_port": 2882,
            "obshell_port": 2886,
            "home_path": "/root/observer",
        }

    """生成 OceanBase 部署配置字典结构"""
    config = {"oceanbase-ce": {"servers": [], "global": global_config}}

    if user_config:
        config["user"] = user_config

    # 生成服务器配置
    for idx, (ip, zone) in enumerate(servers, 1):
        server_name = f"server{idx}"

        # 服务器节点配置
        config["oceanbase-ce"]["servers"].append({"name": server_name, "ip": ip})

        # 服务器个性化配置
        config["oceanbase-ce"][server_name] = {**server_common_config, "zone": zone}

    return config


def deploy_oceanbase(cluster_name, config):
    """部署 OceanBase 集群"""
    try:
        # 生成临时 YAML 文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            yaml.dump(config, f, sort_keys=False, default_flow_style=False, width=120)
            temp_path = f.name
            logger.info(temp_path)

        # 执行部署命令
        cmd = ["obd", "cluster", "deploy", cluster_name, "-c", temp_path]

        result = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        return True, result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"部署失败: {e.stderr}\n建议检查：\n1. 服务器SSH连通性\n2. 端口冲突问题\n3. 磁盘空间是否充足"
        return error_msg
    except Exception as e:
        return f"未知错误: {str(e)}"


def start_oceanbase_cluster(cluster_name: str):
    """
    启动 OceanBase 数据库集群

    :param cluster_name: 集群名称 (如: obtest)
    :return: 包含执行状态的字典 {
        "success": bool,
        "output": str,
        "error": str
    }
    """
    # 构造命令参数（避免shell注入风险）
    cmd = "ulimit -u 120000 && obd cluster start " + cluster_name
    result = subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # result = execute_shell_command(cmd)
    if result.returncode == 0:
        return (
            f"✅ Cluster '{cluster_name}' started successfully\nOutput: {result.stdout}"
        )
    else:
        return f"❌ Failed to start cluster '{cluster_name}'\nError: {result.stderr}"


def check_oceanbase_cluster_status(cluster_name: str):
    """
    获取 OceanBase 集群状态信息

    :param cluster_name: 集群名称 (如: obtest)
    """
    # 构造安全命令参数
    cmd = ["obd", "cluster", "display", cluster_name]
    status = execute_shell_command(cmd)
    if status["success"]:
        return f"🟢 Cluster '{cluster_name}' status:\n{status['output']}"
    else:
        if status["output"]:
            msg = f"Command output: {status['output']}"
            return (
                f"🔴 Failed to get status for cluster '{cluster_name}' "
                + f"Error: {status['error']}"
                + msg
            )
        else:
            return (
                f"🔴 Failed to get status for cluster '{cluster_name}' "
                + f"Error: {status['error']}"
            )


def execute_shell_command(cmd: list):
    """
    启动 OceanBase 数据库集群
    :return: 包含执行状态的字典 {
        "success": bool,
        "output": str,
        "error": str
    }
    """

    try:
        # 执行命令并捕获输出
        result = subprocess.run(
            cmd,
            check=True,  # 非零退出码时自动抛 CalledProcessError
            capture_output=True,
            text=True,
            timeout=300,  # 设置5分钟超时（按需调整）
        )

        msg = {"success": True, "output": result.stdout.strip(), "error": ""}

    except subprocess.CalledProcessError as e:
        # 处理命令执行失败
        msg = {"success": False, "output": e.stdout.strip(), "error": e.stderr.strip()}

    except FileNotFoundError:
        # 处理命令不存在
        msg = {"success": False, "output": "", "error": "command not found."}

    except subprocess.TimeoutExpired:
        # 处理超时
        msg = {
            "success": False,
            "output": "",
            "error": "Command timed out after 5 minutes",
        }

    return msg


def is_obd_available():
    """
    检查当前系统OBD是否已安装

    Returns:
        bool: 如果OBD命令可执行返回True，否则返回False。
    """
    try:
        # 使用subprocess运行obd --version命令
        # 设置stdout和stderr为DEVNULL以避免输出干扰
        # check=True会在返回码非零时抛出CalledProcessError异常
        os.environ["HOME"] = "/" + os.getlogin()
        subprocess.run(
            ["obd", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        # 命令存在但执行失败（如权限问题）
        return False
    except FileNotFoundError:
        # Docker命令不存在
        return False
    except Exception as e:
        # 其他异常情况（如超时，但通常不会发生）
        return False
