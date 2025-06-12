# OceanBase MCP Server

A Model Context Protocol (MCP) server that enables secure interaction with OceanBase databases. 
This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled interface, making database exploration and analysis safer and more structured.

## Features

- List available OceanBase tables as resources
- Read table contents
- Execute SQL queries with proper error handling
- Secure database access through environment variables
- Comprehensive logging

## Tools
- [✔️] Execute SQL queries
- [✔️] Get current tenant
- [✔️] Get all server nodes (sys tenant only)
- [✔️] Get resource capacity (sys tenant only)
- [✔️] Get [ASH](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000002013776) report
- [✔️] Search OceanBase document from official website.
  This tool is experimental because the API on the official website may change.

## Install

### Clone the repository
```bash
git clone https://github.com/oceanbase/mcp-oceanbase.git
cd mcp-oceanbase
```
### Install the Python package manager uv and create virtual environment
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
```
### If you configure the OceanBase connection information using .env file. You should copy .env.template to .env and modify .env
```bash
cp .env.template .env
```
### If the dependency packages cannot be downloaded via UV due to network issues, you can change the mirror source to the Alibaba Cloud mirror source.
```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```
### Install dependencies
```bash
uv pip install .
```
## Configuration
There are two ways to configure the connection information of OceanBase
1. Set the following environment variables:

```bash
OB_HOST=localhost     # Database host
OB_PORT=2881         # Optional: Database port (defaults to 2881 if not specified)
OB_USER=your_username
OB_PASSWORD=your_password
OB_DATABASE=your_database
```
2. Configure in the .env file
## Usage

### Stdio Mode

Add the following content to the configuration file that supports the MCP server client:

```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "uv",
      "args": [
        "--directory", 
        "path/to/mcp-oceanbase",
        "run",
        "oceanbase_mcp_server"
      ],
      "env": {
        "OB_HOST": "localhost",
        "OB_PORT": "2881",
        "OB_USER": "your_username",
        "OB_PASSWORD": "your_password",
        "OB_DATABASE": "your_database"
      }
    }
  }
}
```
### SSE Mode
Within the mcp-oceanbase directory, execute the following command, the port can be customized as desired.<br>
'--transport': MCP server transport type as stdio or sse, default is stdio<br>
'--host': sse Host to bind to, default is 127.0.0.1, that is to say, you can only access it on your local computer. If you want any remote client to be able to access it, you can set the host to 0.0.0.0<br>
'--port': sse port to listen on, default is 8000
```bash
uv run oceanbase_mcp_server --transport sse --port 8000
```
If you don't want to use uv, you can start it in the following way
```bash
cd src/oceanbase_mcp_server/ && python3 -m server --transport sse --port 9000
```

## Security Considerations

- Never commit environment variables or credentials
- Use a database user with minimal required permissions
- Consider implementing query whitelisting for production use
- Monitor and log all database operations

## Security Best Practices

This MCP server requires database access to function. For security:

1. **Create a dedicated OceanBase user** with minimal permissions
2. **Never use root credentials** or administrative accounts
3. **Restrict database access** to only necessary operations
4. **Enable logging** for audit purposes
5. **Regular security reviews** of database access

See [OceanBase Security Configuration Guide](./SECURITY.md) for detailed instructions on:
- Creating a restricted OceanBase user
- Setting appropriate permissions
- Monitoring database access
- Security best practices

⚠️ IMPORTANT: Always follow the principle of least privilege when configuring database access.

## License

Apache License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

