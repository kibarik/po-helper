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
Запиши сгенерированный Mermaid в файл и прогони render-check:
```bash
python3 - <<'PY'
import pathlib
from sa_documentation.blueprint_render import render_check, classify_failure, block_message, unavailable_message
code = pathlib.Path("/tmp/blueprint.mmd").read_text(encoding="utf-8")  # сюда записан Mermaid
ok, log = render_check(code)
if ok:
    print("OK")
elif classify_failure(log) == "environment":
    print(unavailable_message(log))   # рендерер/Chrome недоступен — НЕ ошибка диаграммы
else:
    print(block_message(log))         # ошибка синтаксиса Mermaid
PY
```
Ветвление гейта:
- **OK** → переходи к §4.
- **syntax** (ошибка диаграммы) → авто-repair: верни код + лог модели, исправь Mermaid. До **3 попыток**. После 3 неудач → СТОП, НЕ писать blueprint.md, показать `block_message`:
  ```
  ⛔ Не могу продолжить: ошибка рендера Mermaid.
  Для успешного завершения задачи нужно исправить:
  <лог ошибки + проблемная строка>
  Задача НЕ завершена, пока Mermaid не рендерится чисто.
  ```
- **environment** (нет Chrome/рендерера) → СТОП, НЕ писать blueprint.md, показать `unavailable_message` (разовая установка `npx -y puppeteer browsers install chrome-headless-shell`). Это НЕ ошибка диаграммы — не выдавай за неё.
- Задача = done ТОЛЬКО при чистом рендере (OK). Иначе blocked.

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
