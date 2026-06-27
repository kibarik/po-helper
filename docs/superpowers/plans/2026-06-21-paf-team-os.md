# PAF Team OS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Превратить репо AI-KORTEX в дистрибутивный git-template (PAF Team OS): клиент клонирует → `/paf-init` (конфиг + GROUND + дефолтный каталог Нексусов) → (опц. `/paf-nexus-create` кастомные) → `/paf-onboard` (цифровизация контекста, low-CP) → Steps 1–8.

**Architecture:** 3 skill'а (`.claude/skills/`) управляют онбордингом над GROUND Vault; расширяемый Nexus Catalog (master `sa_documentation/nexus_catalog.md` + client `GROUND/NEXUS/_registry.yaml`); 6 Cortex-агентов адаптируются под продукт-namespace; справочник PAF (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES) read-only.

**Tech Stack:** Markdown (vault), YAML frontmatter (Node schema), Claude Code skills + agents, Python (валидатор + индексер), ruflo MCP (опц. RAG).

**Spec:** `docs/superpowers/specs/2026-06-21-paf-team-os-design.md` (v3).

---

## File Structure

**Create:**
- `sa_documentation/nexus_catalog.md` — мастер-каталог PAF Nexus-типов (read-only)
- `sa_documentation/ground_schema.md` — schema `config.yaml` + `_registry.yaml`
- `sa_documentation/validate_ground.py` — валидатор GROUND (testable)
- `sa_documentation/tests/test_validate_ground.py` — тесты валидатора
- `sa_documentation/tests/fixtures/ground_ok/` + `ground_bad/` — фикстуры
- `.claude/skills/paf-init/SKILL.md`
- `.claude/skills/paf-nexus-create/SKILL.md`
- `.claude/skills/paf-onboard/SKILL.md`
- `GROUND/README.md`, `GROUND/_intake/.gitkeep`, `GROUND/NEXUS/_index.md`, `GROUND/NEXUS/_registry.yaml`, `GROUND/NEXUS/{market,customer,product,growth}/.gitkeep`, `GROUND/{PULSE,BUNCH,RESULTS}/.gitkeep`
- `README.md` (rewrite top-level), `INSTALL.md`, `LICENSE`

**Modify:**
- `sa_documentation/nexus_schema.md` — открытое поле `nexus` + кастомные типы + empirical-секция
- `.claude/agents/{nexus-builder,scouting,bunch-former,cp-scorer,wilting-detector}.md` — GROUND-контекст (продукт-namespace + все Нексусы реестра)
- `.gitignore` — добавить `GROUND/_intake/*` (кроме `.gitkeep`) если хотим не коммитить сырые доки клиента (опц. — см. T3)

---

## Task 1: Master Nexus Catalog

**Files:**
- Create: `sa_documentation/nexus_catalog.md`

- [ ] **Step 1: Автор документа**
  Содержание (секции):
  1. Header: «Master Nexus Catalog — кураторский набор PAF Nexus-типов (read-only)».
  2. Принцип: коробка даёт минимально-необходимый набор; клиент расширяет кастомными (`/paf-nexus-create`); поле `nexus` — открытый slug из реестра клиента.
  3. Таблица типов (колонки: slug, name, purpose, owner_role, paf_step_ref, minimal, seed_questions). 4 minimal (`market`,`customer`,`product`,`growth`) + 2 опц. (`ops-model`,`company`).
  4. YAML-определение каждого minimal-типа (пример для `customer`):
     ```yaml
     slug: customer
     name: Нексус потребителя
     purpose: сегменты, JTBD, боли, mNSM-гипотеза
     owner_role: Product Engineer
     paf_step_ref: 2
     minimal: true
     seed_questions:
       - Кто основные сегменты?
       - Какие работы (JTBD) они «нанимают»?
       - Главные боли и их причины?
       - Гипотеза монетизируемой ценности (mNSM)?
     schema_extensions: {}
     ```
  5. Аналогично для `market` (owner: Portfolio Manager, step 3, seed: объём/тренды/конкуренты/Ставки), `product` (owner: Product Engineer, steps 1,4,7, seed: идея/фичи/Vision/гэп), `growth` (owner: Growth Engineer, steps 5,6,8, seed: каналы/модель/AI-COGS), и опц. `ops-model`/`company`.
  6. Связь: `[[nexus_schema]]` (schema), `[[GROUND/NEXUS/_registry]]` (client registry), `/paf-nexus-create`.

- [ ] **Step 2: Verify**
  Run: `python3 -c "import yaml,sys; [yaml.safe_load(b) for b in __import__('re').findall(r'\`\`\`yaml\n(.*?)\`\`\`', open('sa_documentation/nexus_catalog.md').read(), __import__('re').S)]; print('yaml ok')"`
  Expected: `yaml ok` (все YAML-блоки парсятся). Плюс grep: `grep -c 'minimal: true' sa_documentation/nexus_catalog.md` → ≥4.

- [ ] **Step 3: Commit**
  `git add sa_documentation/nexus_catalog.md && git commit -m "feat(box): master Nexus catalog (minimal PAF set + optional)"`

---

## Task 2: nexus_schema.md — open nexus + custom + empirical

**Files:**
- Modify: `sa_documentation/nexus_schema.md`

- [ ] **Step 1: Правки**
  (a) В таблице frontmatter-ключей (§2) строку `nexus` изменить: тип `enum` → **«open slug (любой из `GROUND/NEXUS/_registry.yaml`); дефолтный минимум в [[nexus_catalog]]»**.
  (b) Добавить секцию **«§3.5 Кастомные Nexus-типы»**: клиент определяет свой тип через `/paf-nexus-create` → определение хранится в `GROUND/NEXUS/_registry.yaml` (`source: custom`) + опц. `schema_extensions` (тип-специфичные поля поверх базовой Node schema). Узлы кастомного Нексуса — те же правила (источник/CP/timestamp/wilting).
  (c) Добавить секцию **«§6 Empirical узлы клиента (GROUND Vault)»**: `kind: empirical`, `sources` = `["onboarding:<doc>|onboarding:interview"]`, `confidence` по умолчанию **0.2–0.4** (допущение, не валидировано), `ttl_days` короче (market/customer=90, growth=60); явная пометка в теле `> ⚠️ допущение клиента (онбординг), требует валидации в Steps 1–8`. Сослаться `[[nexus_catalog]]` + `[[ground_schema]]`.
  (d) В §6 (пилот AI-PROCESSES) добавить пометку: «AI-PROCESSES — normative Nexus фреймворка; GROUND Vault клиента — empirical».

- [ ] **Step 2: Verify**
  Run: `grep -E 'open slug|Кастомные Nexus|Empirical узлы клиента' sa_documentation/nexus_schema.md`
  Expected: 3 совпадения. Плюс: `grep -c 'nexus_catalog' sa_documentation/nexus_schema.md` → ≥1.

- [ ] **Step 3: Commit**
  `git add sa_documentation/nexus_schema.md && git commit -m "feat(box): open nexus field + custom types + empirical client nodes"`

---

## Task 3: GROUND/ skeleton

**Files:**
- Create: `GROUND/README.md`, `GROUND/_intake/.gitkeep`, `GROUND/NEXUS/_index.md`, `GROUND/NEXUS/_registry.yaml`, `GROUND/NEXUS/market/.gitkeep`, `GROUND/NEXUS/customer/.gitkeep`, `GROUND/NEXUS/product/.gitkeep`, `GROUND/NEXUS/growth/.gitkeep`, `GROUND/PULSE/.gitkeep`, `GROUND/BUNCH/.gitkeep`, `GROUND/RESULTS/.gitkeep`

- [ ] **Step 1: Автор артефактов**
  - `GROUND/README.md`: «GROUND Vault — ваш персонализированный продуктовый контекст. Поток: `/paf-init` (конфиг) → (опц. `/paf-nexus-create`) → `/paf-onboard` (цифровизация). Структура: `_intake/` (доки), `NEXUS/` (узлы), `PULSE/`,`BUNCH/`,`RESULTS/`. Методология read-only — работайте только здесь.»
  - `GROUND/NEXUS/_index.md`: MOC — «# GROUND Nexus Index» + список Нексусов из `_registry.yaml` (плейсхолдер-ссылки `[[]]`).
  - `GROUND/NEXUS/_registry.yaml`: минимальный дефолт (будет перегенерирован `/paf-init`, но template шлёт пример):
    ```yaml
    nexus_types:
      - {slug: market,   source: default, onboarded: todo}
      - {slug: customer, source: default, onboarded: todo}
      - {slug: product,  source: default, onboarded: todo}
      - {slug: growth,   source: default, onboarded: todo}
    ```
  - Остальные — пустые папки с `.gitkeep`.

- [ ] **Step 2: Verify**
  Run: `find GROUND -type f | sort`
  Expected: 11 файлов (README, _intake/.gitkeep, NEXUS/_index.md, NEXUS/_registry.yaml, 4×NEXUS/<type>/.gitkeep, PULSE/BUNCH/RESULTS/.gitkeep).
  Run: `python3 -c "import yaml; yaml.safe_load(open('GROUND/NEXUS/_registry.yaml'))"` → no error.

- [ ] **Step 3: Commit**
  `git add GROUND && git commit -m "feat(box): GROUND Vault skeleton + default registry"`

---

## Task 4: GROUND schema doc + validator (TDD)

**Files:**
- Create: `sa_documentation/ground_schema.md`, `sa_documentation/validate_ground.py`, `sa_documentation/tests/test_validate_ground.py`, `sa_documentation/tests/fixtures/ground_ok/` (+ config.yaml, NEXUS/_registry.yaml), `sa_documentation/tests/fixtures/ground_bad/`

- [ ] **Step 1: Документ schema** (`ground_schema.md`)
  Таблицы полей `config.yaml` (company, product{name,slug,idea}, team{size,roster{product_engineer(обяз),...}}, cortex{phase_target,ruflo_mcp,obsidian}, onboarding{status,sources_ingested,baseline_cr,onboarded_at}, nexus{catalog,custom_count}, created, paf_step) и `_registry.yaml` (`nexus_types[]`: slug, source[default|custom], name?, owner?, purpose?, onboarded[todo|partial|done]). Валидный пример обоих.

- [ ] **Step 2: Фикстуры**
  - `tests/fixtures/ground_ok/config.yaml` — валидный (company=ACME, product.slug=acme-billing, roster.product_engineer=Jane, cortex.phase_target=2).
  - `tests/fixtures/ground_ok/NEXUS/_registry.yaml` — 4 default, `onboarded: todo`.
  - `tests/fixtures/ground_bad/config.yaml` — НЕвалидный (нет обязательного `product_engineer` в roster; product.slug с пробелом).
  - `tests/fixtures/ground_bad/NEXUS/_registry.yaml` — slug с заглавной буквой (невалидный ascii-slug).

- [ ] **Step 3: Failing test**
  `sa_documentation/tests/test_validate_ground.py`:
  ```python
  import pathlib
  from sa_documentation.validate_ground import validate_ground
  ROOT = pathlib.Path(__file__).parent
  def test_ok():
      errs = validate_ground(ROOT/"fixtures/ground_ok")
      assert errs == [], f"unexpected errors: {errs}"
  def test_bad():
      errs = validate_ground(ROOT/"fixtures/ground_bad")
      assert any("product_engineer" in e or "slug" in e.lower() for e in errs)
  ```
  Run: `cd sa_documentation && python3 -m pytest tests/test_validate_ground.py -v`
  Expected: FAIL (ModuleNotFoundError / ImportError).

- [ ] **Step 4: Implement validator**
  `sa_documentation/validate_ground.py`:
  ```python
  import pathlib, re, yaml
  def validate_ground(ground_dir: pathlib.Path) -> list[str]:
      errs = []
      ground_dir = pathlib.Path(ground_dir)
      cfg_p = ground_dir/"config.yaml"; reg_p = ground_dir/"NEXUS/_registry.yaml"
      if not cfg_p.exists(): return [f"missing {cfg_p}"]
      cfg = yaml.safe_load(cfg_p.read_text())
      prod = cfg.get("product", {})
      slug = prod.get("slug", "")
      if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
          errs.append(f"product.slug invalid ascii-slug: {slug!r}")
      roster = cfg.get("team", {}).get("roster", {})
      if not roster.get("product_engineer"):
          errs.append("team.roster.product_engineer is required")
      if reg_p.exists():
          reg = yaml.safe_load(reg_p.read_text()) or {}
          for t in reg.get("nexus_types", []):
              s = t.get("slug", "")
              if not re.fullmatch(r"[a-z][a-z0-9-]*", s):
                  errs.append(f"nexus slug invalid: {s!r}")
              if t.get("source") not in ("default", "custom"):
                  errs.append(f"nexus {s!r} source must be default|custom")
      return errs
  if __name__ == "__main__":
      import sys; e = validate_ground(sys.argv[1]); print("\n".join(e) or "OK")
  ```
  (note: `pytest` запускается из `sa_documentation/`, поэтому импорт `from sa_documentation.validate_ground import ...` требует `sa_documentation/__init__.py` — создать пустой + `tests/__init__.py`.)

- [ ] **Step 5: Run test → pass**
  Run: `cd sa_documentation && python3 -m pytest tests/test_validate_ground.py -v`
  Expected: 2 passed.

- [ ] **Step 6: Commit**
  `git add sa_documentation/ground_schema.md sa_documentation/validate_ground.py sa_documentation/__init__.py sa_documentation/tests && git commit -m "feat(box): GROUND schema doc + validator (TDD)"`

---

## Task 5: `/paf-init` skill

**Files:**
- Create: `.claude/skills/paf-init/SKILL.md`

- [ ] **Step 1: Автор skill**
  Frontmatter: `name: paf-init`, `description: "Первоначальная настройка GROUND Vault: интервью → config.yaml + дефолтный каталог Нексусов. One-shot. Запусти после git clone."`
  Body (секции):
  1. **Когда запускать**: после clone, один раз.
  2. **Интервью** (спросить по очереди): компания; продукт (имя + ascii-slug + elevator pitch); размер команды; кто Product Engineer (обяз); (опц.) др. роли (или «Cortex»); целевая Cortex-фаза (1/2/3); (опц.) есть ли готовые доки для `GROUND/_intake/`.
  3. **Detect ruflo MCP**: попробовать `mcp__ruflo__memory_stats`; выставить `cortex.ruflo_mcp` true/false.
  4. **Генерация**: `GROUND/config.yaml` (по schema `ground_schema.md`); `GROUND/NEXUS/_registry.yaml` из дефолтного минимума `nexus_catalog.md` (4 типа, `source: default`, `onboarded: todo`); `GROUND/NEXUS/{market,customer,product,growth}/_index.md` (placeholder); (опц.) `GROUND/PULSE/00-init-pulse.md`.
  5. **Гвардраилы**: idempotent — если `GROUND/config.yaml` существует, НЕ затирать без подтверждения. slug валидный (`[a-z0-9-]`). Product Engineer обязателен.
  6. **Финал**: readiness-строка + «→ `/paf-nexus-create` (если нужны кастомные) → `/paf-onboard`».
  7. **Связи**: ссылаться `sa_documentation/nexus_catalog.md`, `ground_schema.md`, `nexus_schema.md`.

- [ ] **Step 2: Verify**
  Run: `head -5 .claude/skills/paf-init/SKILL.md` → frontmatter (name/description). `grep -c 'config.yaml\|_registry.yaml\|nexus_catalog' .claude/skills/paf-init/SKILL.md` → ≥3.

- [ ] **Step 3: Commit**
  `git add .claude/skills/paf-init && git commit -m "feat(box): /paf-init skill (config + default Nexus catalog)"`

---

## Task 6: `/paf-nexus-create` skill

**Files:**
- Create: `.claude/skills/paf-nexus-create/SKILL.md`

- [ ] **Step 1: Автор skill**
  Frontmatter: `name: paf-nexus-create`, `description: "Создать кастомный Нексус под решение клиента (slug/purpose/owner/seed_questions) → NEXUS/<slug>/ + _registry.yaml. Repeatable."`
  Body:
  1. **Когда**: клиенту нужен Нексус сверх дефолтного минимума (напр. sellers/buyers/integrations/compliance/per-product).
  2. **Интервью**: name; slug (ascii, уникальный); purpose; owner (из roster `config.yaml`); seed_questions (3–7 вопросов для онбординга); (опц.) paf_step_ref; (опц.) schema_extensions.
  3. **Генерация**: `GROUND/NEXUS/<slug>/_index.md` + `.gitkeep`; добавить запись в `GROUND/NEXUS/_registry.yaml` (`source: custom`, name/owner/purpose/onboarded: todo); инкремент `config.yaml: nexus.custom_count`.
  4. **Гвардраилы**: slug уникален в реестре; не конфликтует с `minimal: true` из `nexus_catalog.md` (предложить использовать дефолтный); owner ∈ roster; напомнить «дефолтный минимум уже покрывает Steps 1–8» (анти-расползание, spec §14).
  5. **Опц. мини-онбординг**: сразу запустить интервью по seed_questions → первые узлы (low-CP).
  6. **Финал**: «Нексус `<slug>` создан → `/paf-onboard` наполнит его».

- [ ] **Step 2: Verify**
  `grep -c '_registry.yaml\|roster\|nexus_catalog' .claude/skills/paf-nexus-create/SKILL.md` → ≥3.

- [ ] **Step 3: Commit**
  `git add .claude/skills/paf-nexus-create && git commit -m "feat(box): /paf-nexus-create skill (custom Nexus)"`

---

## Task 7: `/paf-onboard` skill

**Files:**
- Create: `.claude/skills/paf-onboard/SKILL.md`

- [ ] **Step 1: Автор skill**
  Frontmatter: `name: paf-onboard`, `description: "Цифровизация контекста клиента в GROUND Vault по всему реестру Нексусов. Гибрид: ингестия доков + интервью → low-CP узлы. Repeatable. Главное событие коробки."`
  Body (4 фазы):
  1. **Phase A — ингестия доков**: клиент кладёт материалы в `GROUND/_intake/`; агент `scouting` + `nexus-builder` парсят → узлы (`kind: empirical`, `sources: ["onboarding:<filename>"]`, nexus по теме); дедуп (`mcp__ruflo__memory_search` или Grep). Цель: извлечь факты/гипотезы, НЕ выдумывать.
  2. **Phase B — интервью**: по каждому Нексусу из `_registry.yaml` (дефолт+кастом) — его `seed_questions` (из `nexus_catalog.md` или определения кастомного); ответы → узлы (`sources: ["onboarding:interview"]`). Только пробелы после Phase A. Модульно (можно паузить по Нексусам).
  3. **Phase C — verify + CP**: агент `cp-scorer` ставит `confidence: 0.2–0.4` всем онбординг-узлам; anti-workslop пометка в теле каждого `> ⚠️ допущение клиента (онбординг), требует валидации в Steps 1–8`; обновить `_registry.yaml: onboarded` (todo→partial→done по Нексусу).
  4. **Phase D — readiness**: агент `wilting-detector`-стиль: Context Ripeness по каждому Нексусу (полнота×свежесть, CP низкий → RIPEness отражает это); карта «что насыщено / где пробелы / top low-CP узлы для приоритетной валидации». Обновить `config.yaml: onboarding.{status:onboarded, baseline_cr, onboarded_at}`.
  5. **Гвардраилы**: idempotent (дедуп+upsert, не затирать валидированные узлы без подтверждения); ноль галлюцинаций (не выдумывать контент — только из доков/интервью); низкий CP обязательно; (если ruflo) индекс в продукт-namespace.
  6. **Финал**: readiness-отчёт + «GROUND насыщен → Steps 1–8 ВАЛИДИРУЮТ и поднимают CP → `AI-PROCESSES/STEP-1-IDEA/overview`».
  7. **Связи**: агенты (`scouting`,`nexus-builder`,`cp-scorer`,`wilting-detector`), `nexus_schema.md` (empirical), `nexus_catalog.md`, `_registry.yaml`.

- [ ] **Step 2: Verify**
  `grep -cE 'Phase A|Phase B|Phase C|Phase D' .claude/skills/paf-onboard/SKILL.md` → ≥4. `grep -c 'low-CP\|0.2' .claude/skills/paf-onboard/SKILL.md` → ≥1.

- [ ] **Step 3: Commit**
  `git add .claude/skills/paf-onboard && git commit -m "feat(box): /paf-onboard skill (context digitalization, 4 phases)"`

---

## Task 8: Cortex agents → GROUND context

**Files:**
- Modify: `.claude/agents/nexus-builder.md`, `scouting.md`, `bunch-former.md`, `cp-scorer.md`, `wilting-detector.md`

- [ ] **Step 1: Правки**
  В каждый из 5 агентов добавить секцию **«## 📂 GROUND-контекст (box-mode)»** перед «## 🔗 Связи»:
  - Корень продукта-Нексуса = `GROUND/NEXUS/` (не `AI-PROCESSES/`).
  - Продукт-namespace (ruflo) = `GROUND/config.yaml: product.slug` (не хардкод `ai-kortex`).
  - Перечень Нексусов = `GROUND/NEXUS/_registry.yaml` (все slug, дефолт+кастом) — работай по всему реестру.
  - Owner/RACI = `GROUND/config.yaml: team.roster`.
  - **Backward-compat**: если `GROUND/config.yaml` нет (framework-mode) — работай по `AI-PROCESSES/` + namespace `ai-kortex` (как сейчас).
  - Прочитать `GROUND/config.yaml` в начале работы (Read).
  Удалить хардкод `ai-kortex`/`AI-PROCESSES` из RAG-секций (заменить на «продукт-namespace из config»).

- [ ] **Step 2: Verify**
  Run: `grep -L 'GROUND/config.yaml' .claude/agents/{nexus-builder,scouting,bunch-former,cp-scorer,wilting-detector}.md`
  Expected: пусто (все 5 содержат ссылку). `grep -c 'ai-kortex' .claude/agents/*.md` → только в backward-compat контексте (или 0).

- [ ] **Step 3: Commit**
  `git add .claude/agents && git commit -m "feat(box): Cortex agents read GROUND config + full Nexus registry"`

---

## Task 9: README.md (top-level)

**Files:**
- Modify: `README.md` (rewrite)

- [ ] **Step 1: Автор**
  Секции: (1) Что такое PAF Team OS (один абзац) + ссылка PAF (productframework.ru/ops/main, Тихомиров, CC BY-SA). (2) Quickstart: `git clone` → открыть в Claude Code → `/paf-init` → (опц. `/paf-nexus-create`) → `/paf-onboard` → `AI-PROCESSES/STEP-1-IDEA/overview`. (3) 3-слойная структура: справочник PAF (read-only) / движок `.claude/` / GROUND Vault (ваш контекст). (4) Prerequisites кратко (→ INSTALL). (5) Лицензия (CC BY-SA методология / MIT код) + credit. (6) Ссылки: INSTALL, AI-PROCESSES/README, sa_documentation/nexus_schema.

- [ ] **Step 2: Verify**
  `grep -c 'paf-init\|paf-onboard\|productframework.ru' README.md` → ≥3. PAF credit присутствует.

- [ ] **Step 3: Commit**
  `git add README.md && git commit -m "docs(box): top-level README + quickstart"`

---

## Task 10: INSTALL.md

**Files:**
- Create: `INSTALL.md`

- [ ] **Step 1: Автор**
  Секции: (1) Prerequisites: **Claude Code** (обяз); **Obsidian** (рекомендован, просмотр vault); **ruflo MCP** (опц., RAG — как включить: одобрить `.mcp.json` при первом открытии, restart; без него fallback Grep). (2) Установка: clone → открыть папку в Claude Code → approve project MCP (ruflo) → `/paf-init`. (3) Онбординг: положить доки в `GROUND/_intake/` → `/paf-onboard`. (4) Troubleshooting: ruflo MCP не появился (`.mcp.json` approval + restart; или путь `/opt/homebrew/bin/ruflo`); кастомный Нексус (`/paf-nexus-create`); «хочу свой редактор вместо Obsidian» (vault=markdown, ок).

- [ ] **Step 2: Verify**
  `grep -c 'Claude Code\|Obsidian\|ruflo\|_intake' INSTALL.md` → ≥4.

- [ ] **Step 3: Commit**
  `git add INSTALL.md && git commit -m "docs(box): INSTALL (prerequisites + onboarding + troubleshooting)"`

---

## Task 11: LICENSE (dual)

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Автор**
  Dual: (a) **MIT** для кода (`.claude/**`, `sa_documentation/*.py`) — полный MIT-текст + copyright «AI-KORTEX contributors». (b) **CC BY-SA 4.0** для методологии (текст `AI-PROCESSES/`, `AI-TRANSFORMATION/`, `TRADITIONAL/`, `sa_documentation/*.md` docs) — attribution «Сергей Тихомиров, productframework.ru» + ссылка + CC BY-SA условия. Раздел «Which license applies» с таблицей папка→лицензия.

- [ ] **Step 2: Verify**
  `grep -c 'MIT\|CC BY-SA' LICENSE` → ≥2. Оба присутствуют.

- [ ] **Step 3: Commit**
  `git add LICENSE && git commit -m "docs(box): dual LICENSE (MIT code + CC BY-SA methodology)"`

---

## Self-Review (vs spec v3)

**Spec coverage:** spec §2 Nexus Catalog → T1+T2+T3+T5+T6 ✓. §3 flow → T5/T6/T7 ✓. §4 paf-init → T5 ✓. §5 paf-onboard → T7 ✓. §6 CP-дисциплина → T2(empirical)+T7(Phase C) ✓. §7 config/registry → T4 ✓. §8 структура → T3+T8 ✓. §9 degradation → T10 ✓. §10 license → T11 ✓. §11 scope 11 пунктов → T1–T11 (1:1) ✓.

**Placeholders:** нет «TBD/TODO»; контент-спеки детальные; код валидатора — полный.

**Type/name consistency:** `_registry.yaml` ↔ `nexus_types[].slug/source/onboarded` едино во T1/T3/T4/T5/T6/T7/T8 ✓. `config.yaml` поля едино ✓. namespace `product.slug` ↔ agents (T8) ✓.

**Gaps:** нет. (Опц. улучшение: `/paf-status` skill — отмечено out-of-scope spec §12.)

---
**Plan complete.** → Execution handoff (см. ниже в чате).
