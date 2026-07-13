> **Адаптер `mts-link` для po-helper Pulse-pipeline.** Референс source-адаптера для `/chat-sync`.
> Пишет чат-дампы в `GROUND/_intake/chats/` строго по контракту
> `.claude/skills/chat-sync/resources/chat_dump_contract.md` (frontmatter `type: chat-dump` + тело).
> **Opt-in:** `install.sh` его не ставит. Setup: `npm install` (тянет Playwright chromium),
> затем `npm run login` (корпоративный SSO — только PO). Секреты (`.env`, `auth.json`) — вне git.

---

# mts-link-chat-sync

Выгружает сообщения из выбранных чатов МТС Линк (`my.mts-link.ru/chats/`) за период в
обычные markdown-файлы — чтобы дальше их анализировал LLM (Claude Code, ChatGPT, что угодно)
под конкретную цель каждого чата.

Идея: у тебя десятки рабочих чатов, читать всё вручную дорого. Ты один раз выбираешь, за
какими чатами следишь, и на каждый пишешь **зачем** и **что вытаскивать**. Дальше одной
командой выкачиваешь свежак и скармливаешь LLM.

> **Строго read-only.** Инструмент только читает: логинится под твоей сессией и запрашивает
> историю. Он НИКОГДА не отправляет сообщения и не помечает прочитанным — твои счётчики
> непрочитанного не сбиваются. Ничего личного в код не зашито: все пути и сессия — в твоём
> локальном `.env` (в git не попадает).

## Как это работает

У МТС Линк нет публичного API. Чат работает по JSON-RPC поверх WebSocket
(`wss://prod-ws-chat.mts-link.ru`). Доступ — гибридный:
1. Playwright один раз открывает `/chats/` под сохранённой SSO-сессией и снимает из
   хендшейка WS-токен, URL сокета и `organizationId` (`harvest.mjs`).
2. Node открывает свой WebSocket с этим токеном и напрямую вызывает RPC (`wsClient.mjs`).

## Требования

- Node.js **≥ 21** (нужен встроенный `process.loadEnvFile` и глобальный `WebSocket`).
- Доступ к МТС Линк через корпоративный SSO (обычный рабочий аккаунт).

## Установка

```bash
npm install                 # ставит playwright + yaml и скачивает Chromium
```

## Настройка (по желанию)

Все настройки опциональны — по умолчанию всё кладётся в `./chats-out/`. Чтобы поменять пути:

```bash
cp .env.example .env        # затем отредактируй .env под себя
```
Переменные — в `.env.example` (куда выгружать, где хранить сессию и т.д.). `.env` в `.gitignore`.

## Использование

### 1. Разовый вход (и потом при протухании сессии)
```bash
npm run login               # откроется браузер → залогинься через SSO → нажми Enter
```
Сессия сохранится в `~/.mts-link-chat-sync/auth.json` (или куда указал в `.env`).

### 2. Настроить, за какими чатами следить
```bash
node chats.mjs --list-chats                  # весь список, нумерованный с 0
node chats.mjs --list-chats --search продукт # фильтр по названию (удобно на сотнях чатов)
node chats.mjs --watch 0,3,7                  # chat-id + name выбранных
node chats.mjs --add --chat-id "<id>" --name "<имя>" \
     --purpose "<зачем слежу>" --extract "<что вытаскивать>"
node chats.mjs --list-watched                 # показать реестр
node chats.mjs --unwatch "<chat-id>"          # убрать чат
```
Реестр — обычный YAML (`<OUTPUT_DIR>/watched-chats.yaml`), можно править и руками.

### 3. Выгрузить сообщения за окно
```bash
node chats.mjs --pull                         # последние 14 дней
node chats.mjs --pull --days 7
node chats.mjs --pull --from 2026-06-01 --to 2026-06-30
node chats.mjs --pull --dry --days 7          # показать, что выгрузилось бы
```

## Формат выходного файла

`<OUTPUT_DIR>/YYYY-MM-DD..YYYY-MM-DD <название чата>.md`:

```yaml
---
type: mts-chat
chat-id: "…"
window: 2026-07-01..2026-07-09
purpose: "…"      # из реестра — направляет анализ LLM
extract: "…"
msg-count: 214
source: MTS Link
---
```
Далее реплики `Автор HH:MM: текст`, сгруппированные заголовками `## YYYY-MM-DD`.

## Файлы

`config.mjs` (настройки из env/.env) · `login.mjs` (вход) · `harvest.mjs` (снять WS-токен) ·
`wsClient.mjs` (WS-клиент) · `registry.mjs` (реестр) · `chats.mjs` (CLI).

## Если что-то сломалось

- **Редирект на логин / нет токена / `Session expired`** → сессия протухла: `npm run login`.
- **`WS token rejected` / `WS auth timeout`** → протух токен или сменился протокол; перезапусти команду.
- **Сменилась версия чат-фронта** (`v=…` в URL сокета) → протокол мог измениться; снять свежий трафик и сверить методы.
- **`RPC timeout: <метод>`** → метод/параметры изменились на стороне МТС Линк.

## Приватность

`.env`, `auth.json`, `chats-out/` — в `.gitignore`. Перед тем как делиться папкой,
убедись, что не приложил `.env`, файл сессии и выгрузки: это твои личные данные.
