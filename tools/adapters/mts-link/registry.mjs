// Read/write the watched-chats registry (YAML in the vault).
//
// Schema: a YAML list of entries the PO curates. `purpose`/`extract` are free text
// that steers Claude's later analysis; they ride into each exported file's frontmatter.
//
//   - chat-id: "abc123"
//     name: "Продажи B2B — оперативка"
//     purpose: "Слежу за блокерами сделок и жалобами на биллинг"
//     extract: "Новые блокеры, эскалации, упоминания конкурентов, дедлайны"
//     added: 2026-07-09

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import YAML from "yaml";
import { REGISTRY_FILE } from "./config.mjs";

const HEADER = `# Отслеживаемые чаты MTS Link — их выгружает \`chat-sync --pull\`.
# Правь через скилл /chat-watch или руками. Одна запись — один чат.
# purpose = зачем следишь; extract = что вытаскивать (направляет анализ Claude).
`;

export function readRegistry() {
  if (!existsSync(REGISTRY_FILE)) return [];
  const raw = readFileSync(REGISTRY_FILE, "utf8");
  const parsed = YAML.parse(raw);
  if (!parsed) return [];
  if (!Array.isArray(parsed)) throw new Error(`Реестр ${REGISTRY_FILE} должен быть YAML-списком.`);
  return parsed;
}

export function writeRegistry(entries) {
  mkdirSync(dirname(REGISTRY_FILE), { recursive: true });
  writeFileSync(REGISTRY_FILE, HEADER + "\n" + YAML.stringify(entries), "utf8");
}

// Add entries, skipping chat-ids already present. Returns count actually added.
export function addEntries(newOnes) {
  const entries = readRegistry();
  const have = new Set(entries.map((e) => String(e["chat-id"])));
  let added = 0;
  for (const e of newOnes) {
    if (have.has(String(e["chat-id"]))) continue;
    entries.push(e); have.add(String(e["chat-id"])); added += 1;
  }
  writeRegistry(entries);
  return added;
}

export function removeEntry(chatId) {
  const entries = readRegistry();
  const kept = entries.filter((e) => String(e["chat-id"]) !== String(chatId));
  writeRegistry(kept);
  return entries.length - kept.length;
}
