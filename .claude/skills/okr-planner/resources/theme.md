# theme — дизайн-система рендера (`engine/theme.py`)

Единый визуальный контракт для всех рендереров движка. **HTML и PPTX рендерят одну и ту же раскладку `Element`; тема — единственный источник визуальных значений.** `render_html.py` и `render_pptx.py` — две реализации одного каталога архетипов (`engine/archetypes.py`) поверх одного `Theme`: разница между HTML- и PPTX-выводом — только в технике отрисовки (CSS-grid/flex vs autoshapes), не в цветах/шрифтах/геометрии.

`Theme` строится `engine.theme.load_theme(present: dict | None)`. **Пустой/отсутствующий `present:` профиль → эталонные дефолты MTS** (значения ниже), без единого недостающего поля.

---

## 1. Поля `Theme` и дефолты

| Поле | Дефолт (hex/значение) | Что красит |
|------|------------------------|-----------|
| `accent` | `#E4002B` | акцент/kicker/бренд-цвет |
| `heading` | `#1C2333` | заголовки (navy) |
| `body` | `#434C60` | основной текст |
| `muted` | `#8B94A6` | второстепенный/подписи |
| `card_bg` | `#F5F7FB` | фон карточек |
| `dark_bg` | `#141A2E` | фон тёмных слайдов (`title`) |
| `subtitle_on_dark` | `#AEB6CE` | подзаголовок на тёмном фоне (`title`) |
| `positive` | `#2F7D54` | позитивный акцент («СТАНЕТ», «ДАЛЬШЕ») |
| `info` | `#2E4B7A` | нейтрально-информационный акцент («К АВГУСТУ») |
| `direction_palette` | `["#E4002B", "#2E4B7A", "#0F7A8C", "#2F7D54"]` | цвета направлений по кругу |
| `role_color_map` | см. §2 | цвет чипа по роли |
| `heading_font` | `Cambria` | шрифт заголовков |
| `body_font` | `Calibri` | шрифт текста |
| `slide_w_in` | `13.333` | ширина слайда, дюймы (16:9) |
| `slide_h_in` | `7.5` | высота слайда, дюймы (16:9) |

## 2. `role_color_map` — дефолт

| Роль | Цвет |
|------|------|
| `BA` | `#B37D0C` |
| `SA` | `#B37D0C` |
| `ADR` | `#B37D0C` |
| `BE` | `#2E4B7A` |
| `FE` | `#2E4B7A` |
| `QA` | `#7E56A6` |
| `RELEASE` | `#2F8557` |
| `DBA` | `#0F7A8C` |

Метод `theme.role_color(role)` апперкейсит и стрипит роль, ищет в `role_color_map`; не найдено → фолбэк на `theme.body` (`#434C60`).

## 3. Методы

- `role_color(role: str) -> str` — цвет чипа/роли, фолбэк `body`.
- `direction_color(index: int) -> str` — `direction_palette[index % len(direction_palette)]`; используется, когда `Direction.color` в deck-spec не задан.

---

## 4. Профиль `present:` — ключи и переопределение

`load_theme(present)` читает только эти ключи (`_KEYS` в `theme.py`) и переносит их 1:1 в поля `Theme` — **если ключ задан и не пуст**, иначе остаётся дефолт:

| Ключ `present:` | Поле `Theme` |
|------------------|--------------|
| `accent_color` | `accent` |
| `heading_color` | `heading` |
| `body_color` | `body` |
| `muted_color` | `muted` |
| `card_bg` | `card_bg` |
| `dark_bg` | `dark_bg` |
| `subtitle_on_dark` | `subtitle_on_dark` |
| `positive_color` | `positive` |
| `info_color` | `info` |
| `direction_palette` | `direction_palette` |
| `heading_font` | `heading_font` |
| `body_font` | `body_font` |

`role_color_map` из профиля обрабатывается отдельно: не заменяет дефолт целиком, а **мёрджится** поверх него (`dict(_DEFAULT_ROLES)`, обновлённый ключами профиля, приведёнными к верхнему регистру). Значит частичный override (например, только `SA`) не теряет цвета остальных ролей.

`slide_w_in` / `slide_h_in` в `_KEYS` не входят — геометрия слайда (16:9, 13.333×7.5") **не переопределяется** через профиль.

Пример override в `domain-profile`:

```yaml
present:
  accent_color:      "#E4002B"
  heading_color:      "#1C2333"
  direction_palette:  ["#E4002B", "#2E4B7A", "#0F7A8C", "#2F7D54"]
  role_color_map:     {SA: "#B37D0C", ADR: "#B37D0C", BA: "#B37D0C",
                        BE: "#2E4B7A", FE: "#2E4B7A", QA: "#7E56A6",
                        RELEASE: "#2F8557", DBA: "#0F7A8C"}
```

Пустое поле → дефолт эталона (+ `[УТОЧНИТЬ]`, если PO ожидал override). Профиль не отменяет требование источника на факт (см. `deck_spec_schema.md`, §8).

---

## 5. Геометрия слайда

- Формат — 16:9, `13.333 × 7.5` дюйма (стандарт PowerPoint widescreen).
- Все координаты элементов (`Element.fx/fy/fw/fh` в `engine/layout.py`) — **доли** от ширины/высоты слайда (`0..1`), не абсолютные единицы: рендерер сам умножает на `slide_w_in`/`slide_h_in` (PPTX) или на `%`/`vw`/`vh` (HTML). Это и обеспечивает паритет раскладки между бэкендами.
- `radius` в `Element` — тоже доля (`0..1` от `min(fw, fh)`), не пиксели/points.

## 6. Шрифты

- **Заголовки:** `Cambria` (`theme.heading_font`).
- **Текст:** `Calibri` (`theme.body_font`).
- Оба переопределяемы через `present.heading_font` / `present.body_font`.
