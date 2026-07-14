# BFT Pipeline — визуальный референс

Отрисовка текущего пайплайна генерации БФТ (навык `bft-writer`): 10 стадий, у каждой отдельный запуск, своя роль и артефакт, STOP-пауза для PO между ними. Источник процесса — `.claude/skills/bft-writer/SKILL.md`.

## Файлы

| Файл | Что это |
|---|---|
| [`bft-pipeline.html`](./bft-pipeline.html) | Самодостаточная страница: список стадий, петли возврата, диаграмма потока, таблица синхронизации с доской Backlog + диаграмма жизненного цикла контроля. Открывается в браузере, тема-адаптивная. |
| [`bft-pipeline.svg`](./bft-pipeline.svg) | Диаграмма потока пайплайна (10 стадий). |
| [`bft-pipeline.puml`](./bft-pipeline.puml) | PlantUML-исходник диаграммы потока. |
| [`bft-lifecycle.svg`](./bft-lifecycle.svg) | Диаграмма жизненного цикла контроля: `To Do → In Progress → Wait for Review → Accepted → Done` + ветка отказа. |
| [`bft-lifecycle.puml`](./bft-lifecycle.puml) | PlantUML-исходник жизненного цикла. |

## Жизненный цикл контроля (5 статусов задачи Backlog)

`To Do` · `In Progress` · **`Wait for Review`** · `Accepted` · `Done`. Ключевая точка — **Wait for Review**: черновик БФТ у **внешнего PO** (заказчик, который принимает результат работ) на приёмке требований.

- **Одобрено** → `--append-notes` (**обязательно**): кто одобрил, когда, с какими замечаниями. `Accepted` — **только когда все правки внесены и учтены в БФТ** (одобрение с замечаниями само по себе ещё не `Accepted`).
- **Отказано** → `--append-notes` (**обязательно**): кто отказал, какие правки на следующую итерацию → возврат в `In Progress` с `--priority high`.

«Комментарии» в Backlog.md = `--append-notes` (отдельного треда комментариев нет; аудит-лог копится в notes задачи).

## Перерисовать после правок

```bash
plantuml -tsvg -charset UTF-8 docs/bft-pipeline/bft-pipeline.puml
plantuml -tsvg -charset UTF-8 docs/bft-pipeline/bft-lifecycle.puml
```

Диаграмма — «как есть» (текущий процесс). Нижняя таблица в `bft-pipeline.html` — предложение, куда прикрепить отражение статуса на доске Backlog, не меняя сам пайплайн (тред «BFT Backlog control»).

> Синхронизация с онлайн-версией артефакта: https://claude.ai/code/artifact/8b4a6871-f290-4f3a-9dce-67aced2edd64
