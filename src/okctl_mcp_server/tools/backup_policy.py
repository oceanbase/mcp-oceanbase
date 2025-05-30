import subprocess
from typing import Optional
from okctl_mcp_server.utils.errors import format_error

# 导入mcp实例
from okctl_mcp_server import mcp


# 备份策略相关的工具
@mcp.tool()
def list_backup_policies(cluster_name: str, namespace: str = "default"):
    """列出指定集群中的所有备份策略

    Args:
        cluster_name: 集群名称
        namespace: 命名空间（默认为"default"）
    """
    if not cluster_name:
        return "必须指定集群名称"
    try:
        cmd = f"okctl backup-policy list {cluster_name} -n {namespace}"
        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        output = result.stdout
        if not output.strip():
            return "没有找到备份策略"
        return output
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def create_backup_policy(
    tenant_name: str,
    namespace: str = "default",
    archive_path: Optional[str] = None,
    bak_data_path: Optional[str] = None,
    bak_encryption_password: Optional[str] = None,
    dest_type: Optional[str] = None,
    full: Optional[str] = None,
    inc: Optional[str] = None,
    job_keep_days: Optional[int] = None,
    oss_access_id: Optional[str] = None,
    oss_access_key: Optional[str] = None,
    recovery_days: Optional[int] = None,
):
    """在指定集群中创建备份策略

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        archive_path: 备份策略的归档路径
        bak_data_path: 备份策略的备份数据路径
        bak_encryption_password: 备份加密密码
        dest_type: 备份策略的目标类型，当前支持OSS或NFS（默认为"NFS"）
        full: 全量备份计划，crontab格式，例如 0 0 * * 4,5
        inc: 增量备份计划，crontab格式，例如 0 0 * * 1,2,3
        job_keep_days: 保留备份作业的天数（默认为7）
        oss_access_id: OSS目标的访问ID
        oss_access_key: OSS目标的访问密钥
        recovery_days: 保留恢复作业的天数（默认为30）
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        cmd = f"okctl backup-policy create {tenant_name} -n {namespace}"

        # 添加可选参数
        if archive_path:
            cmd += f" --archive-path {archive_path}"
        if bak_data_path:
            cmd += f" --bak-data-path {bak_data_path}"
        if bak_encryption_password:
            cmd += f" --bak-encryption-password {bak_encryption_password}"
        if dest_type:
            cmd += f" --dest-type {dest_type}"
        if full:
            cmd += f" --full {full}"
        if inc:
            cmd += f" --inc {inc}"
        if job_keep_days is not None:
            cmd += f" --job-keep-days {job_keep_days}"
        if oss_access_id:
            cmd += f" --oss-access-id {oss_access_id}"
        if oss_access_key:
            cmd += f" --oss-access-key {oss_access_key}"
        if recovery_days is not None:
            cmd += f" --recovery-days {recovery_days}"

        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def delete_backup_policy(
    tenant_name: str, namespace: str = "default", force: bool = False
):
    """删除指定租户的备份策略

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        force: 强制删除租户备份策略
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        cmd = f"okctl backup-policy delete {tenant_name} -n {namespace}"
        if force:
            cmd += " -f"
        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def show_backup_policy(
    tenant_name: str,
    namespace: str = "default",
    job_type: str = "ALL",
    limit: Optional[int] = None,
):
    """查看指定租户的备份策略

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        job_type: 备份策略的作业类型，例如 FULL、INC、CLEAN、ARCHIVE、ALL（默认为"ALL"）
        limit: 查看的备份策略的作业数量
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        cmd = f"okctl backup-policy show {tenant_name} -n {namespace}"

        # 添加可选参数
        if job_type and job_type != "ALL":
            cmd += f" -t {job_type}"
        if limit is not None:
            cmd += f" --limit {limit}"

        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def pause_backup_policy(tenant_name: str, namespace: str = "default"):
    """暂停指定租户的备份策略

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        cmd = f"okctl backup-policy pause {tenant_name} -n {namespace}"
        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def resume_backup_policy(tenant_name: str, namespace: str = "default"):
    """恢复指定租户的备份策略

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        cmd = f"okctl backup-policy resume {tenant_name} -n {namespace}"
        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)


@mcp.tool()
def update_backup_policy(
    tenant_name: str,
    namespace: str = "default",
    full: Optional[str] = None,
    inc: Optional[str] = None,
    job_keep_days: Optional[int] = None,
    piece_interval_days: Optional[int] = None,
    recovery_days: Optional[int] = None,
):
    """更新指定租户的备份策略

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        full: 全量备份计划，crontab格式，例如 0 0 * * 4,5
        inc: 增量备份计划，crontab格式，例如 0 0 * * 1,2,3
        job_keep_days: 保留备份作业的天数（默认为7）
        piece_interval_days: 切换备份片段的天数（默认为1）
        recovery_days: 保留备份恢复的天数（默认为30）
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        cmd = f"okctl backup-policy update {tenant_name} -n {namespace}"

        # 添加可选参数
        if full:
            cmd += f" --full {full}"
        if inc:
            cmd += f" --inc {inc}"
        if job_keep_days is not None:
            cmd += f" --job-keep-days {job_keep_days}"
        if piece_interval_days is not None:
            cmd += f" --piece-interval-days {piece_interval_days}"
        if recovery_days is not None:
            cmd += f" --recovery-days {recovery_days}"

        result = subprocess.run(
            ["sh", "-c", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return format_error(e)
