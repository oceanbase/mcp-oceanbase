[English](oceanbase_mcp_server.md) | 简体中文<br>
# OceanBase MCP Server

OceanBase MCP Server 通过 MCP (模型上下文协议) 可以和 OceanBase 进行交互。
使用支持 MCP 的客户端，连接上 OB 数据库，可以列出所有的表、读取数据以及执行 SQL，然后可以使用大模型对数据库中的数据进一步分析。


## 特性

- 列出所有 OceanBase 数据库中的表作为资源
- 读取表中的数据
- 执行 SQL 语句
- 通过环境变量访问数据库
- 全面的日志记录

## 工具
- [✔️] 执行 SQL 语句
- [✔️] 查询当前租户
- [✔️] 查询所有的 server 节点信息 （仅支持 sys 租户）
- [✔️] 查询资源信息 （仅支持 sys 租户）
- [✔️] 查询 [ASH](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000002013776) 报告
- [✔️] 搜索 OceanBase 官网的文档。
  这个工具是实验性质的，因为官网的 API 接口可能会变化。

## 安装

### 克隆仓库
```bash
git clone https://github.com/oceanbase/mcp-oceanbase.git
cd mcp-oceanbase/src/oceanbase_mcp_server
```
### 安装 Python 包管理器 uv 并创建虚拟环境
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # 在Windows系统上执行 `.venv\Scripts\activate`
```
### 如果使用 .env 文件配置 OceanBase 的连接信息，需要复制 .env.template 文件为 .env，然后修改 .env 文件
```bash
cp .env.template .env
```
### 如果因为网络问题 uv 下载文件较慢或者无法下载，可以使用阿里云的镜像源
```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```
### 安装依赖
```bash
uv pip install .
```
## 配置
有两种方式可以配置 OceanBase 的连接信息
1. 在环境变量中设置以下变量的值：
```bash
OB_HOST=localhost     # 数据库的地址
OB_PORT=2881         # 可选的数据库的端口（如果没有配置，默认是2881)
OB_USER=your_username
OB_PASSWORD=your_password
OB_DATABASE=your_database
```
2. 在 .env 文件中进行配置
## 使用方法

### stdio 模式
在支持 MCP 的客户端中，将下面的内容填入配置文件，请根据实际信息修改
```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "uv",
      "args": [
        "--directory", 
        "path/to/mcp-oceanbase/src/oceanbase_mcp_server",
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
### sse 模式
在 mcp-oceanbase/src/oceanbase_mcp_server 目录下，执行下面的命令，端口号是可配置的。<br>
'--transport'： MCP 的传输模式，stdio 或者 sse，默认是 stdio<br>
'--host'： sse 模式绑定的 host，默认是 127.0.0.1，也就是只能本机访问，如果需要远程访问，可以设置为 0.0.0.0<br>
'--port'： sse 模式监听的端口，默认是 8000
```bash
uv run oceanbase_mcp_server --transport sse --port 8000
```
如果不想使用 uv，也可以用下面的方式启动
```bash
cd oceanbase_mcp/ && python3 -m server --transport sse --port 8000
```
sse 模式访问地址示例： `http://ip:port/sse`

## 安全注意事项
- 不要提交环境变量信息或者凭证
- 使用最小权限的数据库用户
- 对于生产环境，考虑设置查询白名单
- 监控并记录所有的数据库操作

## 安全最佳实践
MCP 中的工具会访问数据库，为了安全：
1. **创建一个专用的 OceanBase 用户**，拥有最小的权限
2. **不要使用 root 用户**
3. **限制数据库的操作**，只运行必要的操作
4. **开启日志记录**，以便进行审计
5. **进行数据库访问的日常巡检**

## 许可证

Apache License - 查看 LICENSE 文件获取细节。

## 贡献

1. Fork 这个仓库
2. 创建你自己的分支 （`git checkout -b feature/amazing-feature`）
3. 提交修改 （`git commit -m 'Add some amazing feature'`）
4. 推送到远程仓库 （`git push origin feature/amazing-feature`）
5. 提交 PR