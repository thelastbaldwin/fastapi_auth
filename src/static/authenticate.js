// https://developer.spotify.com/documentation/web-api/tutorials/code-pkce-flow
import { generateRandomString, sha256, base64encode } from "./util";

const codeVerifier = generateRandomString(64);
const searchParams = new URLSearchParams(window.location.search);

const clientId = searchParams.get("client_id");
const redirectUri = searchParams.get("redirect_uri");

// unused by leaving as a placeholder when clients are supported
const scope = "user-read-private user-read-email";

window.localStorage.setItem("code_verifier", codeVerifier);

const hashed = await sha256(codeVerifier);
const codeChallenge = base64encode(hashed);

const params = {
  response_type: "code",
  client_id: clientId,
  scope,
  code_challenge_method: "S256",
  code_challenge: codeChallenge,
  redirect_uri: redirectUri,
};

const authUrl = new URL("localhost://8000/authenticate");
authUrl.search = new URLSearchParams(params).toString();
window.location.href = authUrl.toString();
