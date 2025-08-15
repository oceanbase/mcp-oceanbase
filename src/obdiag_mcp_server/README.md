# OBDiag MCP Server

A Model Context Protocol (MCP) server that enables secure interaction with OBDiag (OceanBase Diagnostic Tool).

English | [简体中文](../doc/obdiag_mcp_server_CN.md)

## Overview

The OBDiag MCP Server provides a standardized interface for AI assistants to interact with OceanBase diagnostic tools through the Model Context Protocol. It allows you to perform cluster diagnostics, log analysis, and system health checks programmatically.

## Features

- **Cluster Inspection**: Perform comprehensive cluster health checks and generate inspection reports
- **Log Analysis**: Analyze cluster logs to identify error messages and performance issues
- **Scene-based Diagnostics**: Execute specific diagnostic scenarios with customizable parameters
- **Multiple Transport Protocols**: Support for stdio, SSE, and streamable-http transport modes
- **Easy Integration**: Simple setup and configuration for MCP-compatible clients

## Prerequisites

Before using the OBDiag MCP Server, ensure that:

1. **Python 3.11+**: The server requires Python 3.11 or higher
2. **OBDiag is installed**: The server requires OBDiag to be installed and accessible via the `obdiag` command
3. **Configuration file exists**: The OBDiag configuration file should be present at `~/.obdiag/config.yml`

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/oceanbase/mcp-oceanbase.git
cd mcp-oceanbase
```

2. Navigate to the obdiag MCP server directory:
```bash
cd src/obdiag_mcp_server
```

3. Install the package:
```bash
pip install -e .
```

### Using pip

```bash
pip install obdiag-mcp
```

## Usage

### Command Line

The server can be started with different transport protocols:

```bash
# stdio mode (for direct integration)
obdiag-mcp stdio

# SSE mode (default port 8000)
obdiag-mcp sse

# SSE mode with custom port
obdiag-mcp sse 8001

# streamable-http mode (default port 8000)
obdiag-mcp streamable-http

# streamable-http mode with custom port
obdiag-mcp streamable-http 8001
```

### MCP Client Configuration

To use with an MCP client (like Claude Desktop), configure your client:

```json
{
  "mcpServers": {
    "obdiag": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Available Tools

The OBDiag MCP Server provides the following diagnostic tools:

### obdiag_check_run
Performs cluster inspection and returns inspection reports.

**Usage**: No parameters required
**Returns**: Cluster inspection report

### obdiag_analyze_log
Analyzes cluster logs to identify error messages and performance issues.

**Usage**: No parameters required
**Returns**: Log analysis results

### obdiag_display_list
Queries available diagnostic commands and returns the list of supported commands.

**Usage**: No parameters required
**Returns**: List of available diagnostic scenes

### obdiag_display_run
Executes specific diagnostic commands with optional environment variables.

**Parameters**:
- `scene` (string): The diagnostic scene name from obdiag_display_list results
- `env_dict` (dict, optional): Environment variables for the diagnostic command

**Returns**: Diagnostic results for the specified scene

## Development

### Project Structure

```
obdiag_mcp_server/
├── __init__.py
├── server.py              # Main server implementation
├── tools/
│   ├── __init__.py
│   └── obdiag_tools.py    # OBDiag tool implementations
├── pyproject.toml         # Project configuration
├── LICENSE               # Apache 2.0 License
└── README.md             # This file
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Building

```bash
# Build the package
python -m build

# Install from built package
pip install dist/obdiag_mcp-*.whl
```

## Configuration

The server automatically checks for OBDiag configuration at `~/.obdiag/config.yml`. Ensure this file exists and contains valid OBDiag configuration.

Example configuration structure:
```yaml
# ~/.obdiag/config.yml
obdiag:
  basic:
    config_path: ~/.obdiag/config.yml
    log_path: ~/.obdiag/log
  cluster:
    # Your cluster configuration here
```

## Troubleshooting

### Common Issues

1. **"obdiag is not installed"**
   - Ensure OBDiag is installed and accessible via the `obdiag` command
   - Check your PATH environment variable

2. **"obdiag config is not exist"**
   - Create the configuration file at `~/.obdiag/config.yml`
   - Ensure the file contains valid YAML configuration

3. **Connection refused errors**
   - Check if the specified port is available
   - Ensure firewall settings allow the connection

### Logs

The server outputs diagnostic information to stdout. For detailed OBDiag logs, check the `~/.obdiag/log` directory.

## Contributing

We welcome contributions! Please see our [Contributing Guide](../../CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Community

Don't hesitate to ask for help!

- **Community Forum**: [https://ask.oceanbase.com](https://ask.oceanbase.com)
- **GitHub Issues**: [https://github.com/oceanbase/mcp-oceanbase/issues](https://github.com/oceanbase/mcp-oceanbase/issues)
- **Documentation**: [https://www.oceanbase.com/docs](https://www.oceanbase.com/docs)

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

## Related Projects

- [OBDiag](https://github.com/oceanbase/obdiag) - OceanBase Diagnostic Tool
- [OceanBase](https://github.com/oceanbase/oceanbase) - Distributed relational database
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

