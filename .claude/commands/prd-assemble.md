---
description: 'PRD-витрина — пересобираемый PRD поверх наполненных Нексусов, с честной разметкой confidence/открытых вопросов (роль: Assembler)'
---

## Использование

```
/prd-assemble
```

Вход: узлы Нексусов market/customer/product/growth. Выход: `{prd_output_doc}`.

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `skills/prd-research/SKILL.md` + `resources/pipeline.md`.
2. Резолвни `{prd_output_doc}` и `{product}` из `.claude/domain-profile.md` / `GROUND/config.yaml`.

### Этап 2: Сбор узлов
3. Прочитай `GROUND/NEXUS/_registry.yaml`. По Нексусам market/customer/product/growth (и system-landscape) собери узлы: frontmatter (`hyp_status`, `confidence`, `sources`, `depends_on`) + суть из тела.

### Этап 3: Разметка confidence раздела
4. Для каждого раздела PRD (по шагам pipeline.md) определи метку:
   - `✅ validated` — раздел имеет хотя бы один узел с `hyp_status: validated` и CP ≥ 0.6.
   - `🟡 assumed` — есть узлы, но ни один не `validated`: любой из `draft`/`hypothesis`/`scoring`/`validating` (независимо от CP).
   - `🔴 open` — узлов нет, либо все узла `parked`/`refuted`.

### Этап 4: Рендер `{prd_output_doc}`

```markdown
# PRD — {product}   ·   пересобрано {today}

> Витрина текущего состояния discovery. Метки: ✅ validated / 🟡 assumed / 🔴 open.

## 1. Идея и контекст   <метка>
## 2. Потребитель        <метка>
## 3. Рынок              <метка>
## 4. Ценность           <метка>
## 5. Бизнес-модель       <метка>
## 6. Go-To-Market        <метка>
## 7. Решение и требования <метка>
## 8. Привлечение (PCF)   <метка>

## Открытые вопросы
[агрегат open_questions всех шагов]

## Рассогласования
[узлы wilting с depends_on]

## Доказательная база
[таблица: узел | hyp_status | CP | источники]
```

### Этап 5: СТОП
```
PRD-витрина пересобрана: {prd_output_doc}
Разделы: ✅ N / 🟡 M / 🔴 K. Открытых вопросов: Q. Рассинхронов: R.
── СТОП ── Это срез текущего состояния; наполняй шагами /prd-*.
```

## Запреты
1. НЕ выдавай `🟡 assumed` за `✅ validated`. Метка ← фактический `hyp_status`/CP узлов.
2. Раздел без узлов → `🔴 open`, не выдумывай содержание.
3. Каждый факт в PRD ← узел с `sources`; иначе не включать.
