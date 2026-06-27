---
name: blueprint-discover
description: "Режим SCRATCH Blueprint-pipeline: собрать Scope Model с нуля через исследование. Делегирует в /context-gen, scouting-агент, problem-analyst, Nexus."
---

# /blueprint-discover — Scope Model с нуля (SCRATCH)

Шаг pipeline после `/blueprint-context` при `mode: scratch` (БФТ нет). Собирает контекст
исследованием, **переиспользуя существующие скиллы** — не дублирует их логику.

> Читай `sa_documentation/blueprint_schema.md` перед записью.

## 1. Делегировать discovery (каждый факт → source)
- `/context-gen` — подготовка контекста кодовой базы/домена.
- scouting-агент (Task tool, subagent_type `scouting`) — актёры, системы, возможности (3 Линзы PAF), source kind: nexus/web.
- problem-analyst (Skill) — структура проблемы и journey.
- `mcp__ruflo__memory_search` / `GROUND/NEXUS/` — контекст продукта (source kind: nexus).
- При внешнем поиске — WebSearch (source kind: web, ref = URL).

## 2. Собрать из результатов Scope Model
- Маппинг: актёры → `actors`; путь → `journey`; затронутые системы/слои → `cells`;
  явные изменения → `scope_of_change` (scope: changed).
- Каждый элемент = с источником (интервью-ответ kind: interview / Nexus-узел / web-URL).

## 3. Пробелы
- Нет источника у факта → НЕ в модель. В `gaps`.

## 4. Записать `scope-model.yaml` и провалидировать
```bash
python3 sa_documentation/validate_scope_model.py GROUND/BLUEPRINT/<task>/scope-model.yaml
```
Ожидается `OK`. Ошибки → исправь.

## 5. Выход
```
Scope Model собрана исследованием: <N> шагов, источники=<типы>, gaps=<K>.
→ /blueprint-model
```

## Guardrails
- Zero-hallucination: факт без источника → gaps, не в модель.
- Не дублируй логику scouting/problem-analyst — вызывай их.
- Верхнеуровнево (детали → /arch-gen, /data-trace).
