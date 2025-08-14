
<p align="center">
  <a href="https://github.com/oceanbase/oceanbase/blob/master/LICENSE">
    <img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-blue" />
  </a>
</p>

[English](README.md) | 简体中文
# obshell-mcp

由 [OceanBase 社区](https://open.oceanbase.com/) 提供的 obshell MCP server。

## 快速开始
1. 安装 uv（Python 包管理器），安装方法见 uv 的[仓库](https://github.com/astral-sh/uv)。
2. 运行 `uvx obshell-mcp` 启动 MCP 服务器。

### Cursor
在 Cursor -> Preferences -> Cursor Settings -> MCP -> Add new global MCP Server 中添加如下配置：

```bash
{
  "mcpServers": {
    "obshell-mcp": {
      "command": "uvx",
      "args": [
        "obshell-mcp",
      ],
    }
  }
}
```

如果希望以 SSE（Server-Sent Events）方式启动服务，可添加如下配置：

```bash
{
  "mcpServers": {
    "obshell-mcp": {
      "command": "uvx",
      "args": [
        "obshell-mcp",
        "--sse",
        "8000"
      ],
    }
  }
}
```

### 环境变量
可配置的环境变量如下：
| 变量 | 说明 | 默认值 |
|----------|-------------|---------------|
| OBSHELL_HOST | obshell 服务的主机地址 | 127.0.0.1 |
| OBSHELL_PORT | obshell 服务的端口 | 2886 |
| CLUSTER_NAME | OB 集群名称 | cluster |
| SYS_PASSWORD | sys 租户 root 用户的密码 | password |

## 参与贡献

欢迎通过 Issue 和 Pull Request 改进该项目。

## 许可证

更多信息参见 [LICENSE](LICENSE)。

