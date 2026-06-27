---
name: blueprint-extract
description: "Режим ENRICH Blueprint-pipeline: вытащить Scope Model из готового БФТ (grounded, trace к разделам). Пробелы → Nexus или gaps."
---

# /blueprint-extract — Scope Model из БФТ (ENRICH)

Шаг pipeline после `/blueprint-context` при `mode: enrich`. Заполняет `scope-model.yaml`
из БФТ. Каждый элемент трассируется к разделу БФТ.

> Читай `sa_documentation/blueprint_schema.md` перед записью.

## 1. Прочитать
- БФТ-файл задачи.
- `GROUND/BLUEPRINT/<task>/scope-model.yaml` (skeleton).
- `sa_documentation/blueprint_schema.md`.

## 2. Извлечь (каждый элемент → source = раздел БФТ)
- `trigger` — точка старта взаимодействия (актёр + событие).
- `end_state` — финальная точка (результат).
- `actors` — участники.
- `journey` — шаги happy-path по порядку.
- `cells` — что происходит на каждом шаге по слоям (см. слои в схеме). `scope`:
  `changed` только если БФТ явно говорит об изменении; иначе `context`/`affected`.
- `scope_of_change` — сводка областей изменения.

## 3. Пробелы
- Нет элемента в БФТ → добери из Nexus (`mcp__ruflo__memory_search`, source kind: nexus).
- Нет и в Nexus → НЕ выдумывай. Запиши в `gaps: {about, note}`.

## 4. Записать `scope-model.yaml` и провалидировать
```bash
python3 sa_documentation/validate_scope_model.py GROUND/BLUEPRINT/<task>/scope-model.yaml
```
Ожидается `OK`. Ошибки → исправь, перезапусти.

## 5. Выход
```
Scope Model собрана из БФТ: <N> шагов, <M> ячеек, gaps=<K>.
→ /blueprint-model
```

## Guardrails
- Zero-hallucination: узел без source недопустим — только в gaps.
- `scope: changed` только при явном указании в БФТ.
- Не углубляйся в реализацию — верхнеуровнево (детали → /arch-gen, /data-trace).
