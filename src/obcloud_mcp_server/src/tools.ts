import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import {
  connect,
  diagnostics,
  executeQuery,
  listDatabases,
  listInstances,
  listTenants,
} from "./functions";
import { instances } from "./resources";
import dayjs from "dayjs";

export const setUpTools = (server: Server) => {
  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "list_instances",
        description: "list oceanbase instances",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "list_tenants",
        description: "describe tenants by instance id",
        inputSchema: {
          type: "object",
          properties: {
            instanceId: { type: "string", require: true },
          },
        },
      },
      {
        name: "list_databases",
        description: "describe databases by teant id",
        inputSchema: {
          type: "object",
          properties: {
            instanceId: { type: "string", require: true },
            tenantId: { type: "string", require: true },
          },
        },
      },
      {
        name: "connect",
        description: "create connection to oceanbase database",
        inputSchema: {
          type: "object",
          properties: {
            instanceId: { type: "string", require: true },
            tenantId: { type: "string", require: true },
            database: { type: "string", require: true },
            user: { type: "string", require: true },
            password: { type: "string", require: true },
          },
        },
      },
      {
        name: "diagnostics",
        description: "Diagnose the operational status of a tenant",
        inputSchema: {
          type: "object",
          properties: {
            instanceId: { type: "string", require: true },
            tenantId: { type: "string", require: true },
            start: {
              type: "string",
              description:
                "Start time of the diagnostic task. If not provided, the default is one hour ago. Time format: YYYY-MM-DDTHH:mm:ss",
            },
            end: {
              type: "string",
              description:
                "End time of the diagnostic task. If not provided, the default is the current time. Time format: YYYY-MM-DDTHH:mm:ss",
            },
          },
        },
      },
      {
        name: "query",
        description: "query infos from tenant's database by sql",
        inputSchema: {
          type: "object",
          properties: {
            sql: { type: "string", require: true },
          },
        },
      },
    ],
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
      const { name, arguments: args } = request.params;
      switch (name) {
        case "query":
          const sql = request.params.arguments?.sql as string;
          return executeQuery(sql);
        case "connect":
          return connect(
            {
              tenantId: args?.tenantId as string,
              instanceId: args?.instanceId as string,
              database: args?.database as string,
              user: args?.user as string,
              password: args?.password as string,
            },
          );
        case "list_instances":
          const data = await listInstances();

          data.forEach((instance) => {
            instances.set(instance.instanceId, instance);
          });

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  data.map((instance) => ({
                    id: instance.instanceId,
                    name: instance.instanceName,
                    status: instance.status,
                  }))
                ),
              },
            ],
          };
        case "list_tenants":
          const tenants = await listTenants({
            instanceId: args?.instanceId as string,
          });
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(tenants),
              },
            ],
          };
        case "list_databases":
          const databases = await listDatabases({
            instanceId: args?.instanceId as string,
            tenantId: args?.tenantId as string,
          });
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(databases),
              },
            ],
          };
        case "diagnostics":
          const start =
            (args?.start as string) ??
            dayjs().subtract(9, "hour").format("YYYY-MM-DDTHH:mm:ss") + "Z";
          const end =
            (args?.start as string) ?? dayjs().subtract(8, "hour").format("YYYY-MM-DDTHH:mm:ss") + "Z";

          const result = await diagnostics({
            tenantId: args?.tenantId as string,
            instanceId: args?.instanceId as string,
            start,
            end,
          });

          return {
            content: [{ type: "text", text: JSON.stringify(result) }],
          };
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  });
};
