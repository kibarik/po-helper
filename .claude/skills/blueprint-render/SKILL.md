---
name: blueprint-render
description: "Финал Blueprint-pipeline: из Scope Model рендерит Grid-таблицу + Mermaid в blueprint.md. Блокирующий Mermaid render-гейт (СТОП при ошибке)."
---

# /blueprint-render — финальный BluePrint

Последний шаг pipeline. Из валидной `scope-model.yaml` строит два синхронных артефакта и
пишет `GROUND/BLUEPRINT/<task>/blueprint.md`.

> Читай `references/mermaid-template.md` и `sa_documentation/blueprint_schema.md`.

## 1. Grid-таблица (детерминированный план)
- Строки = `layers`, колонки = `journey`-шаги. Ячейка = `cells[].action` + маркер scope (🔴/🟡/⚪).
- Пустая ячейка → пусто. Элемент из `gaps` → `(?) GAP`.

## 2. Mermaid (по шаблону)
- Сгенерируй `flowchart LR` по `references/mermaid-template.md` (subgraph на слой, узлы=шаги,
  `:::changed|affected|context`, линии visibility/interaction, пунктир между слоями).

## 3. Render-check (ЖЁСТКИЙ ГЕЙТ)
Прогони Mermaid через render-check:
```bash
python3 - <<'PY'
from sa_documentation.blueprint_render import render_check, block_message
code = open("/tmp/blueprint.mmd").read()   # запиши сгенерированный Mermaid сюда
ok, log = render_check(code)
print("OK" if ok else block_message(log))
PY
```
- Ошибка синтаксиса → авто-repair: верни код + лог модели, исправь. До **3 попыток**.
- **После 3 попыток ошибка ИЛИ рендерер недоступен → СТОП.** НЕ писать blueprint.md. Вывести:
  ```
  ⛔ Не могу продолжить: ошибка рендера Mermaid.
  Для успешного завершения задачи нужно исправить:
  <лог ошибки + проблемная строка>
  Задача НЕ завершена, пока Mermaid не рендерится чисто.
  ```
- Задача = done ТОЛЬКО при чистом рендере. Иначе blocked.

## 4. Собрать blueprint.md (только после чистого рендера)
Frontmatter по `blueprint_schema.md` + секции:
- **Mermaid-блок** (отрендеренный).
- **Blueprint Grid** (таблица).
- **Легенда** (из шаблона).
- **Scope-summary** — 1 экран для бизнеса/продакта (из `scope_of_change`).
- **Open questions / GAPs** — из `gaps`.
- **Trace-таблица** — элемент → источник (из `sources`).

## 5. Выход
```
BluePrint готов: GROUND/BLUEPRINT/<task>/blueprint.md (рендер: OK).
Меняемых слоёв=<M>, открытых вопросов=<K>.
```

## Guardrails
- Валидный Mermaid-рендер — обязательное условие завершения (гейт §3).
- Idempotent: существующий blueprint.md не затирать без подтверждения.
- Только трассируемые узлы; пробелы → `(?) GAP`.
- Верхнеуровнево (детали → /arch-gen, /data-trace).
