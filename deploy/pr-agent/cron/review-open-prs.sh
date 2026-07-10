#!/usr/bin/env bash
# Self-hosted PR review without GitHub Actions.
# Polls open PRs of a repo and runs PR-Agent (describe/review/improve) on each
# PR whose head commit hasn't been reviewed yet. Re-reviews when new commits land.
#
# Why this exists: the GitHub account's Actions are billing-locked, so the
# in-repo workflow never starts. This runs the same PR-Agent from any box that
# has `gh` + `docker`, using the z.ai GLM-5 key. No public ingress, no GH App.
#
# Usage:  ./review-open-prs.sh            (reads config from ./ .env-style file)
#         REPO=owner/name ./review-open-prs.sh
# Cron:   */5 * * * *  cd /opt/pr-agent && ./review-open-prs.sh >> run.log 2>&1
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- config -----------------------------------------------------------------
REPO="${REPO:-kibarik/po-helper}"
IMAGE="${IMAGE:-codiumai/pr-agent:latest}"
ENV_FILE="${ENV_FILE:-$HERE/.env}"
STATE_DIR="${STATE_DIR:-$HERE/state}"
STATE_FILE="$STATE_DIR/handled.tsv"          # lines: <pr_number>\t<head_sha>
# Commands run on each new/updated PR. describe edits the PR body; review and
# improve post comments. Trim this list to taste.
COMMANDS=(${PR_COMMANDS:-describe review improve})
# Set SKIP_DRAFT=true to ignore draft PRs.
SKIP_DRAFT="${SKIP_DRAFT:-false}"

command -v gh >/dev/null     || { echo "FATAL: gh CLI not found"; exit 1; }
command -v docker >/dev/null || { echo "FATAL: docker not found"; exit 1; }
[[ -f "$ENV_FILE" ]] || { echo "FATAL: env file not found: $ENV_FILE (copy .env.example)"; exit 1; }
mkdir -p "$STATE_DIR"
touch "$STATE_FILE"

already_handled() {  # $1=num $2=sha
  grep -qxF "$1	$2" "$STATE_FILE"
}
record_handled() {   # $1=num $2=sha  (one line per PR: replace old sha)
  local tmp; tmp="$(mktemp)"
  grep -vP "^$1\t" "$STATE_FILE" > "$tmp" 2>/dev/null || true
  printf '%s\t%s\n' "$1" "$2" >> "$tmp"
  mv "$tmp" "$STATE_FILE"
}

echo "[$(date -u +%FT%TZ)] scanning open PRs of $REPO"

# owner/name -> jq-friendly list of open PRs
mapfile -t PRS < <(gh api "repos/$REPO/pulls?state=open&per_page=100" \
  --jq '.[] | [(.number|tostring), .head.sha, (.draft|tostring)] | @tsv')

for line in "${PRS[@]}"; do
  IFS=$'\t' read -r num sha draft <<<"$line"
  if [[ "$SKIP_DRAFT" == "true" && "$draft" == "true" ]]; then
    echo "  PR #$num: draft, skip"; continue
  fi
  if already_handled "$num" "$sha"; then
    echo "  PR #$num @ ${sha:0:8}: already reviewed, skip"; continue
  fi
  url="https://github.com/$REPO/pull/$num"
  echo "  PR #$num @ ${sha:0:8}: reviewing (${COMMANDS[*]})"
  for cmd in "${COMMANDS[@]}"; do
    echo "    -> pr-agent $cmd"
    docker run --rm --env-file "$ENV_FILE" "$IMAGE" --pr_url="$url" "$cmd" \
      || echo "    !! $cmd failed for PR #$num (continuing)"
  done
  record_handled "$num" "$sha"
done

echo "[$(date -u +%FT%TZ)] done"
