# Node schema — указатель, не дубликат

Источник истины по схеме узла — **`sa_documentation/nexus_schema.md`**:
- §2 — поля frontmatter и колонка «Обязательный» (полный список ключей и
  признак обязательности — в `sa_documentation/nexus_schema.md`).
- §3 — валидные значения `node_type` (полный список по нексусам).
- §4 — вычисление `ripeness`/wilting из `updated` + `ttl_days`.

Этот файл **не переопределяет и не дублирует** схему — стадии `/cindex-*`
читают `nexus_schema.md` как канон. Ниже — только специфика узлов,
создаваемых Confluence-индексатором поверх базовой схемы.

## Специфика Confluence-узлов

Узлы, оцифрованные из Confluence, — `kind: empirical` (контекст продукта, не
методология, `nexus_schema.md` §2.2). Фиксированные значения для этого
источника:

| Поле | Значение | Почему |
|---|---|---|
| `kind` | `empirical` | контекст клиента, не PAF-методология |
| `confidence` | `0.3` | допущение онбординга (Confluence не валидируется индексатором); см. `confidence_rules.md` |
| `sources` | `["confluence:<url>"]` | ссылка на исходную страницу; узел без `sources` = workslop (§2 нексус-схемы) |
| `tags` | включает `confluence-indexed` | маркер происхождения узла для фильтрации/аудита |

`nexus` и `node_type` для конкретного узла — по `routing_table.md`, не
фиксированы здесь. `ttl_days` — по `confidence_rules.md` (market/customer=90,
growth=60, прочие=180). `node_id` — детерминированный из `source_page` +
слаг заголовка (обеспечивает идемпотентность ре-индекса, спека §8).

## Ссылки

- `sa_documentation/nexus_schema.md` — канон схемы узла.
- `routing_table.md` — какой `nexus`/`node_type` для какого сигнала.
- `confidence_rules.md` — `confidence`, `route_confidence`, `ttl_days`.
- `linking_rules.md` — как узлы связываются друг с другом.
