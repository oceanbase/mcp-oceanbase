import subprocess
from typing import Optional
from okctl_mcp_server.utils.errors import format_error

# 导入mcp实例
from okctl_mcp_server import mcp


# 组件安装和更新相关的工具
@mcp.tool()
def install_component(
    component_name: Optional[str] = None,
    version: Optional[str] = None,
):
    """安装OceanBase组件, 目前支持ob-operator，ob-dashboard, local-path-provisioner,cert-manager,不支持其他组件，
    如果未指定，默认将安装ob-operator和 ob-dashboard

    Args:
        component_name: 组件名称
        version: 组件版本
    """
    if component_name and component_name not in [
        "ob-operator",
        "ob-dashboard",
        "local-path-provisioner",
        "cert-manager",
    ]:
        return f"不支持安装{component_name}组件"
    try:
        cmd = f"okctl install {component_name}"

        # 添加可选参数
        if version:
            cmd += f" --version {version}"

        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def update_component(
    component_name: Optional[str] = None,
):
    """更新OceanBase组件, 目前支持ob-operator，ob-dashboard, local-path-provisioner,cert-manager,不支持其他组件，
    如果未指定，默认将更新ob-operator和 ob-dashboard

    Args:
        component_name: 组件名称
    """
    if component_name and component_name not in [
        "ob-operator",
        "ob-dashboard",
        "local-path-provisioner",
        "cert-manager",
    ]:
        return f"不支持更新{component_name}组件"
    try:
        cmd = f"okctl update {component_name}"

        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)
