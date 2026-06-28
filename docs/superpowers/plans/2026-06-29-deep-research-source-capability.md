# Deep-research source-capability layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Дать deep-research явный, записанный слой «роль-источника → коннектор сотрудника» + минимальную policy, переиспользуя `.mcp.json` и существующую деградацию, без скилл-мастера и отдельного capability-профиля.

**Architecture:** `.mcp.json` (готовое, не трогаем) = инвентарь коннекторов. Добавляем тонкий семантический слой: секции `role_bindings` + `source_policy` в `domain-profile.md`, рефактор `source-registry.md` (роли connector-agnostic, tools резолвятся из bindings), преамбулу «Resolve capability» в трёх потребителях (po-research SKILL, bft-context-gen-deep, workflow). Недоступные роли деградируют через уже существующий паттерн `[НЕДОСТУПНО]` + coverage-matrix.

**Tech Stack:** Markdown prompt-файлы (Claude Code skills/commands), YAML-конфиг (domain-profile), JS workflow (Workflow-харнес, Node 25). **Не классический TDD** — артефакты декларативные: верификация = YAML-parse примеров (`python3`+pyyaml), consistency-grep по ключам, `node --check` для workflow.

**Решение по неймингу (рефинмент спеки):** id источников `jira|conf|code|vault|web|vision|compute` ОСТАЮТСЯ как ключи ролей (уже абстракция в workflow-схемах, `domains.md`, `pack-template`). Connector-agnostic достигается через `role_bindings` (id→сервер), без rename по 5 файлам. `jira`=роль tracker, `conf`=роль wiki (документируется в registry).

---

## File Structure

| Файл | Ответственность | Действие |
|---|---|---|
| `domain-profile.template.md` | декларация `role_bindings` + `source_policy` (семантический слой + policy) | Modify |
| `.claude/skills/po-research/resources/source-registry.md` | каталог ролей connector-agnostic; tools ← bindings | Modify |
| `.claude/skills/po-research/resources/pack-template.md` | coverage-matrix с колонками capability | Modify |
| `.claude/skills/po-research/SKILL.md` | преамбула «Resolve capability» (Fast + Deep) | Modify |
| `.claude/commands/bft-context-gen-deep.md` | этап «Resolve capability» перед субагентами | Modify |
| `.claude/workflows/po-context-research.js` | planner резолвит bindings/policy, researcher по resolved-tools | Modify |
| `install.sh` | финальная подсказка заполнить `role_bindings` | Modify |

Порядок задач: сначала декларации (1–3), затем потребители (4–6), затем onboarding-подсказка (7). Каждая задача — самодостаточный коммит.

---

### Task 1: `role_bindings` + `source_policy` в шаблоне профиля

**Files:**
- Modify: `domain-profile.template.md` (после секции «## 4a. База знаний / кортексы (cortex)», перед «### BFT-дефолты»)

- [ ] **Step 1: Вставить секцию `role_bindings`**

Добавь новую секцию `## 4b` сразу после блока `cortex:` (строка с `sa_store: "CORTEX/SA/"` и закрывающим ```` ``` ````):

````markdown
## 4b. Привязка ролей к коннекторам (role_bindings) — для deep-research

Семантический слой: какая роль-источник каким MCP-сервером из `.mcp.json` обслуживается.
`.mcp.json` знает «есть сервер `atlassian`», но не знает, что он играет роль `jira`/`conf`.
Эту привязку объявляем здесь. Settings (base_url/space/projects) НЕ дублируются — берутся
из секций `tracker:`/`wiki:`/`cortex:` выше.

```yaml
role_bindings:
  jira:    atlassian            # роль tracker; settings ← секция tracker:
  conf:    atlassian            # роль wiki;    settings ← секция wiki:
  code:    repowise             # свой RAG-сервер → впиши его имя (напр. my-internal-rag)
  vault:   obsidian
  web:     builtin              # WebSearch / WebFetch (встроенные, не из .mcp.json)
  vision:  atlassian            # confluence_get_page_images
  compute: [playwright, serena, bash]
  # роль НЕ указана  =>  недоступна (её раздел pack → [НЕДОСТУПНО])
```

Кастом-коннектор с нестандартными tool-именами/якорем — развёрнутая форма:

```yaml
role_bindings:
  code:
    mcp:    my-internal-rag     # имя сервера из .mcp.json
    tools:  [rag_query, rag_context]
    anchor: symbol_id
```

Подключить новый источник (D): добавь сервер в `.mcp.json` + одну строку сюда. Скиллы не трогаются.
````

- [ ] **Step 2: Вставить секцию `source_policy`**

Сразу после `role_bindings` добавь:

````markdown
## 4c. Минимум источников по классу (source_policy) — governance

Обязательные роли для класса исследования. Deep-research сверяет `required ∩ available`;
недостающую required-роль — warn/block (по `on_missing_required`) + явно в coverage-matrix.

```yaml
source_policy:
  on_missing_required: warn     # warn (продолжить, флаг в pack) | block (СТОП со списком)
  classes:
    bft-critical:  [jira, conf] # /bft-context-gen-deep
    bft-normal:    [jira]       # /bft-context-gen (быстрый)
    research-deep: [jira, conf] # /po-research deep
    research-fast: [jira]       # /po-research fast
```

Роль из `required` отсутствует в `role_bindings` или сервер не отвечает → срабатывает политика.
````

- [ ] **Step 3: Верифицировать, что YAML-блоки парсятся**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && python3 - <<'PY'
import re, yaml
t = open('domain-profile.template.md').read()
for name in ['role_bindings', 'source_policy']:
    m = re.search(r'```yaml\n(' + name + r':.*?)\n```', t, re.S)
    assert m, f'НЕТ блока {name}'
    obj = yaml.safe_load(m.group(1))
    assert name in obj, f'{name} не корневой ключ'
print('OK: role_bindings + source_policy парсятся')
PY
```
Expected: `OK: role_bindings + source_policy парсятся`

- [ ] **Step 4: Commit**

```bash
git add domain-profile.template.md
git commit -m "feat(profile): add role_bindings + source_policy sections for deep-research capability"
```

---

### Task 2: Рефактор `source-registry.md` — роли connector-agnostic

**Files:**
- Modify: `.claude/skills/po-research/resources/source-registry.md`

- [ ] **Step 1: Заменить вводную строку (убрать хардкод-предположение)**

Найди строку:
```markdown
> Реестр источников. Каждый источник = `{id, tools, extract, anchor}`. **Tool-имена проверены в env (v0.2).** Нет источника на факт → `[УТОЧНИТЬ]`. Все операции — **read-only**.
```
Замени на:
```markdown
> Реестр **ролей-источников**. Каждая роль = `{id, intent, extract, anchor}`. Конкретные tool-имена НЕ хардкодятся здесь — резолвятся из `role_bindings` в `.claude/domain-profile.md` (роль `id` → MCP-сервер сотрудника). Колонка `tools (дефолт)` — типовая привязка, если `role_bindings` не переопределяет. Нет источника на факт → `[УТОЧНИТЬ]`. Все операции — **read-only**.
```

- [ ] **Step 2: Переименовать колонку и пояснить роли в таблице**

Найди заголовок таблицы:
```markdown
| id | source | tools (проверены) | extract | anchor |
```
Замени на:
```markdown
| id (роль) | source | tools (дефолт, override ← role_bindings) | extract | anchor |
```
И в строке `jira` замени ячейку source `трекер (`tracker.base_url`)` на `трекер / роль tracker`; в строке `conf` замени `Confluence` на `wiki / роль conf`. Остальные строки не трогай.

- [ ] **Step 3: Добавить раздел про резолв через role_bindings**

После таблицы «## Источники», перед «## Finding-объект», вставь:
```markdown
## Резолв роли → коннектор (role_bindings)

Tool-имена строки выше — **дефолт**. Реальный сервер берётся из `role_bindings` (`.claude/domain-profile.md`):

- `role_bindings[id]` = имя сервера (строка) → используем его tools по дефолт-маппингу роли.
- развёрнутая форма `{mcp, tools, anchor}` → используем явные tools/anchor (кастом-коннектор).
- роль НЕ в `role_bindings` → **недоступна**: её раздел pack → `[НЕДОСТУПНО: роль <id>]`, субагент по ней не спавнится.
- `web: builtin`, `compute` (playwright/serena/bash) — встроенные, available по умолчанию (кроме явного отсутствия в `role_bindings`).
```

- [ ] **Step 4: Верифицировать консистентность**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && \
grep -q "role_bindings" .claude/skills/po-research/resources/source-registry.md && \
grep -q "tools (дефолт" .claude/skills/po-research/resources/source-registry.md && \
! grep -q "Tool-имена проверены в env" .claude/skills/po-research/resources/source-registry.md && \
echo "OK: registry рефакторнут"
```
Expected: `OK: registry рефакторнут`

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/po-research/resources/source-registry.md
git commit -m "refactor(registry): roles connector-agnostic, tools resolve via role_bindings"
```

---

### Task 3: Coverage-matrix с колонками capability

**Files:**
- Modify: `.claude/skills/po-research/resources/pack-template.md`

- [ ] **Step 1: Расширить таблицу Coverage Matrix**

Найди блок:
```markdown
## Coverage Matrix
> Разделы = оси домена (см. resources/domains.md). Пример для epic:
| Раздел pack | Питающий | Статус |
|---|---|---|
| Границы | C1+N2 | ✅ |
| Образ результата (БТ) | N2+N3 | ⚠️partial |
| Зависимости | C1+N6 | [УТОЧНИТЬ] |
| … | … | … |
```
Замени на:
```markdown
## Coverage Matrix
> Разделы = оси домена (см. resources/domains.md). Колонки capability: `required?` (из source_policy класса), `available?` (роль привязана+отвечает), `used?` (дал findings). Пример для epic:
| Раздел pack | Питающий | required? | available? | used? | Статус |
|---|---|---|---|---|---|
| Границы | C1+conf | да | ✅ | ✅ | ✅ |
| Образ результата (БТ) | conf+code | да | ✅ | ⚠️ | ⚠️partial |
| Зависимости | C1+jira | да | ❌ | — | [НЕДОСТУПНО: роль jira] |
| … | … | … | … | … | … |

> Роль из `source_policy.classes[<class>]` недоступна → строка помечается `[НЕДОСТУПНО: роль <id>]`,
> и (если `on_missing_required: block`) Synthesize выводит СТОП-список вместо pack.
```

- [ ] **Step 2: Добавить правило заполнения**

В разделе «## Правила заполнения» найди пункт `4. **Coverage** — оси = разделы домена, не фикс БФТ.` и замени на:
```markdown
4. **Coverage** — оси = разделы домена, не фикс БФТ. Колонки `required?/available?/used?` — из `source_policy` + `role_bindings`. Недоступная required-роль → `[НЕДОСТУПНО: роль <id>]` в строке.
```

- [ ] **Step 3: Верифицировать**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && \
grep -q "required? | available? | used?" .claude/skills/po-research/resources/pack-template.md && \
echo "OK: coverage-matrix расширена"
```
Expected: `OK: coverage-matrix расширена`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/po-research/resources/pack-template.md
git commit -m "feat(pack): coverage-matrix capability columns (required/available/used)"
```

---

### Task 4: Преамбула «Resolve capability» в po-research SKILL

**Files:**
- Modify: `.claude/skills/po-research/SKILL.md` (вставка после «### Шаг 0. Контекст», и заметка в «### Запуск Workflow»)

- [ ] **Step 1: Вставить Шаг 0.5 (Fast)**

Сразу после блока «### Шаг 0. Контекст» (заканчивается `3. Создай {research_workspace}/.`) и перед «### Шаг 1. Plan» вставь:
```markdown
### Шаг 0.5. Resolve capability (роли → коннекторы)

Перед Gather определи доступные роли-источники у этого сотрудника:

1. Прочитай `role_bindings` из `.claude/domain-profile.md` (роль `id` → MCP-сервер / `builtin`).
2. Каждая роль пресета: привязана в `role_bindings` И её tools доступны в сессии?
   - да → **available**;
   - не привязана / сервер не отвечает → **unavailable**: её раздел pack → `[НЕДОСТУПНО: роль <id>]`, источник исключается из обхода Шага 2 (не дёргаем мёртвые tools). Не выдумывать.
3. Прочитай `source_policy`. Класс для Fast = `research-fast`. `required ∩ available`: недостающую required-роль — в отчёт (Fast: только warn, без блока).
4. В coverage-matrix (Шаг 4) проставь колонки `required?/available?/used?`.
```

- [ ] **Step 2: Добавить заметку в «### Запуск Workflow» (Deep)**

Найди в разделе «### Запуск Workflow» строку, начинающуюся `С собранным `seed` → Workflow`. Сразу ПОСЛЕ абзаца с этой строкой вставь:
```markdown
> Resolve capability в Deep делает сам Workflow (planner читает `role_bindings` + `source_policy`,
> класс = `research-deep`, исключает недоступные роли, проставляет capability-колонки coverage).
> Phase 0 здесь capability не резолвит — только seed PO.
```

- [ ] **Step 3: Верифицировать**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && \
grep -q "Шаг 0.5. Resolve capability" .claude/skills/po-research/SKILL.md && \
grep -q "класс = .research-deep." .claude/skills/po-research/SKILL.md && \
echo "OK: po-research SKILL обновлён"
```
Expected: `OK: po-research SKILL обновлён`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/po-research/SKILL.md
git commit -m "feat(po-research): Resolve-capability preamble (Fast) + Deep workflow note"
```

---

### Task 5: Этап «Resolve capability» в bft-context-gen-deep

**Files:**
- Modify: `.claude/commands/bft-context-gen-deep.md` (вставка между «### Этап 1: CORTEX» и «### Этап 2: Запуск параллельных субагентов»)

- [ ] **Step 1: Вставить этап резолва**

После блока «### Этап 1: CORTEX — читаем локальный фон» (строка `Идентично /bft-context-gen, Этап 1. ...`) и перед «### Этап 2: Запуск параллельных субагентов» вставь:
```markdown
### Этап 1.5: Resolve capability (роли → коннекторы)

Перед спавном субагентов A–E определи доступность ролей:

1. Прочитай `role_bindings` из `.claude/domain-profile.md` (роль `id` → MCP-сервер / `builtin`).
   Маппинг агентов на роли: A→`jira`, B→`conf`, C→`code`, D→`conf`+`code`, E→синтез (без своих tools).
2. Роль не привязана / сервер не отвечает → **соответствующего субагента НЕ спавним**; его раздел в pack → `[НЕДОСТУПНО: роль <id> не привязана/недоступна]`. Не выдумывать факты за недоступный источник.
3. Прочитай `source_policy`, класс = `bft-critical`. Посчитай `required ∩ available`:
   - `on_missing_required: block` → **СТОП**: «<роль> недоступна — `bft-critical` требует [jira, conf]. Проверь `.mcp.json`/`role_bindings` или используй `/bft-context-gen` (быстрый).»
   - `on_missing_required: warn` → продолжай, флаг в шапке pack и в матрице покрытия.
4. В матрице покрытия (Этап 4) добавь колонки `required?/available?/used?`.
```

- [ ] **Step 2: Связать с матрицей покрытия (Этап 4)**

В разделе «### Этап 4: Матрица покрытия (полная)» найди заголовок таблицы:
```markdown
| Раздел БФТ | Питающий источник | Агент | Статус |
```
Замени на:
```markdown
| Раздел БФТ | Питающий источник | Агент | required? | available? | used? | Статус |
```
(остальные строки таблицы оставь как есть — статус-ячейку недоступной роли заполняй `[НЕДОСТУПНО: роль <id>]`).

- [ ] **Step 3: Верифицировать**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && \
grep -q "Этап 1.5: Resolve capability" .claude/commands/bft-context-gen-deep.md && \
grep -q "класс = .bft-critical." .claude/commands/bft-context-gen-deep.md && \
grep -q "required? | available? | used?" .claude/commands/bft-context-gen-deep.md && \
echo "OK: bft-context-gen-deep обновлён"
```
Expected: `OK: bft-context-gen-deep обновлён`

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/bft-context-gen-deep.md
git commit -m "feat(bft-deep): Resolve-capability stage + policy gate before subagents"
```

---

### Task 6: Workflow — planner резолвит bindings/policy, researcher по resolved-tools

**Files:**
- Modify: `.claude/workflows/po-context-research.js` (PLAN_SCHEMA, planner-промпт, лог после plan, researcher-промпт)

- [ ] **Step 1: Расширить PLAN_SCHEMA полями capability**

Найди объявление `PLAN_SCHEMA` (около строки 95–105, объект со `properties` включающим `subQuestions`, `sections`, `coverageThreshold`). Добавь в его `properties` три поля (рядом с существующими, не ломая `required`):
```javascript
      availableRoles:   { type: 'array', items: { type: 'string' }, description: 'роли available по role_bindings' },
      unavailableRoles: { type: 'array', items: { type: 'string' }, description: 'роли не привязаны / не отвечают' },
      policyMissing:    { type: 'array', items: { type: 'string' }, description: 'required-роли класса research-deep, которых нет в available' },
```

- [ ] **Step 2: Дополнить planner-промпт резолвом capability**

Найди planner-агент (`const plan = await agent(` около строки 149). В его промпте после строки `Прочитай пресет домена в ${RES}/domains.md ... и контракт источников в ${RES}/source-registry.md.` добавь новую строку:
```javascript
Прочитай role_bindings + source_policy из .claude/domain-profile.md. Резолв: роль available, если есть в role_bindings И её tools доступны в сессии; иначе unavailable. Из sources каждого sub-Q ИСКЛЮЧИ unavailable-роли (не гоняем мёртвые источники). source_policy класс research-deep: policyMissing = required \\ available. Верни availableRoles, unavailableRoles, policyMissing.
```

- [ ] **Step 3: Логировать policy-вердикт после plan**

Найди строку `log(\`Plan: ${plan.subQuestions.length} sub-Q, ...\`)` (около строки 180). Сразу ПОСЛЕ неё добавь:
```javascript
if (plan.unavailableRoles && plan.unavailableRoles.length) {
  log(`Capability: недоступны роли [${plan.unavailableRoles.join(', ')}] → их разделы → [НЕДОСТУПНО]`)
}
if (plan.policyMissing && plan.policyMissing.length) {
  log(`⚠️ policy(research-deep): не хватает required [${plan.policyMissing.join(', ')}] (on_missing_required=warn → продолжаю, флаг в pack)`)
}
```

- [ ] **Step 4: Researcher использует resolved-tools по role_bindings**

Найди в функции `research(q)` строку промпта `Tools через ToolSearch: jira_* / confluence_* / repowise ... WebSearch,WebFetch. ${computeNote}`. Замени её на:
```javascript
Tools резолвь по role_bindings (.claude/domain-profile.md): роль источника → MCP-сервер сотрудника. Дефолт-маппинг: jira→jira_*, conf→confluence_*, code→repowise(get_answer,get_context,get_risk,get_why,search_codebase), vault→obsidian(search_query,vault_read), web→WebSearch/WebFetch. Кастом-коннектор (развёрнутая форма role_bindings) → его явные tools. Сервер не отвечает → раздел [НЕДОСТУПНО], не выдумывать. ${computeNote}`,
```

- [ ] **Step 5: Pack-агент отмечает недоступные роли + capability-колонки**

Найди pack-агент (`const pack = await agent(` около строки 284). В его промпте, в инструкции про coverage-matrix, добавь строку (после `meta: ...` строки):
```javascript
Coverage-matrix по resources/pack-template.md с колонками required?/available?/used?. Недоступные роли (${'${(plan.unavailableRoles||[]).join(", ") || "нет"}'}) → строки [НЕДОСТУПНО: роль <id>]. policyMissing → флаг в шапке pack.
```
> Примечание: вставляй как обычную строку промпта внутри существующего шаблонного литерала — используй реальную интерполяцию `${(plan.unavailableRoles||[]).join(', ') || 'нет'}` (без внешних кавычек примера выше).

- [ ] **Step 6: Проверить синтаксис JS**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && node --check .claude/workflows/po-context-research.js && echo "OK: workflow синтаксис валиден"
```
Expected: `OK: workflow синтаксис валиден`

- [ ] **Step 7: Проверить наличие правок**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && \
grep -q "availableRoles" .claude/workflows/po-context-research.js && \
grep -q "policyMissing" .claude/workflows/po-context-research.js && \
grep -q "Tools резолвь по role_bindings" .claude/workflows/po-context-research.js && \
echo "OK: workflow capability-resolve добавлен"
```
Expected: `OK: workflow capability-resolve добавлен`

- [ ] **Step 8: Commit**

```bash
git add .claude/workflows/po-context-research.js
git commit -m "feat(workflow): planner resolves role_bindings/policy, researcher uses resolved tools"
```

---

### Task 7: install.sh — подсказка заполнить role_bindings

**Files:**
- Modify: `install.sh` (финальный блок «Дальше:»)

- [ ] **Step 1: Дополнить финальную подсказку**

Найди блок:
```bash
echo "Дальше:"
echo "  1) cp $DEST_ROOT/domain-profile.template.md $DEST_ROOT/domain-profile.md  и заполните под проект"
echo "  2) Reload Window в IDE — команды появятся в чате"
echo "  3) OKR: /okr-context-gen <quarter>   ·   БФТ: /bft-context-gen <epic>"
```
Замени пункт 1 и вставь новый под-пункт про capability:
```bash
echo "Дальше:"
echo "  1) cp $DEST_ROOT/domain-profile.template.md $DEST_ROOT/domain-profile.md  и заполните под проект"
echo "     ↳ секции role_bindings (роль→ваш MCP-сервер) + source_policy — нужны для deep-research"
echo "     ↳ кастом-коннектор: добавьте сервер в .mcp.json и строку в role_bindings"
echo "  2) Reload Window в IDE — команды появятся в чате"
echo "  3) OKR: /okr-context-gen <quarter>   ·   БФТ: /bft-context-gen <epic>"
```

- [ ] **Step 2: Проверить синтаксис bash + наличие правки**

Run:
```bash
cd "$(git rev-parse --show-toplevel)" && bash -n install.sh && \
grep -q "role_bindings (роль→ваш MCP-сервер)" install.sh && \
echo "OK: install.sh подсказка добавлена"
```
Expected: `OK: install.sh подсказка добавлена`

- [ ] **Step 3: Commit**

```bash
git add install.sh
git commit -m "docs(install): nudge to fill role_bindings + source_policy for deep-research"
```

---

## Self-Review

**Spec coverage** (сверка с `2026-06-29-deep-research-source-capability-design.md`):
- `.mcp.json` без изменений → не задача (намеренно). ✅
- `domain-profile` +role_bindings +source_policy → Task 1. ✅
- `source-registry` рефактор → Task 2. ✅
- Преамбула «Resolve capability» в po-research / bft-context-gen-deep / workflow → Tasks 4, 5, 6. ✅
- Coverage-matrix капабилити-колонки → Task 3 (шаблон) + 5/6 (потребители). ✅
- install.sh подсказка → Task 7. ✅
- Цель A (детерминизм): bindings записаны в профиль (Task 1), workflow не пробует случайно (Task 6 — резолв из профиля). ✅
- Цель C (governance): source_policy (Task 1) + policy-гейт (Task 5 block/warn, Task 6 warn-лог) + coverage-колонки (Task 3). ✅
- Цель D (расширяемость): развёрнутая форма role_bindings + install-подсказка (Tasks 1, 2, 7). ✅
- Открытый вопрос спеки «класс топика для policy» → решён: класс задаётся командой (bft-deep=`bft-critical`, po-research deep=`research-deep`, fast=`research-fast`). ✅
- Открытый вопрос «builtin-роли» → решён: `web/compute` available по умолчанию (Task 2 Step 3). ✅

**Placeholder scan:** нет TBD/«add error handling»/«similar to Task N» — каждый шаг содержит точный текст вставки/команду. ✅

**Type/key consistency:** ключи ролей `jira|conf|code|vault|web|vision|compute` едины во всех задачах; поля `availableRoles/unavailableRoles/policyMissing` совпадают между Task 6 Steps 1/3/5; классы `bft-critical|bft-normal|research-deep|research-fast` совпадают между Task 1 и Tasks 4/5. ✅
