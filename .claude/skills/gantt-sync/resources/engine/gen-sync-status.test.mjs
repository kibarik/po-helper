import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { parseSheetXml, decodeCell, colNum, cardBars, phaseClass, parseGantt, hasCardContent, parseMap, parseSwimlaneMap, normalizeIssue, indexJira, diffCoverage, renderStatus } from './gen-sync-status.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const sampleXml = readFileSync(join(__dirname, 'fixtures/sheet-sample.xml'), 'utf8');
const mapSample = readFileSync(join(__dirname, 'fixtures/map-sample.md'), 'utf8');

test('decodeCell: сущности и переносы', () => {
  assert.equal(decodeCell('SA&#183;ADR'), 'SA·ADR');
  assert.equal(decodeCell('A &amp; B'), 'A & B');
  assert.equal(decodeCell('line1\nline2'), 'line1 line2');
});

test('parseSheetXml: строки и ячейки', () => {
  const rows = parseSheetXml(sampleXml);
  const byNum = Object.fromEntries(rows.map((r) => [r.r, r.cells]));
  assert.equal(byNum[3].A, 'Инициативы в квартале');
  assert.equal(byNum[5].A, 'Тест-свимлейн');
  assert.equal(byNum[6].A, 'Тест-карточка & X');
  assert.equal(byNum[6].B, 'SA·ADR');
  assert.equal(byNum[6].H, 'RM');
  assert.equal(byNum[48].A, 'Легенда фаз:');
});

test('colNum: буква колонки в номер', () => {
  assert.equal(colNum('A'), 1);
  assert.equal(colNum('B'), 2);
  assert.equal(colNum('O'), 15);
});

test('phaseClass: класс по коду фазы', () => {
  assert.equal(phaseClass('SA·ADR'), 'analytics');
  assert.equal(phaseClass('BE·Go'), 'dev');
  assert.equal(phaseClass('QA'), 'qa');
  assert.equal(phaseClass('RM'), 'release');
});

test('cardBars: спринты и фазы по ячейкам', () => {
  const bars = cardBars({ A: 'x', B: 'SA·ADR', H: 'RM' });
  assert.deepEqual(bars.map((b) => b.sprint), [1, 4]);
  assert.deepEqual(bars.map((b) => b.phase), ['analytics', 'release']);
});

test('parseGantt: свимлейны с карточками, шапка и легенда отсечены', () => {
  const rows = parseSheetXml(sampleXml);
  const g = parseGantt(rows);
  assert.equal(g.swimlanes.length, 1);
  assert.equal(g.swimlanes[0].name, 'Тест-свимлейн');
  assert.equal(g.swimlanes[0].cards.length, 1);
  const card = g.swimlanes[0].cards[0];
  assert.equal(card.name, 'Тест-карточка & X');
  assert.deepEqual(card.sprints, [1, 4]);
});

test('parseGantt: строка только с колонкой P — карточка вне квартала, не свимлейн', () => {
  const rows = [
    { r: 5, cells: { A: 'Свимлейн' } },
    { r: 6, cells: { A: 'Обычная карточка', B: 'SA·ADR' } },
    { r: 7, cells: { A: 'Карточка вне квартала', P: 'вне квартала' } },
  ];
  const g = parseGantt(rows);
  assert.equal(g.swimlanes.length, 1);
  assert.equal(g.swimlanes[0].cards.length, 2);
  const ooq = g.swimlanes[0].cards[1];
  assert.equal(ooq.name, 'Карточка вне квартала');
  assert.equal(ooq.outOfQuarter, true);
  assert.deepEqual(ooq.sprints, []);
});

test('parseMap: slug из последней колонки, эпики, uncertain', () => {
  const rows = parseMap(mapSample);
  assert.equal(rows.length, 3);
  assert.equal(rows[0].slug, 'card-alpha');
  assert.deepEqual(rows[0].epics, ['DEMO-101']);
  assert.deepEqual(rows[1].epics, []); // TODO → нет эпиков
  assert.equal(rows[2].uncertain, true);
  assert.deepEqual(rows[2].epics, ['DEMO-201', 'DEMO-202']);
});

test('parseSwimlaneMap: свимлейн → инициатива', () => {
  const sm = parseSwimlaneMap(mapSample);
  assert.equal(sm.length, 2);
  assert.equal(sm[0].swimlane, 'Свимлейн Один');
  assert.equal(sm[0].initiative, 'DEMO-1');
});

const jiraSample = JSON.parse(readFileSync(join(__dirname, 'fixtures/jira-sample.json'), 'utf8'));

test('normalizeIssue: raw REST форма', () => {
  const n = normalizeIssue(jiraSample[0]);
  assert.equal(n.key, 'DEMO-1');
  assert.equal(n.type, 'Инициатива');
  assert.equal(n.status, 'В работе');
});

test('indexJira: классификация инициатив и эпиков', () => {
  const idx = indexJira(jiraSample);
  assert.deepEqual(idx.initiatives.map((i) => i.key), ['DEMO-1']);
  assert.deepEqual(idx.epics.map((e) => e.key).sort(), ['DEMO-101', 'DEMO-999']);
});

test('normalizeIssue: MCP jira_search форма (issue_type + status.category)', () => {
  const mcp = { key: 'DEMO-101', issue_type: { name: 'Epic' }, summary: 'x', status: { name: 'Бэклог', category: 'К выполнению' } };
  const n = normalizeIssue(mcp);
  assert.equal(n.type, 'Epic');
  assert.equal(n.status, 'Бэклог');
  const idx = indexJira([mcp]);
  assert.deepEqual(idx.epics.map((e) => e.key), ['DEMO-101']);
});

test('diffCoverage: покрытие и дрейф на двух высотах', () => {
  const gantt = { swimlanes: [
    { name: 'Свимлейн Один', r: 5, cards: [
      { name: 'Карточка Альфа', r: 6, sprints: [1], phases: ['analytics'] },
      { name: 'Карточка без KR', r: 7, sprints: [2], phases: ['dev'] },
    ] },
  ] };
  const map = [
    { kr: '1.1', name: 'Карточка Альфа', gantt: 'Ц1', epics: ['DEMO-101'], slug: 'card-alpha', uncertain: false },
    { kr: '4.2', name: 'Карточка Дельта', gantt: 'Ц4', epics: [], slug: 'card-delta', uncertain: false },
  ];
  const swimMap = [{ swimlane: 'Свимлейн Один', initiative: 'DEMO-1' }];
  const jira = indexJira([
    { key: 'DEMO-1', fields: { issuetype: { name: 'Инициатива' }, summary: 'x', status: { name: 'В работе' } } },
    { key: 'DEMO-101', fields: { issuetype: { name: 'Эпик' }, summary: 'y', status: { name: 'Бэклог' } } },
    { key: 'DEMO-999', fields: { issuetype: { name: 'Эпик' }, summary: 'сирота', status: { name: 'Открыт' } } },
  ]);

  // Карточки xlsx привязываются к mapping по name; slug приходит из mapping.
  const d = diffCoverage({ gantt, map, swimMap, jira });

  // свимлейн покрыт инициативой DEMO-1
  assert.equal(d.tree[0].initiative, 'DEMO-1');
  assert.equal(d.tree[0].initiativeOk, true);

  // дрейф: карточка без KR (r7), эпик-сирота DEMO-999, KR 4.2 без карточки в GANTT
  const kinds = d.drift.map((x) => x.kind);
  assert.ok(kinds.includes('card-no-kr'));
  assert.ok(kinds.includes('orphan-epic'));
  assert.ok(kinds.includes('kr-no-card'));

  assert.equal(d.summary.orphanEpics, 1);
});

test('diffCoverage: эпик в mapping без GANTT-карточки — НЕ сирота; не-mapping эпик — сирота', () => {
  // Карточка "Карточка Альфа" привязана к KR 1.1 + DEMO-101.
  // KR 2.1 привязан к DEMO-200, но у него НЕТ карточки в GANTT.
  // DEMO-999 не фигурирует ни в каком mapping-row — истинная сирота.
  const gantt = { swimlanes: [
    { name: 'Свимлейн Один', r: 5, cards: [
      { name: 'Карточка Альфа', r: 6, sprints: [1], phases: ['analytics'] },
    ] },
  ] };
  const map = [
    { kr: '1.1', name: 'Карточка Альфа', gantt: 'Ц1', epics: ['DEMO-101'], slug: '', uncertain: false },
    // 2.1: mapping-row есть, карточки в GANTT нет
    { kr: '2.1', name: 'Интеграция', gantt: '', epics: ['DEMO-200'], slug: '', uncertain: false },
  ];
  const swimMap = [{ swimlane: 'Свимлейн Один', initiative: 'DEMO-1' }];
  const jira = indexJira([
    { key: 'DEMO-1', fields: { issuetype: { name: 'Инициатива' }, summary: 'x', status: { name: 'В работе' } } },
    { key: 'DEMO-101', fields: { issuetype: { name: 'Эпик' }, summary: 'y', status: { name: 'Бэклог' } } },
    { key: 'DEMO-200', fields: { issuetype: { name: 'Эпик' }, summary: 'интеграция', status: { name: 'Открыт' } } },
    { key: 'DEMO-999', fields: { issuetype: { name: 'Эпик' }, summary: 'сирота', status: { name: 'Открыт' } } },
  ]);

  const d = diffCoverage({ gantt, map, swimMap, jira });
  const orphanKeys = d.drift.filter((x) => x.kind === 'orphan-epic').map((x) => x.msg);

  // DEMO-200 есть в mapping-row (2.1), значит — НЕ сирота
  assert.ok(!orphanKeys.some((m) => m.includes('DEMO-200')), 'DEMO-200 не должен быть в orphan-epic');
  // DEMO-999 НЕ в mapping нигде — истинная сирота
  assert.ok(orphanKeys.some((m) => m.includes('DEMO-999')), 'DEMO-999 должен быть в orphan-epic');
  // Счётчик: только 1 реальная сирота
  assert.equal(d.summary.orphanEpics, 1);
});

test('renderStatus: дерево, дрейф, сводка', () => {
  const diff = {
    tree: [
      { swimlane: 'Свимлейн Один', initiative: 'DEMO-1', initiativeOk: true, cards: [
        { name: 'Карточка Альфа', slug: 'card-alpha', kr: '1.1', epics: ['DEMO-101'], epicsOk: true, krOk: true, sprints: [1, 2] },
      ] },
    ],
    drift: [{ level: 'mid', kind: 'orphan-epic', msg: 'эпик DEMO-999 — открыт, ни к одной карточке (scope creep)' }],
    summary: { swimlanes: 1, swimlanesCovered: 1, cards: 1, cardsWithEpic: 1, cardsWithKr: 1, orphanEpics: 1 },
  };
  const md = renderStatus(diff, { stamp: '2026-07-13' });
  assert.match(md, /## Свимлейн: Свимлейн Один.*DEMO-1 ✅/);
  assert.match(md, /Карточка Альфа/);
  assert.match(md, /DEMO-101 ✅/);
  assert.match(md, /## Дрейф/);
  assert.match(md, /эпик DEMO-999/);
  assert.match(md, /## Сводка/);
  assert.match(md, /Свимлейнов: 1/);
  assert.match(md, /руками не правится/); // предупреждение-шапка
});
