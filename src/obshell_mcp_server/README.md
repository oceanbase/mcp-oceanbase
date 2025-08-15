<p align="center">
  <a href="https://github.com/oceanbase/oceanbase/blob/master/LICENSE">
    <img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-blue" />
  </a>
</p>

English | [Chinese](README_CN.md)

# obshell-mcp

A MCP server for obshell provided by the [OceanBase Community](https://open.oceanbase.com/).

## Quick Start
1. Install uv (Python package manager), see the uv [repo](https://github.com/astral-sh/uv) for install methods.
2. `uvx obshell-mcp` to start the mcp server.

### cursor
Go to Cursor -> Preferences -> Cursor Settings -> MCP -> Add new global MCP Server to include the following configuration:

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
or if you want to start the server with sse, you can add the following configuration:

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

### Environment Variables
The following environment variables can be configured:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| OBSHELL_HOST | The host of the obshell server | 127.0.0.1 |
| OBSHELL_PORT | The port of the obshell server | 2886 |
| CLUSTER_NAME | The name of the obcluster | cluster |
| SYS_PASSWORD | The password of the root user of sys tenant| password |

## Contributing

Issues and Pull Requests are welcome to improve this project.

## License

See [LICENSE](LICENSE) for more information.
