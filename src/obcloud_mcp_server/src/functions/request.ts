import { HttpCookieAgent, HttpsCookieAgent } from "http-cookie-agent/http";
import { CookieJar } from "tough-cookie";
import axios from "axios";
import { REFERER_URL } from "../constants";
import { CONFIG } from "../env";

const jar = new CookieJar();
export const client = axios.create({
  httpAgent: new HttpCookieAgent({ cookies: { jar } }),
  httpsAgent: new HttpsCookieAgent({
    cookies: { jar },
    rejectUnauthorized: false,
  }),
  withCredentials: true,
  headers: {
    Referer: REFERER_URL,
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN",
    ["X-Ob-Project-Id"]: CONFIG.auth.project,
  },
});
