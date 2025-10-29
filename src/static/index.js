import { generateRandomString, sha256, base64encode } from "./util.js";

const codeVerifier = generateRandomString(64);
const hashed = await sha256(codeVerifier);
const codeChallenge = base64encode(hashed);
