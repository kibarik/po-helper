---
description: 'Intake стадия 4 — SMART-задача со всем контекстом и критериями приёмки (роль: Task Writer)'
---

## Использование

```
/req-smart <request_id>
```

Вход: `artefacts/gap.md` (+ impact-map, interview). Выход: `smart-task.md` (черновик в корне папки запроса).

## Важно

**Роль: Task Writer.** Превращаешь краткое продуктовое изменение в **SMART-задачу** со всем контекстом и проверяемыми критериями приёмки. Это будущий seed для эпика в `bft-writer`. Высота — результат и приёмка, **не декомпозиция** (без User Stories/БТ/ФТ/API — это bft-writer ниже по потоку).

---

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `domain-profile.md`, `skills/request-intake/resources/smart_rules.md`, `resources/anchor_rules.md`.
2. Прочитай `artefacts/gap.md`, `artefacts/impact-map.md`, `artefacts/interview.md`.
3. Эталон — `skills/request-intake/examples/ideal_smart_task.md`.

### Этап 2: Сборка SMART (по smart_rules.md)
Заполни разделы: Заголовок (глагол+результат) · Контекст · Суть изменения · **Критерии приёмки** (проверяемые, R1) · Ценность/метрика · Границы (входит/НЕ входит) · Контекст домена (R2) · Открытые вопросы · Якоря.
Прогони SMART-чек: S/M/A/R/T — каждая буква закрыта или явная пометка `[УТОЧНИТЬ]`/`[срок: УТОЧНИТЬ]`.

### Этап 3: Сохранение + STOP
- Сохрани **черновик** `<intake_workspace>/<request_id>/smart-task.md` (финализируется на `/req-score`).
```
SMART-задача (черновик): <intake_workspace>/<request_id>/smart-task.md
Заголовок: «<…>». Критерии приёмки: <N>. SMART-чек: S<> M<> A<> R<> T<>.
── СТОП ── PO: проверьте задачу. Дальше — /req-score <request_id> (скоринг + routing-решение).
```

## Запреты
1. НЕ декомпозировать в User Stories/БТ/ФТ/НФТ/API/БД — это bft-writer (altitude).
2. Критерии приёмки обязательны и проверяемы; нет образа приёмки → возврат на `/req-gap` или `[УТОЧНИТЬ]`.
3. Заголовок — про результат, не про предложенное решение.
4. Каждое утверждение ← якорь. Стиль — `skills/bft-writer/resources/writing_style.md`.
