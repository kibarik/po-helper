# Integrations — внешние интерфейсы к экосистеме po-helper

Опциональный слой. Здесь живут модули, которые дают **второй способ**
взаимодействия с экосистемой po-helper — не через набор скиллов Claude Code
(`/bft-writer`, `/okr-planner`, `/request-intake`, …), а через внешние каналы.

> **Важно:** ничто в этом каталоге не является зависимостью ядра po-helper.
> Модули подключены как git-субмодули и по умолчанию **не выкачиваются**.
> Клонирование `po-helper` без `--recurse-submodules`, работа скиллов,
> `install.sh`, хуки и Vault (`GROUND/`) — всё функционирует без единого файла
> отсюда. Отсутствие модуля ничего не ломает; его наличие — дополняет.

---

## github-issue-agents

- **Субмодуль:** `integrations/github-issue-agents` → [`kibarik/GitHub-issue-agents`](https://github.com/kibarik/GitHub-issue-agents)
- **Что это:** self-hosted сервис (docker-compose + Temporal), который слушает
  вебхуки GitHub и проводит Issue через полный жизненный цикл как один
  долгоживущий workflow (предфильтры → intake gate → классификация → дубликаты →
  приоритизация → research/bug-пайплайны).

### Зачем это po-helper

Обычно PO управляет экосистемой из Claude Code — вызывая скиллы вручную. Этот
модуль добавляет **интерфейс через GitHub Issues**: PO (или любой участник)
открывает Issue или ставит лейбл, а сервис сам запускает нужные пайплайны
экосистемы (`po-helper` → Repowise → Blueprint → `deb8flow` → `SA-helper`).

**Условная цель:** взаимодействовать с пространством через Issue-запросы в гите,
а не только через набор скиллов в Claude Code. Issue становится точкой входа в
те же самые пайплайны, что и слэш-команды.

```
Два интерфейса к одним пайплайнам экосистемы:

  [Claude Code skills]  ──┐
                          ├──►  po-helper / SA-helper / deb8flow  ──►  артефакты
  [GitHub Issues]  ───────┘        (BFT / Blueprint / техспека)
   (github-issue-agents)
```

### Как подключить (когда понадобится)

Субмодуль опционален — инициализируй его только если разворачиваешь сервис:

```bash
# выкачать содержимое субмодуля
git submodule update --init integrations/github-issue-agents

# дальше — по инструкции самого модуля
cd integrations/github-issue-agents
cat README.md   # регистрация GitHub App, .env, docker-compose up
```

Чтобы клонировать po-helper сразу с модулем:

```bash
git clone --recurse-submodules https://github.com/kibarik/po-helper.git
```

### Статус

MVP + спроектированные системные требования на ближайшую доработку
(реализация тяжёлых стадий + доставка скиллов в воркер) —
см. `integrations/github-issue-agents/sa_documentation/FNR/FNR_1/`.

### Обновление ссылки на модуль

Субмодуль запиннен на конкретный commit. Обновить до свежего `main`:

```bash
git submodule update --remote integrations/github-issue-agents
git add integrations/github-issue-agents && git commit -m "chore: bump github-issue-agents submodule"
```
