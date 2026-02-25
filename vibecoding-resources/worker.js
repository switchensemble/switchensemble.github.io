/**
 * Cloudflare Worker OAuth proxy for Decap CMS (GitHub backend)
 *
 * Expected Decap config:
 *   backend:
 *     name: github
 *     repo: switchensemble/switchensemble.github.io
 *     branch: master
 *     base_url: https://www.switchensemble.com
 *     auth_endpoint: /auth
 *
 * Worker routes (Cloudflare Workers → Domains & Routes):
 *   https://www.switchensemble.com/auth*
 *   https://www.switchensemble.com/callback*
 *   https://www.switchensemble.com/health*
 *
 * Secrets:
 *   GITHUB_CLIENT_ID      (secret)
 *   GITHUB_CLIENT_SECRET  (secret)
 *
 * Variables (text):
 *   CMS_ORIGIN   = https://www.switchensemble.com
 *   CALLBACK_URL = https://www.switchensemble.com/callback
 */

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers },
  });
}

function html(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: { "content-type": "text/html; charset=utf-8", ...headers },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    const CMS_ORIGIN = (env.CMS_ORIGIN || "https://www.switchensemble.com").replace(/\/+$/, "");
    const CALLBACK_URL = (env.CALLBACK_URL || `${CMS_ORIGIN}/callback`).replace(/\/+$/, "");

    // --- Healthcheck (for quick sanity checks) ---
    if (path === "/health") {
      return new Response("ok", { status: 200, headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    // --- Step 1: Redirect to GitHub authorize ---
    if (path === "/auth") {
      const state = url.searchParams.get("state") || crypto.randomUUID();
      const scope = url.searchParams.get("scope") || "repo";

      const gh = new URL("https://github.com/login/oauth/authorize");
      gh.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
      gh.searchParams.set("redirect_uri", CALLBACK_URL);
      gh.searchParams.set("scope", scope);
      gh.searchParams.set("state", state);

      // Optional: helps avoid weird cached flows in some browsers
      // gh.searchParams.set("prompt", "select_account");

      return Response.redirect(gh.toString(), 302);
    }

    // --- Step 2: GitHub redirects back here with ?code=...&state=... ---
    if (path === "/callback") {
      const debug = url.searchParams.get("debug") === "1";
      const code = url.searchParams.get("code");
      const state = url.searchParams.get("state");

      if (!code) {
        return json({ ok: false, message: "Missing ?code in callback", state, cmsOrigin: CMS_ORIGIN }, 400, {
          "cache-control": "no-store",
        });
      }

      // Exchange code → access_token
      let tokenJson;
      let tokenText;
      let httpStatusFromGitHub;

      try {
        const tokenRes = await fetch("https://github.com/login/oauth/access_token", {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": "decap-oauth-cloudflare-worker",
          },
          body: JSON.stringify({
            client_id: env.GITHUB_CLIENT_ID,
            client_secret: env.GITHUB_CLIENT_SECRET,
            code,
          }),
        });

        httpStatusFromGitHub = tokenRes.status;
        tokenText = await tokenRes.text();

        try {
          tokenJson = JSON.parse(tokenText);
        } catch {
          tokenJson = { raw: tokenText };
        }
      } catch (e) {
        return json({ ok: false, message: "Token exchange request failed", error: String(e), cmsOrigin: CMS_ORIGIN }, 500, {
          "cache-control": "no-store",
        });
      }

      const accessToken = tokenJson && tokenJson.access_token;
      if (!accessToken) {
        // GitHub returns 200 with an error JSON for bad/expired codes
        return json(
          {
            ok: false,
            message: "Token exchange failed",
            httpStatusFromGitHub,
            response: tokenJson,
            cmsOrigin: CMS_ORIGIN,
          },
          500,
          { "cache-control": "no-store" }
        );
      }

      /**
       * IMPORTANT: Decap CMS expects the payload after success to be JSON, not a raw token string.
       * For Decap 3.x the most compatible form is:
       *   authorization:github:success:{"token":"..."}
       */
      const payload = JSON.stringify({ token: accessToken });

      if (debug) {
        // Debug page that lets you manually fire postMessage (useful to confirm opener + origin)
        return html(
          `<!doctype html>
<html>
<head><meta charset="utf-8"/><title>Decap OAuth Debug</title></head>
<body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 18px;">
  <h1 style="margin: 0 0 12px 0;">Decap OAuth Debug</h1>
  <p><b>CMS_ORIGIN:</b> <code>${CMS_ORIGIN}</code></p>
  <p><b>window.location.origin:</b> <code><script>document.write(window.location.origin)</script></code></p>
  <p><b>state:</b> <code>${state || ""}</code></p>
  <p><b>message:</b> <code id="msg"></code></p>
  <button id="send">Send postMessage</button>
  <pre id="log" style="margin-top: 14px; background:#111; color:#eee; padding:12px; border-radius:8px;"></pre>
  <script>
    const message = "authorization:github:success:${payload.replace(/</g,"\\u003c")}";
    document.getElementById("msg").textContent = message.slice(0, 120) + (message.length > 120 ? "…" : "");
    const log = (s) => document.getElementById("log").textContent += s + "\\n";

    document.getElementById("send").onclick = () => {
      try {
        if (!window.opener) {
          log("no window.opener (this callback was not opened as a popup)");
          return;
        }
        window.opener.postMessage(message, "${CMS_ORIGIN}");
        log("postMessage sent to ${CMS_ORIGIN}");
      } catch (e) {
        log("postMessage error: " + e);
      }
    };

    // Auto-send when opener exists
    if (window.opener) {
      try {
        window.opener.postMessage(message, "${CMS_ORIGIN}");
        log("auto postMessage sent to ${CMS_ORIGIN}");
        window.close();
      } catch (e) {
        log("auto postMessage error: " + e);
      }
    } else {
      log("auto postMessage skipped: no window.opener");
    }
  </script>
</body>
</html>`,
          200,
          { "cache-control": "no-store" }
        );
      }

      // Normal mode: send message back to opener and close the popup
      return html(
        `<!doctype html><html><head><meta charset="utf-8"/></head><body>
<script>
  (function () {
    var message = "authorization:github:success:${payload.replace(/</g,"\\u003c")}";
    try {
      if (window.opener) {
        window.opener.postMessage(message, "${CMS_ORIGIN}");
      }
    } finally {
      window.close();
    }
  })();
</script>
</body></html>`,
        200,
        { "cache-control": "no-store" }
      );
    }

    // Everything else
    return new Response("Not found", { status: 404, headers: { "content-type": "text/plain; charset=utf-8" } });
  },
};
