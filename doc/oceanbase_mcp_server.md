# OceanBase MCP Server

A Model Context Protocol (MCP) server that enables secure interaction with OceanBase databases. 
This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled interface, making database exploration and analysis safer and more structured.

## Features

- List available OceanBase tables as resources
- Read table contents
- Execute SQL queries with proper error handling
- Secure database access through environment variables
- Comprehensive logging


## Configuration

Set the following environment variables:

```bash
OB_HOST=localhost     # Database host
OB_PORT=2881         # Optional: Database port (defaults to 2881 if not specified)
OB_USER=your_username
OB_PASSWORD=your_password
OB_DATABASE=your_database
```

## Usage

### With Claude Desktop

Add this to your `claude_desktop_config.json`:

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

### As a standalone server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m oceanbase_mcp_server
```

## Install & Development

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-oceanbase.git
cd mcp-oceanbase

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Copy and modify .env
cp .env.template .env

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
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

