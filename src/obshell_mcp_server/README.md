<p align="center">
  <a href="https://github.com/oceanbase/oceanbase/blob/master/LICENSE">
    <img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-blue" />
  </a>
</p>


# obshell-mcp

A MCP server for obshell provided by the [OceanBase Community](https://open.oceanbase.com/).

## Quick Start
1. Install uv (Python package manager), see the uv [repo](https://github.com/astral-sh/uv) for install methods.
2. `uvx obshell-mcp --sse 8000` to start the mcp server.

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

## Contributing

Issues and Pull Requests are welcome to improve this project.

## License

See [LICENSE](LICENSE) for more information.
