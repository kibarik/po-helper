# Pack Template — context-pack.md

> Шаблон артефакта po-research. Расширение pack из `bft-context-gen` (+2 блока: Contradictions, Evidence Quality). Заполнять только из источников; нет источника → `[УТОЧНИТЬ]`. Store: `{research_workspace}/context-pack.md`.

```markdown
# Context Pack: <topic>

> meta: domain=<…> | режим=<Fast|Deep> | budget-tier=<High|Med|Low> | seed=<PO ✅ (Phase 0) | — (автономно)> | дата=<ГГГГ-ММ-ДД> | статус источников=<VPN ✅/⚠️>

## CORTEX (фон) — по релевантности
<подключить ссылкой + короткие выдержки, НЕ копировать целиком>
- C1 Архитектура: …            ({cortex.architecture})
- C3 Регуляторика: …          ({cortex.regulatory})
- C2+ BR-*: …                 ({cortex.business_rules})
- C5 ADR/PO-решения: …        ({cortex.decisions})

## NEXUS (живые факты) — per source, с якорями
### N1 JIRA        [PROJ-101] conf:High  fact…  (freshness: …)
### N2 Confluence  [pageId=…]  conf:Med   fact…
### N3 Код (repowise)  blast-radius: …  [symbol_id]  conf:High
### N4 web (Deep)  [url]  conf:Med  fact…
<каждый finding: fact + anchor + confidence + freshness>

## ⚠️ Contradictions  (если есть)
- <аспект>: JIRA говорит «X» [anchor] vs Confluence «Y» [anchor]
  → ⚠️ CONTRADICTION → [УТОЧНИТЬ у <владельца>]
  (обе версии в pack, если обе confidence ≥Medium; иначе High + Low как [УТОЧНИТЬ])

## Coverage Matrix
> Разделы = оси домена (см. resources/domains.md). Пример для epic:
| Раздел pack | Питающий | Статус |
|---|---|---|
| Границы | C1+N2 | ✅ |
| Образ результата (БТ) | N2+N3 | ⚠️partial |
| Зависимости | C1+N6 | [УТОЧНИТЬ] |
| … | … | … |

coverage% = sections_with_source / total_sections = <X>/<Y> = <Z>%
Порог домена: <75/80/95>%. Зависимости — hard-gate.

## Evidence Quality
- High (verified, ≥2 источника): <n>
- Medium: <n>
- Low: <n>
- Refuted / killed скептиком (Deep): <n>

## Требует уточнения
- [УТОЧНИТЬ у PO/архитектора/…]: <что> — <как проверить> — <кто ответит>
- …
```

## Правила заполнения

1. **CORTEX** — фон, по ссылке + выдержка, не копировать целиком.
2. **NEXUS** — каждый факт с якорем + confidence + freshness. Нет якоря → в `[УТОЧНИТЬ]`.
3. **Contradictions** — не прятать; обе стороны, если обе ≥Med (open Q #5, дефолт v0.2).
4. **Coverage** — оси = разделы домена, не фикс БФТ.
5. **Evidence Quality** — в Fast блок «Refuted» пуст (скептика нет); в Deep — заполняется.
6. **Статус источников** — честно про VPN/недоступность.
