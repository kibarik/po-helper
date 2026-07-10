# Deploy PR-Agent App on Dokploy

Runs the self-hosted PR-Agent GitHub App on your Dokploy box. Bypasses the
GitHub Actions billing lock entirely (webhook + GitHub API, not Actions).
Gives auto-review on PR open + `/ask` `/review` `/improve` from PR comments,
using your z.ai GLM-5 key. Dokploy's Traefik handles TLS.

Prereqs: a Dokploy instance, a domain whose DNS A-record points at the Dokploy
host, ports 80/443 open on that host.

---

## 1. Register the GitHub App

Settings → Developer settings → **GitHub Apps → New GitHub App**.

- **Permissions**: Pull requests **RW**, Issue comment **RW**, Contents **RO**, Metadata **RO**.
- **Subscribe to events**: Pull request, Issue comment, Push.
- **Webhook URL**: `https://pr-agent.<your-domain>/api/v1/github_webhooks`
  (the domain you'll attach in step 3 — set it now, it just needs to match).
- **Webhook secret**: generate and keep it —
  ```bash
  python -c "import secrets; print(secrets.token_hex(10))"
  ```
- **Generate a private key** → downloads a `.pem`. Note the **App ID**.
- Leave "Where can this app be installed?" as you prefer (Only this account is fine).

Don't install it on the repo yet — do that in step 5, after it's live.

---

## 2. Create the Dokploy service

In your Dokploy project → **Create Service → Compose**.

- **Provider**: Git → this repo (`https://github.com/kibarik/po-helper`), branch
  `main` (or your CI branch).
- **Compose Path**: `deploy/pr-agent/github-app/docker-compose.dokploy.yml`

That compose builds the `github_app` image directly from the upstream pr-agent
git repo — nothing else to clone.

---

## 3. Secrets — Dokploy Environment

Set these in the service's **Environment** tab (the compose substitutes them):

```
OPENAI_KEY=<z.ai GLM-5 key>
GITHUB_APP_ID=<app id>
GITHUB_WEBHOOK_SECRET=<webhook secret from step 1>
GITHUB_PRIVATE_KEY=<paste the whole .pem>
```

Model/provider default to z.ai GLM-5 in the compose; override with
`OPENAI_API_BASE`, `CONFIG_MODEL`, `CONFIG_MAX_TOKENS` only if needed.

> **Multiline .pem caveat.** `GITHUB_PRIVATE_KEY` is a multiline PEM. Dokploy's
> Environment editor keeps newlines — paste the key as-is (BEGIN/END lines
> included). If the app logs a key-parse error, the newlines got flattened; then
> either re-paste preserving line breaks, or switch that one value to a File
> Mount at `/app/pr_agent/settings/.secrets.toml` with a `[github] private_key`
> triple-quoted block (see `.secrets.toml.example`).

---

## 4. Domain + TLS

Service → **Domains → Add Domain**:

- **Host**: `pr-agent.<your-domain>` (must match the Webhook URL from step 1)
- **Container Port**: `3000`
- **HTTPS**: on
- **Certificate**: Let's Encrypt

Then **Deploy**. Watch the build/deploy logs; the container should log that it
binds `:3000`. Hit `https://pr-agent.<your-domain>/` — a 404/health response
means Traefik + the app are up.

---

## 5. Wire the webhook & install

- Back in the GitHub App settings, confirm the Webhook URL/secret match, then
  the **Advanced** tab shows webhook deliveries — a green `ping` = reachable.
- **Install App** tab → install on `kibarik/po-helper`.

---

## 6. Verify

- Open a test PR → `describe` / `review` / `improve` comments appear in seconds.
- Comment `/ask "что делает этот PR?"` on the PR → it answers.

Behavior (which commands auto-run, Russian output, focus) is driven by the
committed [`.pr_agent.toml`](../../../.pr_agent.toml) at the repo root — edit
there, no redeploy of the App needed.

## Updating

- **Config/behavior**: edit `.pr_agent.toml`, merge to `main`. Picked up live.
- **PR-Agent version**: Dokploy → service → **Redeploy** (rebuilds from
  upstream `main`). Pin a tag by setting the git context to
  `...pr-agent.git#<tag>` in the compose if you want reproducible builds.

## Troubleshooting

- **Webhook delivery fails (timeout/SSL)**: DNS not pointing at the Dokploy host,
  or cert not issued yet — check Dokploy Traefik logs and the Domains tab.
- **401/invalid signature in app logs**: `webhook_secret` in the mount ≠ the one
  in the GitHub App settings.
- **LLM auth errors**: `[openai] key`/`api_base` in the mount are wrong, or the
  z.ai key is out of quota.
- **App comments nothing on open**: check the App is subscribed to the Pull
  request event and installed on the repo; check `[github_app] pr_commands` in
  `.pr_agent.toml`.
