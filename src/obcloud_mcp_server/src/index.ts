import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { mockLogin } from "./functions/login";
import { CONFIG } from "./env";
import { setUpResources } from "./resources";
import { setUpTools } from "./tools";
import { setUpPrompts } from "./prompts";

const server = new Server(CONFIG.server, {
  capabilities: {
    prompts: {},
    tools: {},
    resources: { suscribe: true, },
    logging: {
      level: 'info',
    }
  }
});

if (!CONFIG.auth.project) {
  throw new Error('project is required!');
}

if (!CONFIG.auth.username) {
  throw new Error('username is required!');
}

if (!CONFIG.auth.password) {
  throw new Error('password is required!');
}

async function runServer() {
  const transport = new StdioServerTransport();
  await mockLogin();
  
  setUpResources(server);
  setUpTools(server);
  setUpPrompts(server);

  await server.connect(transport);
}

runServer().catch((error: unknown) => {
  console.error("Server error:", error);
  process.exit(1);
});
