import socket
import subprocess
import os
import time
import logging
import uuid

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
            ['docker', '--version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
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
        log_keyword: str = "boot success"
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
            errors="ignore"
        )
        return result.stdout.lower()

    try:

        # 启动容器
        run_cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{port}:2881",
            "-e", "MODE=SLIM",
            "-e", f"MYSQL_ROOT_PASSWORD={root_password}",
            image
        ]

        result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        container_id = result.stdout.strip()
        logger.info(f"🟢 容器已启动 | ID: {container_id}")

        # 日志检测循环
        start_time = time.time()
        logger.info(f"🔍 开始检测启动日志 (关键词: '{log_keyword}')...")

        while (time.time() - start_time) < timeout:
            # 获取容器状态
            inspect_result = subprocess.run(
                ["docker", "inspect", "--format={{.State.Status}}", container_name],
                capture_output=True,
                text=True
            )
            container_status = inspect_result.stdout.strip()

            if container_status != "running":
                raise RuntimeError(f"容器状态异常: {container_status}")

            # 获取新增日志
            logs = _get_container_logs(container_name)
            if log_keyword.lower() in logs:
                logger.info(f"✅ 检测到启动成功标识: '{log_keyword}'")
                logger.info(f"⏱️ 启动耗时: {int(time.time() - start_time)} 秒")
                logger.debug(f"🔗 连接信息: mysql -h127.0.0.1 -P{port} -uroot -p{root_password}")
                return "OceanBase Docker启动成功，container_id为：" + container_id

            logger.info(f"⏳ 等待启动 ({int(time.time() - start_time)}/{timeout}s)...")
            time.sleep(check_interval)

        # 超时处理
        logs = _get_container_logs(container_name)
        error_msg = [
            "🚨 启动超时，可能原因:",
            f"1. 镜像下载慢: 尝试手动执行 docker pull {image}",
            f"2. 资源不足: OceanBase 需要至少 2GB 内存",
            f"3. 查看完整日志: docker logs {container_name}",
            "--- 最后 50 行日志 ---",
            "\n".join(logs.splitlines()[-50:])
        ]
        raise RuntimeError("\n".join(error_msg))

    except subprocess.CalledProcessError as e:
        error_lines = [
            "🚨 容器启动失败:",
            f"命令: {' '.join(e.cmd)}",
            f"错误: {e.stderr.strip() or '无输出'}"
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
        ("223.5.5.5", 53)  # AliDNS
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


def install_obd(sudo_user=True, password='') -> str:
    """
    执行OceanBase All in One在线安装
    :param sudo_user: 是否使用管理员权限安装
    :param password: 可选sudo密码（安全风险提示）
    :return: 安装结果和obd路径元组 (bool, str)
    """
    install_cmd = ('bash -c "$(curl -s https://obbusiness-private.oss-cn-shanghai.aliyuncs.com/download-center'
                   '/opensource/oceanbase-all-in-one/installer.sh)"')

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
                encoding='utf-8',
            )
            obd_path = os.path.expanduser("~/.oceanbase-all-in-one/obd/usr/bin/obd")
        else:
            # Not Support now
            obd_path = os.path.expanduser("~/.oceanbase-all-in-one/obd/usr/bin/obd")

        # 设置环境变量
        env_script = os.path.expanduser("~/.oceanbase-all-in-one/bin/env.sh")
        subprocess.run(f"source {env_script}", shell=True, executable="/bin/bash", check=True)

        return f"OBD 安装成功，opd_path: {obd_path}"

    except subprocess.CalledProcessError as e:
        return f"OBD 安装失败: {e.returncode}  {e.stderr} "

