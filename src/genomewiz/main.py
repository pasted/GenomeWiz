from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware

from .db.base import Base, engine
from .core.config import get_settings
from .core.auth import require_curator_or_admin, require_admin
from .routers import sv as sv_router
from .routers import labels as labels_router
from .routers import consensus  as consensus_router
from .routers import auth as auth_router
from .routers import evidence as evidence_router

from fastapi.responses import HTMLResponse

app = FastAPI(title="GenomeWiz", version="0.1.0")

# DB
Base.metadata.create_all(bind=engine)

# Sessions for OAuth
s = get_settings()
app.add_middleware(SessionMiddleware, secret_key=s.session_secret, https_only=False)

@app.get("/health")
def health():
    return {"status": "ok"}

# Public auth routes
app.include_router(auth_router)

# Protected routes (example usage of role guards)
# You can also place Depends in each handler if you prefer fine-grained control
app.include_router(sv_router, dependencies=[Depends(require_curator_or_admin)])
app.include_router(labels_router, dependencies=[Depends(require_curator_or_admin)])
app.include_router(consensus_router, dependencies=[Depends(require_curator_or_admin)])
app.include_router(evidence_router, dependencies=[Depends(require_curator_or_admin)])


@app.get("/auth/signed-in", response_class=HTMLResponse)
def auth_signed_in_page():
    # Minimal HTML that reads #token, stores it, and shows status
    return """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Signed in</title></head>
<body>
  <h2>Signing you in…</h2>
  <div id="msg"></div>
  <script>
    (function () {
      const hash = (window.location.hash || "").replace(/^#/, "");
      const params = new URLSearchParams(hash);
      const token = params.get("token");

      const msg = document.getElementById("msg");
      if (!token) {
        msg.textContent = "No token found in URL. Try logging in again.";
        return;
      }

      // Store token for the SPA / future requests
      try { localStorage.setItem("gw_jwt", token); } catch (e) {}

      // Optional: verify identity
      fetch("/auth/me", { headers: { "Authorization": "Bearer " + token } })
        .then(r => r.json())
        .then(data => {
          msg.textContent = "Signed in as " + (data.email || "unknown");
        })
        .catch(() => { msg.textContent = "Signed in. (Could not verify /auth/me)"; });

      // Optional: redirect to your app home after a short delay
      // setTimeout(() => { window.location.assign("/"); }, 800);
    })();
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>GenomeWiz</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2em; }
    .card { max-width: 500px; padding: 1.5em; border: 1px solid #ccc;
            border-radius: 1em; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    button { padding: 0.6em 1.2em; margin: 0.5em; font-size: 1em; cursor: pointer;
             border: none; border-radius: 0.5em; background-color: #0069d9; color: #fff; }
    button:hover { background-color: #0053aa; }
    #user-info { margin-top: 1em; }
    #token { font-family: monospace; word-break: break-all; font-size: 0.85em; color: #555; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🧬 GenomeWiz</h1>
    <p id="status">Checking authentication…</p>
    <div id="user-info" hidden>
      <p><strong>Email:</strong> <span id="email"></span></p>
      <p><strong>Roles:</strong> <span id="roles"></span></p>
      <details>
        <summary>Show JWT token</summary>
        <div id="token"></div>
      </details>
    </div>
    <button id="login-btn" hidden>Login with Google</button>
    <button id="logout-btn" hidden>Logout</button>
  </div>

  <script>
    async function getMe(token) {
      const r = await fetch("/auth/me", {
        headers: { "Authorization": "Bearer " + token }
      });
      if (!r.ok) throw new Error(await r.text());
      return r.json();
    }

    async function updateUI() {
      const status = document.getElementById("status");
      const info = document.getElementById("user-info");
      const loginBtn = document.getElementById("login-btn");
      const logoutBtn = document.getElementById("logout-btn");
      const emailEl = document.getElementById("email");
      const rolesEl = document.getElementById("roles");
      const tokenEl = document.getElementById("token");

      const token = localStorage.getItem("gw_jwt");
      if (!token) {
        status.textContent = "You are not signed in.";
        loginBtn.hidden = false;
        logoutBtn.hidden = true;
        info.hidden = true;
        return;
      }

      try {
        const me = await getMe(token);
        status.textContent = "Signed in ✅";
        info.hidden = false;
        emailEl.textContent = me.email;
        rolesEl.textContent = me.roles.join(", ");
        tokenEl.textContent = token;
        loginBtn.hidden = true;
        logoutBtn.hidden = false;
      } catch {
        status.textContent = "Invalid or expired session.";
        loginBtn.hidden = false;
        logoutBtn.hidden = true;
        info.hidden = true;
        localStorage.removeItem("gw_jwt");
      }
    }

    document.getElementById("login-btn").onclick = () => {
      window.location.assign("/auth/login");
    };
    document.getElementById("logout-btn").onclick = async () => {
      localStorage.removeItem("gw_jwt");
      await fetch("/auth/logout");
      location.reload();
    };

    updateUI();
  </script>
  <button id="fetch-png" hidden>Render PNG (demo)</button>
  <img id="panel" style="display:block; margin-top:1em; max-width:100%;" />
  <script>
  // after successful /auth/me:
  document.getElementById("fetch-png").hidden = false;
  document.getElementById("fetch-png").onclick = async () => {
    const token = localStorage.getItem("gw_jwt");
    const r = await fetch("/evidence/png", {
      method: "POST",
      headers: {"Authorization": "Bearer " + token, "Content-Type": "application/json"},
      body: JSON.stringify({ sample_id: "samp_demo", chrom: "chr12", start: 25396000, end: 25412000 })
    });
    const blob = await r.blob();
    document.getElementById("panel").src = URL.createObjectURL(blob);
  };
  </script>

</body>
</html>
"""
