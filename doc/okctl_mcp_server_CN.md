# OceanBase Kubernetes 控制工具 (okctl) MCP 服务器

[English](okctl_mcp-server.md) | 简体中文

## 项目简介

本项目是 OceanBase Kubernetes 控制工具 ([okctl](https://github.com/oceanbase/ob-operator?tab=readme-ov-file#using-cli-tool-okctl)) 的 MCP 服务器实现，提供了一系列工具函数，用于管理 OceanBase 集群、租户和备份策略等。这些函数通过调用底层的 okctl 命令行工具来实现各种管理操作，并通过 MCP 协议将这些功能暴露给客户端。

## 功能模块

本项目包含以下主要 tools：

### 1. 集群管理 (clusters.py)

提供了创建、删除、查看、扩缩容、更新和升级 OceanBase 集群的功能。

- `list_all_clusters()` - 列出所有 OceanBase 集群
- `show_cluster()` - 显示指定集群的详细信息
- `create_cluster()` - 创建新的 OceanBase 集群
- `delete_cluster()` - 删除指定的 OceanBase 集群
- `scale_cluster()` - 扩缩 OceanBase 集群
- `update_cluster()` - 更新 OceanBase 集群配置
- `upgrade_cluster()` - 升级 OceanBase 集群版本

### 2. 租户管理 (tenants.py)

提供了创建、删除、查看、扩缩容、更新和管理 OceanBase 租户的功能。

- `list_tenants()` - 列出所有租户
- `create_tenant()` - 创建新的租户
- `delete_tenant()` - 删除指定的租户
- `show_tenant()` - 显示租户详细信息
- `scale_tenant()` - 扩缩租户资源
- `update_tenant()` - 更新租户配置
- `upgrade_tenant()` - 升级租户版本
- `change_tenant_password()` - 修改租户密码
- `activate_tenant()` - 激活备用租户
- `replay_tenant_log()` - 回放租户日志
- `switchover_tenant()` - 切换主备租户

### 3. 备份策略管理 (backup_policy.py)

提供了创建、删除、查看、更新和管理 OceanBase 备份策略的功能。

- `list_backup_policies()` - 列出所有备份策略
- `create_backup_policy()` - 创建新的备份策略
- `delete_backup_policy()` - 删除指定的备份策略
- `show_backup_policy()` - 显示备份策略详细信息
- `update_backup_policy()` - 更新备份策略
- `pause_backup_policy()` - 暂停备份策略
- `resume_backup_policy()` - 恢复备份策略

### 4. SQL操作 (sql.py)

提供了配置数据库连接和在OceanBase集群上执行SQL查询的功能。

- `configure_cluster_connection()` - 配置到集群的数据库连接
  - 参数：cluster_name（集群名称）, tenant_name（租户名称，默认为sys）, namespace（命名空间，默认为"default"）, user（用户名）, password（密码，如果未提供，则从环境变量 OB_CLUSTER_PASSWORD 中获取集群密码）, port（端口，默认为2881）
  - 返回：数据库连接配置信息
  
- `execute_cluster_sql()` - 在集群上执行SQL查询
  - 参数：query（查询语句）, cluster_name（集群名称，可选）, tenant_name（租户名称，默认为sys）, database（数据库名称，默认为oceanbase，也可以为业务数据库）, namespace（命名空间，默认为"default"）
  - 返回：查询结果
  - 支持各种SQL命令，包括SELECT、SHOW TABLES、SHOW COLUMNS、DESCRIBE和DML语句

### 5. 组件管理 (components.py)

提供了安装、更新和管理 OceanBase 组件的功能。

- `list_components()` - 列出所有已安装的组件
- `install_component()` - 安装新的组件
- `update_component()` - 更新组件

## 开发环境配置

### 前提条件

- 已安装 Python 3.10 或更高版本
- 已安装 uv 包管理工具（[uv 官方文档](https://github.com/astral-sh/uv)）
- 已安装并配置 OceanBase Kubernetes 控制工具 (okctl)
- 已配置 Kubernetes 环境，并有权限访问 OceanBase 集群

### 配置 MCP 服务器

```json
{
  "mcpServers": {
    "okctl": {
      "command": "uv",
      "args": ["--directory", "<path/to/mcp-oceanbase>", "run", "okctl_mcp_server"],
      "env": {
        // 如果想要用系统租户连接集群，默认访问root@sys, 需要配置以下参数
        "OB_CLUSTER_PASSWORD": "<password of cluster>"
      }
    }
  }
}
```

#### 命令行参数

以下是可选的命令行参数，例如，如果你只想启用集群管理工具，可以这样配置：

```bash
uv run --directory <path/to/mcp-oceanbase> okctl_mcp_server --tools=clusters
```

- `--tools`: 指定要启用的工具，用逗号分隔。选项：
  - `all`: 启用所有工具（默认）
  - `clusters`: 仅启用集群管理工具
  - `tenants`: 仅启用租户管理工具
  - `backup_policy`: 仅启用备份策略管理工具
  - `components`: 仅启用组件管理工具
  - `sql`: 仅启用SQL操作工具
  
  示例：`--tools=clusters,tenants,sql`

- `--use_sse`: 使用服务器发送事件（SSE）传输而不是标准输入输出
- `--port`: 指定SSE传输的端口（默认：8000）

## 注意事项

- 服务器需要在能够访问 Kubernetes 集群的环境中运行
- 所有函数都是通过调用底层的 okctl 命令行工具来实现的，因此需要确保 okctl 已正确安装并配置
- 大多数函数都提供了 namespace 参数，默认值为 "default"，可以根据需要指定不同的命名空间
- 部分操作（如删除集群、删除租户等）可能是不可逆的，请谨慎操作
- 目前在执行SQL语句时，需要提供较为精确的prompt，否则可能会返回错误
- 建议在执行重要操作前先进行备份

## 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个项目。

## 许可证

查看[LICENSE](../LICENSE)获取更多信息.
