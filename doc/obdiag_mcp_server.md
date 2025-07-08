# mcp-oceanbase

MCP Server for OBDiag (OceanBase Diagnostic Tool).

English | [简体中文](obdiag_mcp_server_CN.md)

## Usage

To use with the MCP Client, it is necessary to utilize a client that supports Prompt, such as Claude Desktop. Before entering a request, you need to manually select the desired Prompt and then input your request.

Claude Desktop config example:

```json
{
  "mcpServers": {
    "obdiag": {
      "url": "http://{host}:8000/mcp"
    }
  }
}
```

## Supporting Multiple MCP Types

You can start the obdiag mcp with different protocols using the following commands:

```shell
cd src/obdiag_mcp_server
python server.py stdio # stdio mode
python server.py sse # sse mode, default port 8000
python server.py sse 8001 # sse mode, specify port 8001
python server.py streamable-http # streamable-http mode, default port 8000
python server.py streamable-http 8001 # streamable-http mode, specify port 8001
```


## Prerequisites

Before using the OBDiag MCP Server, ensure that:

1. **OBDiag is installed**: The server requires OBDiag to be installed and accessible via the `obdiag` command.
2. **Configuration file exists**: The OBDiag configuration file should be present at `~/.obdiag/config.yml`.

## Available Tools

The OBDiag MCP Server provides the following diagnostic tools:

- **obdiag_check_run**: Performs cluster inspection and returns inspection reports
- **obdiag_analyze_log**: Analyzes cluster logs to identify error messages
- **obdiag_display_list**: Queries available diagnostic commands and returns the list of supported commands
- **obdiag_display_run**: Executes specific diagnostic commands with optional environment variables

## Community

Don't hesitate to ask!

Contact the developers and community at [https://ask.oceanbase.com](https://ask.oceanbase.com) if you need any help.

[Open an issue](https://github.com/oceanbase/mcp-oceanbase/issues) if you found a bug.

## Licensing

See [LICENSE](../LICENSE) for more information. 