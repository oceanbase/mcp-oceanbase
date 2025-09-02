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

## Install from PyPI Repository

### Install the Python package manager uv and create virtual environment
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
```
### If the dependency packages cannot be downloaded via uv due to network issues, you can change the mirror source to the Alibaba Cloud mirror source.
```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```
### Install OceanBase MCP Server
```bash
uv pip install oceanbase-mcp
```
## Configuration
There are two ways to configure the connection information of OceanBase
1. Set the following environment variables:

```bash
export OB_HOST=localhost     # Database host
export OB_PORT=2881         # Optional: Database port (defaults to 2881 if not specified)
export OB_USER=your_username
export OB_PASSWORD=your_password
export OB_DATABASE=your_database
```
2. Configure in the .env file
Create an .env file in the directory where the OceanBase MCP Server command is executed, and fill in the following information
OB_HOST=localhost     # Database host
OB_PORT=2881         # Optional: Database port (defaults to 2881 if not specified)
OB_USER=your_username
OB_PASSWORD=your_password
OB_DATABASE=your_database
## Usage

### stdio Mode

Add the following content to the configuration file that supports the MCP server client:

```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "uvx",
      "args": [
        "oceanbase-mcp"
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
### sse Mode
Within the mcp-oceanbase directory, execute the following command, the port can be customized as desired.<br>
'--transport': MCP server transport type as stdio or sse, default is stdio<br>
'--host': sse Host to bind to, default is 127.0.0.1, that is to say, you can only access it on your local computer. If you want any remote client to be able to access it, you can set the host to 0.0.0.0<br>
'--port': sse port to listen on, default is 8000
```bash
oceanbase_mcp_server --transport sse --port 8000
```
The URL address for the general SSE mode configuration is `http://ip:port/sse`

### 🧠 AI Memory System

**Experimental Feature**: Transform your AI assistant with persistent vector-based memory powered by OceanBase's advanced vector capabilities.

The memory system enables your AI to maintain continuous context across conversations, eliminating the need to repeat personal preferences and information. Four intelligent tools work together to create a seamless memory experience:

- **`ob_memory_query`** - Semantically search and retrieve contextual memories
- **`ob_memory_insert`** - Automatically capture and store important conversations  
- **`ob_memory_delete`** - Remove outdated or unwanted memories
- **`ob_memory_update`** - Evolve memories with new information over time

#### 🚀 Quick Setup

Memory tools are **disabled by default** to avoid the initial embedding model download (0.5~4 GiB). Install extra dependences are necessary.

```
cd mcp-oceanbase/src/oceanbase_mcp_server
uv sync --extra memory
```

Enable intelligent memory with these environment variables:

```bash
ENABLE_MEMORY=1  # default 0 disabled， set 1 to enable
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5 # default BAAI/bge-small-en-v1.5, You can set BAAI/bge-m3 or other models to get better experience.
EMBEDDING_MODEL_PROVIDER=huggingface
```

#### 📋 Prerequisites

**Vector Support**: Requires OceanBase v4.3.5.3+ (vector features enabled by default)

```bash
sudo docker run -p 2881:2881 --name obvector -e MODE=mini -d oceanbase/oceanbase-ce:4.3.5.3-103000092025080818
```

**Legacy Versions**: For older OceanBase versions, manually configure [ob_vector_memory_limit_percentage](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000003381620).

#### 💡 Usage Example

Experience the power of cross-session intelligent memory:

```
📅 Monday Conversation
User: "I love football and basketball, but I don't like swimming. I work in Shanghai using Python."
AI: "Got it! I've saved your preferences and work information!" 
    💾 [Automatically calls ob_memory_insert to save preference data]

📅 Wednesday Conversation  
User: "Recommend some sports I might be interested in"
AI: 🔍 [Automatically calls ob_memory_query searching "sports preferences"]
    "Based on your previous preferences, I recommend football and basketball activities! 
     Since you mentioned not liking swimming, here are some great land-based sports..."

📅 One Week Later
User: "Where do I work and what programming language do I use?"  
AI: 🔍 [Automatically calls ob_memory_query searching "work programming"]
    "You work in Shanghai and primarily use Python for development."
```

**🎯 Memory System Benefits**:
- ✅ **Cross-Session Continuity** - No need to reintroduce yourself
- ✅ **Intelligent Semantic Search** - Understands related concepts and context  
- ✅ **Personalized Experience** - AI truly "knows" your preferences
- ✅ **Automatic Capture** - Important information saved without manual effort

## Security Considerations

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

