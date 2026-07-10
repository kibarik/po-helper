# Self-hosted PR review (no GitHub Actions)

The in-repo Actions workflow can't run: the GitHub account is **billing-locked**,
so every job fails in ~3s with _"account is locked due to a billing issue"_.
This runs [PR-Agent](https://github.com/qodo-ai/pr-agent) from your own box,
driven by a webhook instead of Actions.

Two modes here:

| mode | folder | auto-review on open | `@mention` dialog | needs public HTTPS |
|------|--------|:---:|:---:|:---:|
| **GitHub App** (active) | [`github-app/`](github-app/) | ✅ | ✅ | ✅ |
| cron (fallback) | [`cron/`](cron/) | ✅ (≈5 min lag) | ❌ | ❌ |

Review behavior (Russian, focus, N suggestions) and the auto-command list live
in the repo-root [`.pr_agent.toml`](../../.pr_agent.toml) — committed, no secrets.
Model + keys + App credentials live in `github-app/.secrets.toml` (git-ignored).

---

## GitHub App (auto-review + mention dialog)

One webhook server. Auto-reviews every PR on open, re-reviews on push, and
answers commands typed as PR comments — real-time.

> **On Dokploy?** Follow [`github-app/DOKPLOY.md`](github-app/DOKPLOY.md) instead —
> it uses `docker-compose.dokploy.yml`, lets Dokploy's Traefik handle TLS, and
> injects secrets via a Dokploy File Mount. The manual steps below are for a
> plain Docker host.

### What "mention dialog" means

PR-Agent responds to its **command set** in PR comments (no `@bot` needed):

- `/ask "почему тут так сделано?"` — free-form Q&A about the PR
- `/review` — re-run the review
- `/improve` — code suggestions
- `/describe` — regenerate the PR description
- `/help`, `/config`, `/update_changelog`

It's a command dialog scoped to the PR, not arbitrary chat.

### Setup

**1. Register a GitHub App** — Settings → Developer settings → GitHub Apps → New.
   - Permissions: **Pull requests** RW, **Issue comment** RW, **Contents** RO, **Metadata** RO.
   - Subscribe to events: **Pull request**, **Issue comment**, **Push** (for re-review on new commits).
   - Webhook URL: your public endpoint (set in step 4). Webhook secret: generate one:
     ```bash
     python -c "import secrets; print(secrets.token_hex(10))"
     ```
   - Generate & download a **private key** (.pem). Note the **App ID**.

**2. Put files in place** on the box:
   ```bash
   cd deploy/pr-agent/github-app
   git clone https://github.com/qodo-ai/pr-agent.git   # build context
   cp .secrets.toml.example .secrets.toml
   $EDITOR .secrets.toml        # z.ai key + app_id + webhook_secret + paste the .pem
   ```

**3. TLS**: either use the bundled Caddy (auto Let's Encrypt) —
   ```bash
   cp Caddyfile.example Caddyfile && $EDITOR Caddyfile   # set your domain
   ```
   — or delete the `caddy` service from `docker-compose.yml` and point your own
   reverse proxy at the container's port 3000.

**4. Launch**:
   ```bash
   docker compose up -d --build
   docker compose logs -f pr-agent      # confirm it binds :3000
   ```

**5. Wire the webhook**: back in the App settings set Webhook URL to
   `https://<your-domain>/api/v1/github_webhooks` and the secret from step 1.
   Then **Install App** → select `kibarik/po-helper`.

**6. Verify**: open a test PR → describe/review/improve should appear within
   seconds. Comment `/ask "что делает этот PR?"` → it answers.

> The App reads this repo's `.pr_agent.toml` for `[github_app] pr_commands`
> (what auto-runs on open) and `push_commands` (what runs on new commits).

---

## cron fallback (no public endpoint)

If you can't expose HTTPS, `cron/` auto-reviews open PRs on a timer (no mention
dialog). See [`cron/review-open-prs.sh`](cron/review-open-prs.sh):

```bash
cd deploy/pr-agent/cron
cp .env.example .env && $EDITOR .env     # z.ai key + GitHub PAT (repo scope)
docker pull codiumai/pr-agent:latest
./review-open-prs.sh                      # dry run
# schedule: */5 * * * * cd .../cron && ./review-open-prs.sh >> run.log 2>&1
```

Or run it via the bundled systemd `pr-review.timer` / `pr-review.service`.

---

## Notes

- Billing lock affects **Actions only** — the App/cron use your server + the
  GitHub API and are unaffected.
- Comments are authored by the App (App mode) or the PAT owner (cron mode).
- When billing is unlocked, `.github/workflows/pr-agent.yml` works again on its
  own; you can retire this deployment.
