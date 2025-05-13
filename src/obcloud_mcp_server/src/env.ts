import dotenv from 'dotenv';
dotenv.config();

export const CONFIG = {
  server: { name: 'oceanbase-mcp-server', version: '1.0.0' },
  auth: {
    project: process.env.project,
    username: process.env.username,
    password: process.env.password
  }
}