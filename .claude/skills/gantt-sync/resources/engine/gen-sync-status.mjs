#!/usr/bin/env node
// gen-sync-status.mjs — GANTT-anchored read-model сверки GANTT↔OKR↔JIRA.
// Read-only: пишет только выходной markdown-зеркало. GANTT правит владелец в GanttPRO,
// JIRA — вручную. Движок оффлайновый и детерминированный: вход — файлы, выход — markdown.
// Сбор live-issues из JIRA — на стороне skill через MCP (сюда приходит --issues <file>).
import { readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

// Опорные строки GanttPRO-экспорта (дефолты). Переопределяются через --anchors <json>
// или из domain-profile (секция gantt.anchors), если экспорт на другом языке/шаблоне.
export const ANCHORS = {
  header: 'Инициативы в квартале',
  legend: 'Легенда фаз:',
  stack: 'Стек:',
};

export function decodeCell(raw) {
  if (raw == null) return '';
  return raw
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/[\r\n]+/g, ' ')
    .trim();
}

export function parseSheetXml(xml) {
  const rows = [];
  for (const rowFrag of xml.split('<row ').slice(1)) {
    const rNum = Number((rowFrag.match(/^r="(\d+)"/) || [])[1]);
    if (!rNum) continue;
    const cells = {};
    const cellRe = /<c r="([A-P])\d+"[^>]*?(?:t="([^"]*)")?[^>]*>(?:<is><t[^>]*>([\s\S]*?)<\/t><\/is>|<v>([\s\S]*?)<\/v>)?<\/c>/g;
    let m;
    while ((m = cellRe.exec(rowFrag))) {
      const col = m[1];
      const raw = m[3] !== undefined ? m[3] : (m[4] !== undefined ? m[4] : '');
      const text = decodeCell(raw);
      if (text) cells[col] = text;
    }
    rows.push({ r: rNum, cells });
  }
  return rows;
}

export function colNum(letter) {
  return letter.charCodeAt(0) - 64; // 'A' → 1
}

const PHASE_MAP = [
  [/\b(BA|SA|ADR|PO)\b/i, 'analytics'],
  [/\b(BE|FE|Go|PHP|Java|C#)\b/i, 'dev'],
  [/\bQA\b/i, 'qa'],
  [/\bRM\b/i, 'release'],
];

export function phaseClass(code) {
  for (const [re, cls] of PHASE_MAP) if (re.test(code)) return cls;
  return 'other';
}

export function cardBars(cells) {
  const bars = [];
  for (const [col, text] of Object.entries(cells)) {
    if (col === 'A' || !text) continue;
    const n = colNum(col);
    if (n < 2 || n > 15) continue; // B..O
    bars.push({ col, sprint: Math.floor(n / 2), phase: phaseClass(text) });
  }
  bars.sort((a, b) => a.sprint - b.sprint);
  return bars;
}

// карточка = есть заполненная ячейка в B..P (кол.16 P = маркер "вне квартала");
// свимлейн = только A-текст, в B..P пусто.
export function hasCardContent(cells) {
  for (const [col, text] of Object.entries(cells)) {
    if (col === 'A' || !text) continue;
    const n = colNum(col);
    if (n >= 2 && n <= 16) return true;
  }
  return false;
}

export function parseGantt(rows, anchors = ANCHORS) {
  const sorted = [...rows].sort((a, b) => a.r - b.r);
  const swimById = new Map();
  const swimlanes = [];
  let current = null;
  for (const row of sorted) {
    const name = row.cells.A;
    if (!name) continue;
    if (name === anchors.header) continue;
    if (name.startsWith(anchors.legend) || name.startsWith(anchors.stack)) break;
    if (!hasCardContent(row.cells)) {
      current = { name, r: row.r, cards: [] }; // кандидат-свимлейн, материализуется при первой карточке
      continue;
    }
    if (!current) continue;
    if (!swimById.has(current.r)) { swimById.set(current.r, current); swimlanes.push(current); }
    const bars = cardBars(row.cells);
    current.cards.push({
      name,
      r: row.r,
      sprints: [...new Set(bars.map((b) => b.sprint))],
      phases: [...new Set(bars.map((b) => b.phase))],
      outOfQuarter: !!row.cells.P,
    });
  }
  return { swimlanes };
}

function tableRows(md) {
  return md.split('\n').filter((l) => l.startsWith('| '));
}

export function parseMap(md) {
  const rows = [];
  for (const line of tableRows(md)) {
    const cells = line.split('|').map((c) => c.trim());
    // cells: ['', KR, Название, GANTT, Эпики, slug?, '']
    if (cells.length < 6) continue;
    const [, kr, name, gantt, epicsRaw, slugRaw] = cells;
    // строки KR-таблицы: непустой KR, не заголовок, не разделитель
    if (!kr || kr === 'KR' || kr.startsWith('-')) continue;
    const epics = epicsRaw
      .split(',')
      .map((e) => e.replace(/\(\?\)/g, '').trim())
      .filter((e) => /^[A-Z][A-Z0-9]*-\d+$/.test(e));
    rows.push({
      kr,
      name,
      gantt,
      epics,
      slug: (slugRaw || '').trim(),
      uncertain: /\(\?\)/.test(epicsRaw),
    });
  }
  return rows;
}

export function parseSwimlaneMap(md) {
  const out = [];
  const section = md.split('## GANTT свимлейн → Инициатива')[1];
  if (!section) return out;
  for (const line of tableRows(section.split('\n##')[0])) {
    const cells = line.split('|').map((c) => c.trim());
    if (cells.length < 4) continue;
    const [, swimlane, initiative] = cells;
    if (swimlane === 'Свимлейн (xlsx)' || swimlane.startsWith('-')) continue;
    out.push({ swimlane, initiative: (initiative || '').trim() });
  }
  return out;
}

export function readSheetRows(xlsxPath, anchors = ANCHORS) {
  let xml;
  try {
    xml = execFileSync('unzip', ['-p', xlsxPath, 'xl/worksheets/sheet1.xml'], {
      encoding: 'utf8',
      maxBuffer: 32 * 1024 * 1024,
    });
  } catch (e) {
    throw new Error(`Не удалось распаковать ${xlsxPath} (нужен системный unzip): ${e.message}`);
  }
  const rows = parseSheetXml(xml);
  const flat = rows.flatMap((row) => Object.values(row.cells));
  for (const anchor of [anchors.header, anchors.legend, anchors.stack]) {
    if (!flat.some((t) => t.includes(anchor))) {
      throw new Error(`Структура xlsx уехала: не найдена опорная строка «${anchor}». Проверь экспорт GanttPRO или gantt.anchors в domain-profile.`);
    }
  }
  return rows;
}

// ─── JIRA нормализация ─────────────────────────────────────────────────────────

export function normalizeIssue(iss) {
  const f = iss.fields || iss;
  return {
    key: iss.key,
    // issuetype (raw REST) | issue_type (MCP jira_search) | type (плоская выгрузка)
    type: f.issuetype?.name || f.issue_type?.name || f.type || '',
    summary: (f.summary || '').replace(/\|/g, '\\|'),
    // status.name везде; statusCategory (raw REST) | category (MCP) — запасной путь
    status: f.status?.name || f.status?.statusCategory?.name || f.status?.category || '',
  };
}

export function indexJira(issues) {
  const byKey = new Map();
  const initiatives = [];
  const epics = [];
  for (const raw of issues) {
    const n = normalizeIssue(raw);
    byKey.set(n.key, n);
    if (/инициатив|initiative/i.test(n.type)) initiatives.push(n);
    else if (/эпик|epic/i.test(n.type)) epics.push(n);
  }
  return { byKey, initiatives, epics };
}

function normName(s) {
  return (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
}

export function diffCoverage({ gantt, map, swimMap, jira }) {
  const drift = [];
  const mapByName = new Map(map.map((m) => [normName(m.name), m]));
  const swimByName = new Map(swimMap.map((s) => [normName(s.swimlane), s]));

  const usedEpics = new Set();
  const usedKrs = new Set();

  // эпики, привязанные к KR в mapping (даже без карточки GANTT), — не сироты
  for (const mrow of map) for (const e of mrow.epics) usedEpics.add(e);

  const tree = [];
  let cardsWithEpic = 0;
  let cardsWithKr = 0;
  let totalCards = 0;
  let swimlanesCovered = 0;

  for (const s of gantt.swimlanes) {
    const sm = swimByName.get(normName(s.name));
    const initiative = sm?.initiative || '';
    const initiativeOk = !!(initiative && jira.byKey.has(initiative));
    if (initiativeOk) swimlanesCovered += 1;
    if (!initiative) drift.push({ level: 'top', kind: 'swimlane-no-initiative', msg: `свимлейн «${s.name}» — нет Инициативы JIRA в mapping` });

    const cards = [];
    for (const c of s.cards) {
      totalCards += 1;
      const mrow = mapByName.get(normName(c.name));
      const slug = mrow?.slug || '';
      const kr = mrow?.kr || '';
      const epics = mrow?.epics || [];
      if (kr) { usedKrs.add(kr); cardsWithKr += 1; }
      const liveEpics = epics.filter((e) => jira.byKey.has(e));
      liveEpics.forEach((e) => usedEpics.add(e));
      const epicsOk = liveEpics.length > 0;
      if (epicsOk) cardsWithEpic += 1;

      if (!kr) drift.push({ level: 'mid', kind: 'card-no-kr', msg: `карточка «${c.name}» — без KR (нет целеполагания)` });
      if (!epics.length) drift.push({ level: 'mid', kind: 'card-no-epic', msg: `карточка «${c.name}» — без Эпика JIRA (пробел планирования)` });

      cards.push({ name: c.name, slug, kr, epics, epicsOk, krOk: !!kr, sprints: c.sprints });
    }
    tree.push({ swimlane: s.name, initiative, initiativeOk, cards });
  }

  // верх: открытая инициатива JIRA без свимлейна
  const mappedInits = new Set(swimMap.map((s) => s.initiative).filter(Boolean));
  for (const init of jira.initiatives) {
    if (!mappedInits.has(init.key)) drift.push({ level: 'top', kind: 'initiative-no-swimlane', msg: `Инициатива ${init.key} — открыта, нет свимлейна GANTT` });
  }

  // середина: открытый эпик JIRA без карточки
  let orphanEpics = 0;
  for (const ep of jira.epics) {
    if (!usedEpics.has(ep.key)) { orphanEpics += 1; drift.push({ level: 'mid', kind: 'orphan-epic', msg: `эпик ${ep.key} — открыт, ни к одной карточке (scope creep)` }); }
  }

  // середина: KR OKR без карточки GANTT
  for (const m of map) {
    if (m.kr && !usedKrs.has(m.kr)) drift.push({ level: 'mid', kind: 'kr-no-card', msg: `KR ${m.kr} — без карточки в GANTT` });
  }

  return {
    tree,
    drift,
    summary: {
      swimlanes: gantt.swimlanes.length,
      swimlanesCovered,
      cards: totalCards,
      cardsWithEpic,
      cardsWithKr,
      orphanEpics,
    },
  };
}

// ─── Renderer ───────────────────────────────────────────────────────────────

const CARD_FLAG = (ok) => (ok ? '✅' : '⚠');

export function renderStatus(diff, { stamp }) {
  let out = `<!-- Автоген gen-sync-status.mjs — руками не правится. -->\n`;
  out += `# GANTT-SYNC-STATUS — сверка покрытия GANTT ↔ OKR ↔ JIRA\n\n`;
  out += `> Read-model. GANTT (владелец, GanttPRO) — скелет; KR и JIRA сверяются с ним. Обновлено: ${stamp}.\n`;
  out += `> ✅ покрыто · ⚠ разрыв. Разбирай по списку «## Дрейф» как по чеклисту.\n\n`;

  for (const s of diff.tree) {
    const initTxt = s.initiative ? `→ Инициатива ${s.initiative} ${CARD_FLAG(s.initiativeOk)}` : `→ ⚠ инициатива не в mapping`;
    out += `## Свимлейн: ${s.swimlane}  ${initTxt}\n`;
    for (const c of s.cards) {
      const sp = c.sprints?.length ? `[S${c.sprints[0]}${c.sprints.length > 1 ? '-S' + c.sprints[c.sprints.length - 1] : ''}] ` : '';
      const krTxt = c.kr ? `(KR ${c.kr})` : '(⚠ без KR)';
      const epicTxt = c.epics.length ? `→ ${c.epics.join(', ')} ${CARD_FLAG(c.epicsOk)}` : '→ ⚠ эпик TODO';
      out += `- ${sp}${c.name}  ${krTxt}  ${epicTxt}\n`;
    }
    out += `\n`;
  }

  out += `## Дрейф (плоский список для разбора)\n`;
  if (!diff.drift.length) out += `_разрывов нет_\n`;
  for (const d of diff.drift) out += `⚠ ${d.msg}\n`;
  out += `\n`;

  const s = diff.summary;
  out += `## Сводка\n`;
  out += `Свимлейнов: ${s.swimlanes} (покрыто инициативами ${s.swimlanesCovered})\n`;
  out += `Карточек: ${s.cards} (с эпиком ${s.cardsWithEpic}, с KR ${s.cardsWithKr})\n`;
  out += `Эпиков-сирот: ${s.orphanEpics}\n`;
  return out;
}

// ─── issues loader (только из файла; сбор из JIRA — на стороне skill через MCP) ──

export function loadIssues(issuesFile) {
  const arr = JSON.parse(readFileSync(issuesFile, 'utf8'));
  const issues = Array.isArray(arr) ? arr : (arr.issues || []);
  return indexJira(issues);
}

// ─── CLI entry ───────────────────────────────────────────────────────────────

function argVal(argv, flag) {
  const i = argv.indexOf(flag);
  return i !== -1 ? argv[i + 1] : null;
}

function main() {
  const argv = process.argv.slice(2);
  const dry = argv.includes('--dry');
  const xlsx = argVal(argv, '--xlsx');
  const mapPath = argVal(argv, '--map');
  const issuesFile = argVal(argv, '--issues');
  const outFile = argVal(argv, '--out');
  const anchorsJson = argVal(argv, '--anchors');

  const missing = [];
  if (!xlsx) missing.push('--xlsx <GanttPRO.xlsx>');
  if (!mapPath) missing.push('--map <KR-EPIC-MAP.md>');
  if (!issuesFile) missing.push('--issues <issues.json> (собирает skill через MCP)');
  if (!dry && !outFile) missing.push('--out <GANTT-SYNC-STATUS.md> (или --dry)');
  if (missing.length) {
    console.error('Нужны аргументы:\n  ' + missing.join('\n  '));
    process.exit(1);
  }

  const anchors = anchorsJson ? { ...ANCHORS, ...JSON.parse(anchorsJson) } : ANCHORS;
  const mapMd = readFileSync(mapPath, 'utf8');

  const gantt = parseGantt(readSheetRows(xlsx, anchors), anchors);
  const map = parseMap(mapMd);
  const swimMap = parseSwimlaneMap(mapMd);
  const jira = loadIssues(issuesFile);
  const diff = diffCoverage({ gantt, map, swimMap, jira });
  const stamp = new Date().toISOString().slice(0, 10);
  const md = renderStatus(diff, { stamp });

  if (dry) { console.log(md); return; }
  writeFileSync(outFile, md);
  console.error(`OK → ${outFile}`);
  console.error(`Дрейф-пунктов: ${diff.drift.length}; эпиков-сирот: ${diff.summary.orphanEpics}`);
}

// запуск как CLI (не при импорте из теста)
import { fileURLToPath } from 'node:url';
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  try { main(); } catch (e) { console.error('ОШИБКА:', e.message); process.exit(1); }
}
