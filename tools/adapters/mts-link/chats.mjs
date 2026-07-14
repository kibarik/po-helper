// mts-link-chat-sync — export MTS Link chat messages for a window into markdown.
//
// Modes:
//   --list-chats [--search "text"]      list watched-able chats (numbered from 0)
//   --watch 0,3,7                       resolve picked indices -> chat-id + name (for /chat-watch)
//   --add --chat-id X --name "" --purpose "" --extract ""   append one registry entry
//   --list-watched                      print the current registry
//   --unwatch <chat-id>                 remove a registry entry
//   --pull [--days N | --from D --to D] [--dry]   export each watched chat's window
//
// READ-ONLY against the MTS Link chat API (see wsClient.mjs). Reuses the transcript
// tool's saved SSO session.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { harvest } from "./harvest.mjs";
import { connect } from "./wsClient.mjs";
import { readRegistry, addEntries, removeEntry } from "./registry.mjs";
import { OUTPUT_DIR } from "./config.mjs";

// ---------- args ----------
const argv = process.argv.slice(2);
const has = (f) => argv.includes(`--${f}`);
const arg = (f) => { const i = argv.indexOf(`--${f}`); return i >= 0 ? argv[i + 1] : undefined; };

const LIST_FILE = join(OUTPUT_DIR, ".last-chats.json");
const MSK = new Intl.DateTimeFormat("ru-RU", { timeZone: "Europe/Moscow", hour: "2-digit", minute: "2-digit" });
const MSK_DATE = new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Moscow", year: "numeric", month: "2-digit", day: "2-digit" });
const dateStr = (ms) => MSK_DATE.format(new Date(ms));            // YYYY-MM-DD
const timeStr = (ms) => MSK.format(new Date(ms));                 // HH:MM
const sanitize = (s) => String(s || "Без названия").replace(/[\/:\\]/g, "-").replace(/\s+/g, " ").trim().slice(0, 80);

// ---------- chat list normalization ----------
// dialogs/group chats come wrapped: {type, value:{...}}; channels come flat.
function normDialogItem(it) {
  const v = it.value || {};
  if (it.type === "FavoritesListItem") return { chatId: v.chatId, name: "Избранное", kind: "favorites" };
  if (it.type === "DialogListItem") return { chatId: v.chatId, name: null, kind: "dialog", interlocutorId: v.interlocutorId };
  return { chatId: v.chatId, name: v.name, kind: "group" }; // GroupChatListItem
}

async function fetchAllChats(rpc, orgId, resolveName) {
  const dialogs = (await rpc.call("chat", "Chat.GetMyDialogsAndGroupChatsV2", {})).value.items || [];
  const channels = (await rpc.call("chat", "Chat.GetMyChannelsV2", {})).value.items || [];
  const out = [];
  for (const it of dialogs) {
    const n = normDialogItem(it);
    if (!n.chatId) continue;
    if (!n.name && n.interlocutorId) n.name = await resolveName(n.interlocutorId);
    out.push(n);
  }
  for (const c of channels) out.push({ chatId: c.chatId, name: c.name, kind: "channel" });
  return out;
}

// ---------- member name resolution (cached) ----------
function makeResolver(rpc, orgId) {
  const cache = new Map();
  return async (userId) => {
    if (!userId) return "—";
    if (cache.has(userId)) return cache.get(userId);
    let name = userId.slice(0, 8);
    try {
      const p = (await rpc.call("organization", "Organization.GetMemberV2", { organizationId: orgId, userId })).value?.profile || {};
      name = [p.firstName, p.lastName].filter(Boolean).join(" ").trim() || p.displayName || name;
    } catch { /* keep short-id fallback */ }
    cache.set(userId, name);
    return name;
  };
}

// ---------- message pagination for a window ----------
async function fetchWindow(rpc, chatId, fromMs, toMs) {
  const collected = [];
  let cursor = undefined; // message id to page from; first page = newest (no cursor)
  for (let guard = 0; guard < 200; guard++) {
    // First page: no direction/from → newest messages. Then page older with "Before".
    const param = cursor ? { chatId, limit: 50, from: cursor, direction: "Before" } : { chatId, limit: 50 };
    const res = await rpc.call("chat", "Chat.GetMessagesV2", param);
    const msgs = res.value?.messages || [];
    if (msgs.length === 0) break;
    // API returns ascending by createdAt; oldest is msgs[0].
    for (const m of msgs) collected.push(m);
    const oldest = msgs.reduce((a, b) => (a.createdAt <= b.createdAt ? a : b));
    if (oldest.createdAt < fromMs) break;      // paged past the window's left edge
    if (cursor === oldest.id) break;            // no progress — stop
    cursor = oldest.id;
  }
  // de-dup by id, keep window, drop deleted, sort ascending
  const seen = new Set();
  return collected
    .filter((m) => { if (seen.has(m.id)) return false; seen.add(m.id); return true; })
    .filter((m) => !m.isDeleted && m.createdAt >= fromMs && m.createdAt <= toMs)
    .sort((a, b) => a.createdAt - b.createdAt);
}

// ---------- window bounds ----------
function windowBounds() {
  const from = arg("from"), to = arg("to");
  const days = Number(arg("days") || 14);
  const toMs = to ? Date.parse(`${to}T23:59:59+03:00`) : Date.now();
  const fromMs = from ? Date.parse(`${from}T00:00:00+03:00`) : toMs - days * 86400000;
  return { fromMs, toMs };
}

// ====================================================================
async function main() {
  mkdirSync(OUTPUT_DIR, { recursive: true });

  // --- registry-only modes that need no network ---
  if (has("list-watched")) {
    const reg = readRegistry();
    if (!reg.length) return console.log("Реестр пуст. Сначала добавь чаты: --list-chats → --add (см. README).");
    reg.forEach((e, i) => console.log(`  ${i}. ${e.name}  [${e["chat-id"]}]\n       purpose: ${e.purpose || "—"}\n       extract: ${e.extract || "—"}`));
    return;
  }
  if (has("add")) {
    const entry = { "chat-id": arg("chat-id"), name: arg("name") || "", purpose: arg("purpose") || "", extract: arg("extract") || "", added: dateStr(Date.now()) };
    if (!entry["chat-id"]) throw new Error("--add требует --chat-id");
    const n = addEntries([entry]);
    return console.log(n ? `Добавлено: ${entry.name} [${entry["chat-id"]}]` : `Уже в реестре: ${entry["chat-id"]}`);
  }
  if (has("unwatch")) {
    const n = removeEntry(arg("unwatch"));
    return console.log(n ? `Удалено из реестра: ${arg("unwatch")}` : `Не найдено: ${arg("unwatch")}`);
  }

  // --- network modes (below need a live session; bail early otherwise) ---
  if (!has("list-chats") && !has("watch") && !has("pull")) {
    console.log("Режимы: --list-chats | --watch | --add | --list-watched | --unwatch | --pull");
    return;
  }
  const h = await harvest();
  const rpc = await connect(h);
  try {
    if (has("list-chats")) {
      const resolveName = makeResolver(rpc, h.orgId);
      let chats = await fetchAllChats(rpc, h.orgId, resolveName);
      const search = arg("search");
      if (search) chats = chats.filter((c) => (c.name || "").toLowerCase().includes(search.toLowerCase()));
      chats.sort((a, b) => (a.name || "").localeCompare(b.name || "", "ru"));
      const watched = new Set(readRegistry().map((e) => String(e["chat-id"])));
      chats.forEach((c, i) => (c.index = i));
      writeFileSync(LIST_FILE, JSON.stringify(chats, null, 2));
      console.log(`Чатов${search ? ` по «${search}»` : ""}: ${chats.length}\n`);
      for (const c of chats) console.log(`  ${c.index}. ${c.name}  [${c.chatId}]${watched.has(String(c.chatId)) ? "   [слежу]" : ""}`);
      console.log(`\nДальше: node chats.mjs --watch <номера>, затем --add по каждому.`);
      return;
    }

    if (has("watch")) {
      if (!existsSync(LIST_FILE)) throw new Error("Нет .last-chats.json — сначала --list-chats");
      const list = JSON.parse(readFileSync(LIST_FILE, "utf8"));
      const picks = String(arg("watch")).split(",").map((s) => Number(s.trim())).filter(Number.isInteger);
      const chosen = picks.map((i) => list[i]).filter(Boolean);
      console.log(JSON.stringify(chosen.map((c) => ({ "chat-id": c.chatId, name: c.name })), null, 2));
      return;
    }

    if (has("pull")) {
      // --all pulls every chat in the window, bypassing the registry (purpose/extract blank).
      let reg;
      if (has("all")) {
        const resolveNameForList = makeResolver(rpc, h.orgId);
        reg = (await fetchAllChats(rpc, h.orgId, resolveNameForList))
          .map((c) => ({ "chat-id": c.chatId, name: c.name, purpose: "", extract: "" }));
      } else {
        reg = readRegistry();
        if (!reg.length) throw new Error("Реестр пуст. Сначала добавь чаты: --list-chats → --add (см. README). Или --pull --all.");
      }
      const { fromMs, toMs } = windowBounds();
      const dry = has("dry");
      const resolveName = makeResolver(rpc, h.orgId);
      const win = `${dateStr(fromMs)}..${dateStr(toMs)}`;
      console.log(`Окно: ${win}${dry ? "  (dry-run)" : ""}\n`);
      const saved = [];
      for (const e of reg) {
        const chatId = e["chat-id"];
        const msgs = await fetchWindow(rpc, chatId, fromMs, toMs);
        if (msgs.length === 0) { console.log(`  · ${e.name}: 0 сообщений в окне`); continue; }
        if (dry) { console.log(`  [dry] ${e.name}: ${msgs.length} сообщений`); continue; }
        const fileBase = `${win} ${sanitize(e.name)}`;
        const lines = [
          "---", "type: chat-dump", `source: "MTS Link"`, `chat-id: "${chatId}"`, `window: "${win}"`,
          `purpose: ${JSON.stringify(e.purpose || "")}`, `extract: ${JSON.stringify(e.extract || "")}`,
          `msg-count: ${msgs.length}`, "---", "", `# ${e.name}`, "",
        ];
        let lastDate = "";
        for (const m of msgs) {
          const d = dateStr(m.createdAt);
          if (d !== lastDate) { lines.push("", `## ${d}`, ""); lastDate = d; }
          const author = await resolveName(m.authorId);
          lines.push(`${author} ${timeStr(m.createdAt)}: ${(m.text || "").trim()}`);
        }
        const filePath = join(OUTPUT_DIR, `${fileBase}.md`);
        writeFileSync(filePath, lines.join("\n"), "utf8");
        console.log(`  ✓ ${fileBase}.md  (${msgs.length} сообщений)`);
        saved.push({ file: `${fileBase}.md`, chatId, msgCount: msgs.length });
      }
      if (!dry) writeFileSync(join(OUTPUT_DIR, ".last-pull.json"), JSON.stringify(saved, null, 2));
      console.log(`\nГотово. Файлов: ${dry ? 0 : saved.length}. Папка: ${OUTPUT_DIR}`);
      return;
    }
  } finally {
    rpc.close();
  }
}

main()
  .then(() => process.exit(0))
  .catch((e) => { console.error("\n" + e.message); process.exit(1); });
