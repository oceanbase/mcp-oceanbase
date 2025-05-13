import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { GetPromptRequestSchema, ListPromptsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

export const setUpPrompts = (server: Server) => {
  server.setRequestHandler(ListPromptsRequestSchema, () => ({
    prompts: [{
      name: "obcloud-workflow",
      description: "obcloud 操作的工作流",
      arguments: [],
    }]
  }))

  server.setRequestHandler(GetPromptRequestSchema, (request) => {
    const { name, arguments: args } = request.params;
    switch (name) {
      case 'obcloud-workflow':
        return {
          messages: [
            {
              role: "assistant",
              content: {
                type: "text",
                text: `用中文回答，引导用户:
                1.检查是否存在 instances 资源，如果不存在，尝试请求资源后展示。
                2.让用户选择某一个实例。
                3.列出该实例下所有的租户。
                4.让用户选择某一个租户。
                5.尝试对租户进行诊断
                6.列出该实例下所有的数据库。
                7.让用户选择某一个数据库。
                8.让用户输入数据库连接的账号和密码后，尝试连接数据库
                `,
              },
            },
          ],
        }
      default:
        throw new Error(`Unknown prompt:${name}`);
    }

  })
};