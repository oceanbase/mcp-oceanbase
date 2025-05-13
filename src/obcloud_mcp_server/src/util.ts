import NodeRSA from "node-rsa";

export default function rsa(pwd: string, publicKey: string) {
  if (!pwd || typeof pwd !== "string") {
    return "";
  }

  const pk = `-----BEGIN PUBLIC KEY-----
${publicKey}
-----END PUBLIC KEY-----`;

  const encryptor = new NodeRSA(pk);
  encryptor.setOptions({
    encryptionScheme: "pkcs1", // 加密方式（与 JSEncrypt 一致）
  });

  const encrypted = encryptor.encrypt(pwd, "base64");

  return encrypted;
}
