export const meta = {
  name: 'po-context-research',
  description: 'Deep Research сбор контекста PO по топику → context-pack.md (Perplexity-loop, read-only)',
  phases: [
    { title: 'Plan', detail: 'декомпозиция топика в sub-Q по пресету домена' },
    { title: 'Research', detail: 'multi-query sweep по источникам, per sub-Q' },
    { title: 'Critic', detail: 'coverage + follow-the-lead + contradiction → новые sub-Q' },
    { title: 'Verify', detail: 'skeptic: refuters, kill ≥2/3' },
    { title: 'Synthesize', detail: 'сборка context-pack.md (barrier)' },
  ],
}

// ── Вход ───────────────────────────────────────────────────────────────────
// args = { domain, topic, tier, seed? }
//   domain ∈ sprint|epic|bft|risk|decision
//   topic  = id топика (sprint-id / jira_key / epic_code+key / risk-id)
//   tier   ∈ High|Med|Low  (default Med) — budget-tier ← confidence KR
//   seed   = объект Phase 0 (опрос PO): { intent, hypotheses[], scope, priorities[], risks[], known_anchors[] }
//            если нет → planner работает автономно по пресету
// args может прийти объектом или JSON-строкой — нормализуем
let _args = args
if (typeof _args === 'string') { try { _args = JSON.parse(_args) } catch { _args = {} } }
const domain = _args && _args.domain
const topic = _args && _args.topic
const tier = (_args && _args.tier) || 'Med'
const seed = (_args && _args.seed) || null
if (!domain || !topic) throw new Error(`po-context-research: args требует { domain, topic, tier?, seed? } | got=${JSON.stringify(args)}`)

const RES = '.claude/skills/po-research/resources'
const OUT = `{research_workspace}/context-pack.md`

// budget-tier параметры (spec §6.2)
const TIERS = {
  // verifyCap = потолок findings на skeptic-фазу: защитить от agent-cap (1000), т.к.
  // Verify = findings × refuters и findings копятся по раундам. См. фикс ниже.
  High: { maxRounds: 4, refuters: 3, compute: true, coverageDefault: 0.80, verifyCap: 220 },
  Med: { maxRounds: 2, refuters: 1, compute: false, coverageDefault: 0.80, verifyCap: 300 },
  Low: { maxRounds: 1, refuters: 0, compute: false, coverageDefault: 0.75, verifyCap: 0 },
}
const T = TIERS[tier] || TIERS.Med
const DRY_LIMIT = 2 // loop-until-dry K=2

// ── Схемы структурированного вывода ──────────────────────────────────────────
const PLAN_SCHEMA = {
  type: 'object',
  required: ['sections', 'coverageThreshold', 'subQuestions'],
  properties: {
    sections: { type: 'array', items: { type: 'string' }, description: 'оси coverage-матрицы (разделы домена)' },
    coverageThreshold: { type: 'number', description: 'порог покрытия 0..1 из пресета' },
    subQuestions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['question', 'sources', 'section'],
        properties: {
          question: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' }, description: 'id источников: jira|conf|code|vault|web|compute' },
          section: { type: 'string', description: 'к какому разделу pack относится' },
        },
      },
    },
    availableRoles:   { type: 'array', items: { type: 'string' }, description: 'роли available по role_bindings' },
    unavailableRoles: { type: 'array', items: { type: 'string' }, description: 'роли не привязаны / не отвечают' },
    policyMissing:    { type: 'array', items: { type: 'string' }, description: 'required-роли класса research-deep, которых нет в available' },
  },
}

const FINDING = {
  type: 'object',
  required: ['fact', 'source', 'anchor', 'confidence', 'section'],
  properties: {
    fact: { type: 'string' },
    source: { type: 'string' },
    anchor: { type: 'string' },
    confidence: { type: 'string', enum: ['High', 'Med', 'Low'] },
    freshness: { type: 'string' },
    excerpt: { type: 'string' },
    section: { type: 'string' },
    queries: { type: 'array', items: { type: 'string' } },
  },
}
const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['findings'],
  properties: {
    findings: { type: 'array', items: FINDING },
    unresolved: { type: 'array', items: { type: 'string' }, description: 'что не нашлось → [УТОЧНИТЬ]' },
  },
}

const CRITIC_SCHEMA = {
  type: 'object',
  required: ['coveragePct', 'newSubQuestions', 'contradictions'],
  properties: {
    coveragePct: { type: 'number', description: 'covered_sections / total * 100' },
    coveredSections: { type: 'array', items: { type: 'string' } },
    newSubQuestions: {
      type: 'array',
      description: 'gap-driven + follow-the-lead (новые сущности/неизвестности)',
      items: {
        type: 'object',
        required: ['question', 'sources', 'section', 'kind'],
        properties: {
          question: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' } },
          section: { type: 'string' },
          kind: { type: 'string', enum: ['gap', 'follow-the-lead'] },
          entity: { type: 'string', description: 'для follow-the-lead: ключ/pageId/symbol сущности' },
        },
      },
    },
    contradictions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['aspect', 'sideA', 'sideB'],
        properties: {
          aspect: { type: 'string' },
          sideA: { type: 'string' }, // "JIRA: X [anchor] conf"
          sideB: { type: 'string' },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  required: ['refuted', 'reason'],
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string', enum: ['anchor-not-confirmed', 'contradicts-other-source', 'stale', 'sensor-mismatch', 'holds'] },
    note: { type: 'string' },
  },
}

// ── PLAN ─────────────────────────────────────────────────────────────────────
// seed из Phase 0 (опрос PO). Если есть — planner приоритизирует декомпозицию
// вокруг образа результата PO, а не автономно по пресету.
const seedBlock = seed
  ? `SEED от PO (образ результата из Phase 0 — приоритизируй декомпозицию вокруг него, НЕ автономно):
${JSON.stringify(seed)}
Правила использования seed:
- intent/hypotheses → sub-Q строятся чтобы проверить/раскрыть их; это приоритет над дефолтом пресета.
- known_anchors (${(seed.known_anchors || []).join(', ') || '—'}) → стартовые сущности: добавь по sub-Q на каждый якорь, не покрытый пресетом; это старт для follow-the-lead (G1) и entity-queue (G3).
- risks → отдельный sub-Q на каждый риск PO, не покрытый пресетом.
- scope → НЕ выходи за границы PO; вне-скоуп не порождает sub-Q.
- Пустые поля seed → fallback на дефолт пресета (автономно по этому полю).`
  : 'SEED от PO отсутствует — декомпозируй автономно по пресету домена.'

phase('Plan')
const plan = await agent(
  `Ты — planner po-research. Домен="${domain}", топик="${topic}".
Прочитай пресет домена в ${RES}/domains.md (источники, seed sub-Q, разделы pack, порог coverage) и контракт источников в ${RES}/source-registry.md.
Прочитай role_bindings + source_policy из .claude/domain-profile.md. Резолв: роль available, если есть в role_bindings И её tools доступны в сессии; иначе unavailable. Из sources каждого sub-Q ИСКЛЮЧИ unavailable-роли (не гоняем мёртвые источники). source_policy класс research-deep: policyMissing = required \\ available. Верни availableRoles, unavailableRoles, policyMissing.
${seedBlock}
Декомпозируй топик в 3–7 атомарных sub-Q. Каждому — subset источников из пресета и раздел pack. Если seed есть — приоритет sub-Q вокруг intent/hypotheses/known_anchors PO.
Верни sections (оси coverage), coverageThreshold (0..1 из пресета), subQuestions. READ-ONLY.`,
  { schema: PLAN_SCHEMA, phase: 'Plan' }
)

const sections = plan.sections
const threshold = (plan.coverageThreshold || T.coverageDefault)
log(`Plan: ${plan.subQuestions.length} sub-Q, ${sections.length} разделов, порог ${Math.round(threshold * 100)}%, tier ${tier}${seed ? ', seed=PO ✅' : ', seed=—'}`)
if (plan.unavailableRoles && plan.unavailableRoles.length) {
  log(`Capability: недоступны роли [${plan.unavailableRoles.join(', ')}] → их разделы → [НЕДОСТУПНО]`)
}
if (plan.policyMissing && plan.policyMissing.length) {
  log(`⚠️ policy(research-deep): не хватает required [${plan.policyMissing.join(', ')}] (on_missing_required=warn → продолжаю, флаг в pack)`)
}

// ── RESEARCH (multi-query) ───────────────────────────────────────────────────
function research(q) {
  const computeNote = T.compute
    ? 'Compute разрешён (только read-whitelist из source-registry.md: playwright browser_navigate/snapshot, serena find_*, Bash read-команды).'
    : 'Compute ВЫКЛ для этого tier.'
  return agent(
    `Ты — researcher po-research (READ-ONLY). Sub-Q: "${q.question}". Раздел: "${q.section}". Источники: ${(q.sources || []).join(', ')}.
Multi-query sweep (G2): на каждый источник 2–3 переформулировки запроса, мерджи dedupe по anchor.
Tools резолвь по role_bindings (.claude/domain-profile.md): роль источника → MCP-сервер сотрудника. Дефолт-маппинг: jira→jira_*, conf→confluence_*, code→repowise(get_answer,get_context,get_risk,get_why,search_codebase), vault→obsidian(search_query,vault_read), web→WebSearch/WebFetch. Кастом-коннектор (развёрнутая форма role_bindings) → его явные tools. Сервер не отвечает → раздел [НЕДОСТУПНО], не выдумывать. ${computeNote}
Каждый факт — с якорем + confidence + freshness + excerpt. Нет якоря → в unresolved. Не выдумывать.`,
    { schema: FINDINGS_SCHEMA, phase: 'Research', label: `research:${q.section}` }
  )
}

// ── LOOP: research → critic → (gap + follow-the-lead + entity-queue) ─────────
const allFindings = []
const unresolved = []
const contradictions = []
const seen = new Set()
const seenEntities = new Set()
let queue = plan.subQuestions.slice()
let round = 0
let dry = 0

while (queue.length && round < T.maxRounds && dry < DRY_LIMIT) {
  round++
  phase('Research')
  const batch = await parallel(queue.map((q) => () => research(q)))
  const ok = batch.filter(Boolean)
  ok.forEach((r) => (r.unresolved || []).forEach((u) => unresolved.push(u)))

  const fresh = ok
    .flatMap((r) => r.findings || [])
    .filter((f) => {
      const k = f.anchor + '|' + f.fact
      if (seen.has(k)) return false
      seen.add(k)
      return true
    })
  allFindings.push(...fresh)
  dry = fresh.length === 0 ? dry + 1 : 0

  phase('Critic')
  const critic = await agent(
    `Ты — critic po-research. Разделы (оси): ${JSON.stringify(sections)}.
Findings на данный момент:
${JSON.stringify(allFindings.map((f) => ({ section: f.section, fact: f.fact, source: f.source, anchor: f.anchor, confidence: f.confidence })))}
1) coveragePct = covered_sections / ${sections.length} * 100 (раздел covered, если есть ≥1 finding с якорем).
2) newSubQuestions: (а) gap — раздел без источника; (б) follow-the-lead (G1) — новая сущность (зависимый эпик/ADR/сервис/стейкхолдер) или новая неизвестность из findings → новый sub-Q (укажи kind и entity).
3) contradictions (G4): группируй по (section, аспект); ≥2 finding с расходящимся fact на один аспект → contradiction (sideA/sideB с якорями). Семантически, не строково.
Зависимости — hard-gate: незакрытая → НЕ закрывай раздел, оставь для [УТОЧНИТЬ].`,
    { schema: CRITIC_SCHEMA, phase: 'Critic' }
  )

  ;(critic.contradictions || []).forEach((c) => contradictions.push(c))

  // entity-queue (G3): не повторять уже обработанные сущности
  const next = (critic.newSubQuestions || []).filter((q) => {
    if (q.kind === 'follow-the-lead' && q.entity) {
      if (seenEntities.has(q.entity)) return false
      seenEntities.add(q.entity)
    }
    return true
  })

  log(`round ${round}: coverage ${Math.round(critic.coveragePct)}% / порог ${Math.round(threshold * 100)}% · +${fresh.length} findings · ${next.length} new sub-Q · dry=${dry}`)

  if (critic.coveragePct >= threshold * 100 && next.length === 0) break
  queue = next
}

// ── VERIFY (skeptic, adversarial cite-or-kill) ───────────────────────────────
phase('Verify')
// hard-cap против agent-cap (1000): findings копятся по раундам, ×refuters может превысить лимит.
// Берём топ-N по confidence/freshness на skeptic, остаток (low-conf) проходит в pack БЕЗ verify —
// ничего не теряем, экономим агентов.
const CONF_RANK = { High: 3, Med: 2, Low: 1 }
const rankFindings = (a, b) => {
  const d = (CONF_RANK[b.confidence] || 0) - (CONF_RANK[a.confidence] || 0)
  if (d) return d
  return String(b.freshness || '').localeCompare(String(a.freshness || '')) // новее раньше (rough)
}
const ranked = [...allFindings].sort(rankFindings)
const toVerify = T.verifyCap > 0 ? ranked.slice(0, T.verifyCap) : ranked
const skipped = T.verifyCap > 0 ? ranked.slice(T.verifyCap) : []
if (skipped.length) log(`Verify cap: ${allFindings.length} findings → top-${toVerify.length} на skeptic, ${skipped.length} low-conf без verify`)

let verified = allFindings
let killed = []
if (T.refuters > 0 && toVerify.length) {
  const killThreshold = Math.ceil((T.refuters * 2) / 3) // ≥2/3
  const judged = await parallel(
    toVerify.map((f) => () =>
      parallel(
        Array.from({ length: T.refuters }, (_, i) => () =>
          agent(
            `Ты — refuter #${i + 1} (skeptic). Попытайся ОПРОВЕРГНУТЬ факт.
Факт: "${f.fact}"  | source: ${f.source} | anchor: ${f.anchor} | conf: ${f.confidence}
Перечитай источник по якорю. Способы refute: якорь не подтверждается / противоречит другому источнику / устарел (freshness) / сенсор источника не покрывает утверждение.
default=refuted=true, если НЕ уверен. READ-ONLY.`,
            { schema: VERDICT_SCHEMA, phase: 'Verify', label: `refute:${f.source}` }
          )
        )
      ).then((votes) => {
        const refutes = votes.filter(Boolean).filter((v) => v.refuted).length
        return { ...f, _killed: refutes >= killThreshold, _refutes: refutes }
      })
    )
  )
  verified = judged.filter((f) => f && !f._killed)
  killed = judged.filter((f) => f && f._killed)
}
// low-conf findings минуют skeptic → идут в pack как есть (unverified), ничего не теряем
const skippedClean = skipped.map((f) => ({ ...f, _skipped: true }))
verified = verified.concat(skippedClean)

// ── SYNTHESIZE (barrier) ─────────────────────────────────────────────────────
phase('Synthesize')
const verifiedClean = verified.map((f) => ({
  section: f.section, fact: f.fact, source: f.source, anchor: f.anchor,
  confidence: f.confidence, freshness: f.freshness, excerpt: f.excerpt,
}))
const pack = await agent(
  `Ты — synthesizer po-research. Собери context-pack.md строго по шаблону ${RES}/pack-template.md и запиши в ${OUT} (создай папки; используй Write).
meta: domain=${domain} | режим=Deep | budget-tier=${tier} | seed=${seed ? 'PO ✅ (Phase 0)' : '— (автономно)'} | дата=<сегодня> | статус источников=<VPN ✅/⚠️>.
Coverage-matrix по resources/pack-template.md с колонками required?/available?/used?. Недоступные роли (${(plan.unavailableRoles || []).join(', ') || 'нет'}) → строки [НЕДОСТУПНО: роль <id>]. policyMissing → флаг в шапке pack.
CORTEX-фон: подключи релевантное из CORTEX/ ссылкой+выдержкой (по теме топика, не целиком).
NEXUS (verified findings, с якорями):
${JSON.stringify(verifiedClean)}
Contradictions (обе стороны, если обе confidence ≥Med; иначе High + Low как [УТОЧНИТЬ]):
${JSON.stringify(contradictions)}
Coverage Matrix: оси = ${JSON.stringify(sections)}; статус раздела по наличию источника; порог ${Math.round(threshold * 100)}%; зависимости — hard-gate.
Evidence Quality: verified=${verified.length - skippedClean.length}, unverified_low_conf=${skippedClean.length}, killed_by_skeptic=${killed.length}.
Требует уточнения (что/как проверить/кто): ${JSON.stringify(unresolved)}.
Жёстко: нет факта без якоря → [УТОЧНИТЬ]. READ-ONLY на источники.`,
  { phase: 'Synthesize' }
)

return {
  artifact: OUT,
  stats: {
    domain, topic, tier, seedDriven: !!seed, rounds: round,
    findings: allFindings.length, verified: verified.length,
    unverifiedLowConf: skippedClean.length, killed: killed.length, verifyCap: T.verifyCap,
    contradictions: contradictions.length, unresolved: unresolved.length,
    coverageThreshold: threshold,
  },
  pack,
}
