// Configuration for mts-link-chat-sync.
//
// Nothing personal is baked in. Defaults are safe/relative; override anything via a
// local `.env` file (copy `.env.example` → `.env`) or real environment variables.
// The `.env` file is gitignored — your paths and session location never get committed.

import { homedir } from "node:os";
import { join, isAbsolute, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// --- load .env from the tool directory, if present (built-in, no dependency) ---
const TOOL_DIR = dirname(fileURLToPath(import.meta.url));
try { process.loadEnvFile(join(TOOL_DIR, ".env")); } catch { /* no .env — use defaults/real env */ }

// Resolve a path setting: absolute stays, `~` expands, relative is anchored to the tool dir.
function resolvePath(value, fallback) {
  const v = value || fallback;
  if (v.startsWith("~/")) return join(homedir(), v.slice(2));
  return isAbsolute(v) ? v : join(TOOL_DIR, v);
}

// Entry point of the chats web app. Override for a different MTS Link instance.
export const CHATS_URL = process.env.CHAT_SYNC_CHATS_URL || "https://my.mts-link.ru/chats/";

// Saved browser session (cookies + localStorage), produced by `npm run login`.
// Default lives in your home dir, OUTSIDE this repo — it is a personal SSO secret.
export const AUTH_FILE = resolvePath(process.env.CHAT_SYNC_AUTH_FILE, "~/.mts-link-chat-sync/auth.json");

// Where exported chat markdown lands. Default: ./chats-out inside the tool (gitignored).
export const OUTPUT_DIR = resolvePath(process.env.CHAT_SYNC_OUTPUT_DIR, "chats-out");

// Registry of watched chats. Default: alongside the output.
export const REGISTRY_FILE = process.env.CHAT_SYNC_REGISTRY
  ? resolvePath(process.env.CHAT_SYNC_REGISTRY)
  : join(OUTPUT_DIR, "watched-chats.yaml");
