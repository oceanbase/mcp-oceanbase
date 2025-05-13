import { LOGIN_API, REFERER_URL } from "../constants";
import { CONFIG } from "../env";
import rsa from "../util";
import { client } from "./request";

const getPublicKey = async () => {
  const result = await client.get(
    `${LOGIN_API}/webapi/aciamweb/config/publicKey`,
    {
      headers: {
        Referer: REFERER_URL,
      },
      withCredentials: true,
    }
  );
  return result.data?.data;
};

export const mockLogin = async () => {
  const publicKey = await getPublicKey();
  const pwd = rsa(CONFIG.auth.password as string, publicKey);

  const loginRes = await client.post(
    `${LOGIN_API}/webapi/aciamweb/login/publicLogin`,
    {
      passAccountName: CONFIG.auth.username,
      password: pwd,
    },
    {
      headers: {
        Referer: REFERER_URL,
      },
      withCredentials: true,
    }
  );
};