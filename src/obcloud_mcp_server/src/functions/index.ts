import * as mysql2 from "mysql2/promise";
import { Pool } from "mysql2/promise";
import { CONSOLE_API } from "../constants";
import { client } from "./request";

let pool: Pool | undefined;

export const listInstances = async (): Promise<OB.Instance[]> => {
  try {
    const response = await client.get(
      `${CONSOLE_API}/api/v2/instances?requestId=mcp-request&Action=DescribeInstances`,
      { data: { pageSize: 99 } }
    );

    return response.data?.data?.dataList;
  } catch (error) {
    throw error;
  }
};

export const listTenants = async ({ instanceId }: { instanceId: string }) => {
  const response = await client.get(
    `${CONSOLE_API}/api/v2/instances/${instanceId}/tenants?requestId=mcp-request&Action=DescribeTenants`
  );
  return response.data?.data?.dataList;
};

export const listDatabases = async ({
  instanceId,
  tenantId,
}: {
  instanceId: string;
  tenantId: string;
}) => {
  const response = await client.get(
    `${CONSOLE_API}/api/v2/instances/${instanceId}/tenants/${tenantId}/databases?requestId=mcp-request&Action=DescribeDatabases`
  );
  return response.data?.data?.dataList;
};

export const getPublicAddress = async ({
  instanceId,
  tenantId,
}: {
  instanceId: string;
  tenantId: string;
}) => {
  const response = await client.get(
    `${CONSOLE_API}/api/v2/instances/${instanceId}/tenants/${tenantId}/publicaddress?requestId=mcp-request&Action=DescribeTenantPublicAddress`
  );
  return response.data.data ?? {};
};

export const connect = async ({
  instanceId,
  tenantId,
  user,
  password,
  database,
}: {
  instanceId: string;
  tenantId: string;
  user: string;
  password: string;
  database: string;
}) => {
  try {
    const address = await getPublicAddress({ instanceId, tenantId });
    const host = address?.internetDomain;
    const port = address?.internetPort;

    pool = mysql2.createPool({
      host,
      port,
      user,
      password,
      database,
    });

    await pool.getConnection();

    return {
      content: [
        {
          type: "text",
          text: "连接成功",
        },
      ],
      isError: false,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${errorMessage}` }],
      isError: true,
    };
  }
};

export async function executeQuery(sql: string) {
  if (pool) {
    const connection = await pool.getConnection();
    try {
      const result = await connection.query(sql);
      const rows = Array.isArray(result) ? result[0] : result;
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(rows, null, 2),
          },
        ],
        isError: false,
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    } finally {
      connection.release();
    }
  } else {
    return {
      content: [{ type: "text", text: `Error: 需要完成数据库连接` }],
      isError: true,
    };
  }
}

const getTopSql = async ({
  instanceId,
  tenantId,
  start,
  end,
}: {
  instanceId: string;
  tenantId: string;
  start: string;
  end: string;
}) => {
  const topSqlResponse = await client.get(
    `${CONSOLE_API}/api/v2/instances/${instanceId}/tenants/${tenantId}/topSql?requestId=29800c68-5464-47f8-add6-a010adb5ee08&Action=DescribeOasTopSQLList&startTime=${start}&endTime=${end}&mergeDynamicSql=false`
  );
  return topSqlResponse.data;
};

const getSlowSql = async ({
  instanceId,
  tenantId,
  start,
  end,
}: {
  instanceId: string;
  tenantId: string;
  start: string;
  end: string;
}) => {
  const slowSqlResponse = await client.get(
    `${CONSOLE_API}/api/v2/instances/${instanceId}/tenants/${tenantId}/slowSql?requestId=29800c68-5464-47f8-add6-a010adb5ee08&Action=DescribeOasSlowSQLList&startTime=${start}&endTime=${end}&mergeDynamicSql=false`
  );
  return slowSqlResponse.data;
};

const getMetrics = async ({
  instanceId,
  tenantId,
  start,
  end,
}: {
  instanceId: string;
  tenantId: string;
  start: string;
  end: string;
}) => {
  const metricsResponse = await client.post(
    `${CONSOLE_API}/api/v2/services/DescribeMetricsData?requestId=d6a73fc2-bdf3-41fb-8cbf-951501f5fb26&Action=DescribeMetricsData`,
    {
      StartTime: start,
      EndTime: end,
      Metrics:
        "sql_all_count,sql_delete_count,sql_insert_count,sql_other_count,sql_replace_count,sql_select_count,sql_update_count",
      labels: `clusterId:${instanceId},tenantId:${tenantId}`,
      GroupByLabels: "clusterId,tenantId",
      InstanceId: instanceId,
    }
  );

  return metricsResponse.data;
};

export const diagnostics = async ({
  instanceId,
  tenantId,
  start,
  end,
}: {
  instanceId: string;
  tenantId: string;
  start: string;
  end: string;
}) => {
  const metrics = await getMetrics({ instanceId, tenantId, start, end });
  const topSql = await getTopSql({ instanceId, tenantId, start, end });
  const slowSql = await getSlowSql({ instanceId, tenantId, start, end });

  return { metrics, topSql, slowSql };
};
