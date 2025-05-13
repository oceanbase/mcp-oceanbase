import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { ListResourcesRequestSchema, ListResourceTemplatesRequestSchema, ReadResourceRequestSchema } from "@modelcontextprotocol/sdk/types.js";

export const instances = new Map<string, OB.Instance>();

export const setUpResources = (server: Server) => {

  server.setRequestHandler(ListResourceTemplatesRequestSchema, async () => {
    return {
      resourceTemplates: [
        {
          uriTemplate: "instance://{id}",
          name: "oceanbase instance",
          description: "A oceanbase instance with a id",
        },
      ],
    };
  });

  server.setRequestHandler(ListResourcesRequestSchema, async () => {
    return {
      resources: [
        ...Array.from(instances.keys()).map(id => ({
          uri: `instance://${id}`,
          mimeType: 'text',
          name: instances.get(id)?.instanceName,
          text: JSON.stringify(instances.get(id) ?? '')
        }))
      ]
    }
  });

  server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    const uri = request.params.uri.toString();
  
    if (uri.startsWith('instance')) {
      const id = request.params.uri.replace("instance://", "");
      return {
        contents: [{
          uri,
          mimeType: 'text',
          name: instances.get(id)?.instanceName,
          text: JSON.stringify(instances.get(id))
        }]
      }
    }
    throw new Error(`Unknown resource: ${name}`);
  });
}
