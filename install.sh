#!/usr/bin/env bash
# po-helper installer — разворачивает ВСЮ экосистему po-helper в проект (Claude Code).
#
# Детерминированный движок (умные/рассуждающие шаги — за скиллом /paf-install):
#   Phase 0  выбор источника (клон или git clone --depth 1 во временную папку)
#   Phase 1  выбор target-проекта
#   Phase 2  копия всего репозитория (кроме VCS-внутренностей и runtime-мусора)
#   Phase 3  bootstrap внешних CLI: ruflo · entire · backlog · serena (best-effort + fallback)
#   Phase 4  адаптация конфигов: .mcp.json путь · .serena project_name · domain-profile · backlog init
#   Phase 5  self-check + машиночитаемый отчёт (=== PAF-INSTALL-REPORT ===)
#
# Режимы:
#   bash install.sh [target]            — install: недостающее добавляется, существующее НЕ трогается
#   bash install.sh --update [target]   — update:  framework-слой обновляется, domain/project-слой защищён
#   bash install.sh --ref <branch> …    — какую ветку клонировать при curl|bash (default: main)
#
# domain/project-слой (domain-profile.md, GROUND-данные, backlog/, examples проекта,
# .serena project_name, .mcp.json, settings.local.json) НЕ перезаписывается никогда.
set -euo pipefail

REPO_URL="https://github.com/kibarik/po-helper.git"
RUFLO_MIN="3.14.4"

# --- разбор аргументов ---
MODE="install"
TARGET=""
REF="main"
while [ $# -gt 0 ]; do
  case "$1" in
    --update)  MODE="update" ;;
    --install) MODE="install" ;;
    --ref)     if [ $# -ge 2 ]; then REF="$2"; shift; else REF="main"; fi ;;
    --ref=*)   REF="${1#--ref=}" ;;
    *)         TARGET="$1" ;;
  esac
  shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- отчёт: накапливаем строки key:value, печатаем блоком в Phase 5 ---
REPORT=()
rep() { REPORT+=("$1"); }

# ============================================================================
# Phase 0 — выбор источника (approach B)
# ============================================================================
CLONED_TMP=""
cleanup() { [ -n "$CLONED_TMP" ] && rm -rf "$CLONED_TMP" 2>/dev/null || true; }
trap cleanup EXIT

is_repo_root() { [ -d "$1/.claude/skills" ] && [ -d "$1/GROUND" ] && [ -f "$1/install.sh" ]; }

echo "→ Phase 0: источник"
if is_repo_root "$SCRIPT_DIR"; then
  SRC="$SCRIPT_DIR"
  echo "  ✓ запущен из клона po-helper — копирую из $SRC"
else
  echo "  · не в клоне (curl|bash) — клонирую $REPO_URL@$REF…"
  if ! command -v git >/dev/null 2>&1; then
    echo "❌ Phase 0: нет git и нет локального клона. Установите git или запускайте из клона po-helper." >&2
    exit 1
  fi
  CLONED_TMP="$(mktemp -d 2>/dev/null || mktemp -d -t po-helper)"
  if ! git clone --depth 1 --branch "$REF" "$REPO_URL" "$CLONED_TMP" >/dev/null 2>&1; then
    echo "❌ Phase 0: git clone не удался (ветка $REF, сеть?). Проверьте доступ к $REPO_URL." >&2
    exit 1
  fi
  if ! is_repo_root "$CLONED_TMP"; then
    echo "❌ Phase 0: клон не похож на репозиторий po-helper (нет .claude/skills или GROUND)." >&2
    exit 1
  fi
  SRC="$CLONED_TMP"
  echo "  ✓ клонировано во временную папку"
fi

# ============================================================================
# Phase 1 — выбор target-проекта
# ============================================================================
echo "→ Phase 1: target"
TARGET="${TARGET:-$PWD}"
TARGET="$(cd "$TARGET" 2>/dev/null && pwd || echo "$TARGET")"
if [ ! -d "$TARGET" ]; then
  echo "❌ Phase 1: целевая папка $TARGET не существует." >&2
  exit 1
fi
if [ "$SRC" = "$TARGET" ]; then
  echo "❌ Phase 1: источник и target совпадают ($TARGET). Запускайте установку в отдельном проекте." >&2
  exit 1
fi
TARGET_NAME="$(basename "$TARGET")"
echo "  → Режим: $MODE   ·   Проект: $TARGET_NAME ($TARGET)"
if git -C "$TARGET" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "  ✓ target — git-репозиторий"
else
  echo "  ⚠ target не git-репозиторий — часть шагов (entire/backlog init) будет пропущена. Совет: git init"
fi

# ============================================================================
# Phase 2 — копия всего репозитория
# ============================================================================
echo "→ Phase 2: копия репозитория"
if ! command -v rsync >/dev/null 2>&1; then
  echo "❌ Phase 2: нужен rsync. Установите: brew install rsync  (или: apt-get install rsync)." >&2
  rep "repo_copied:      FAILED (нет rsync)"
  exit 1
fi

# Единственный список исключений: VCS-внутренности + машинно-локальный runtime.
# Всё «выключенное» переинициализируется в Phase 3–4.
EXCLUDES=(
  ".git" ".git/**"
  ".claude/worktrees" ".claude/worktrees/**"
  ".serena/cache" ".serena/cache/**" ".serena/project.local.yml"
  ".entire/logs" ".entire/logs/**" ".entire/metadata" ".entire/metadata/**"
  ".entire/tmp" ".entire/tmp/**" ".entire/settings.local.json"
  ".entire/redactors/local" ".entire/redactors/local/**"
  ".claude/*.db" ".swarm" ".swarm/**"
  "repomix-output.xml" "**/repomix-*.xml"
  ".DS_Store" "**/.DS_Store" "__pycache__" "**/__pycache__/**" "*.pyc"
)
# domain/project-слой: в --update НЕ перезаписываем (защищённые пути).
PROTECT=(
  ".claude/domain-profile.md"
  ".claude/settings.local.json"
  ".mcp.json"
  ".serena/project.yml"
  "GROUND/**"
  "backlog" "backlog/**"
  ".claude/skills/*/examples" ".claude/skills/*/examples/**"
)

rsync_args=(-a)
for e in "${EXCLUDES[@]}"; do rsync_args+=(--exclude "$e"); done

# Pass 1 (оба режима): аддитивно — создаём недостающее, существующее НЕ трогаем.
rsync "${rsync_args[@]}" --ignore-existing "$SRC/" "$TARGET/"
echo "  ✓ аддитивная синхронизация (недостающее добавлено, существующее сохранено)"

# Pass 2 (только update): обновляем framework-слой, защищая domain/project-слой.
if [ "$MODE" = "update" ]; then
  update_args=(-a)
  for e in "${EXCLUDES[@]}"; do update_args+=(--exclude "$e"); done
  for p in "${PROTECT[@]}"; do update_args+=(--exclude "$p"); done
  rsync "${update_args[@]}" "$SRC/" "$TARGET/"
  echo "  ✓ framework-слой обновлён (domain/project-слой защищён)"
fi

# санитарная проверка: .git источника не утёк в target как файл/папка сорса
if [ -e "$TARGET/.git" ] && [ ! -d "$TARGET/.git" ] && ! git -C "$TARGET" rev-parse >/dev/null 2>&1; then
  echo "  ⚠ в target появился подозрительный .git — проверьте вручную"
fi
rep "repo_copied:      OK"
rep "excluded_clean:   OK (.git источника не скопирован)"

# ============================================================================
# Phase 3 — bootstrap внешних CLI (best-effort + fallback)
# ============================================================================
echo "→ Phase 3: внешний тулзен"

# ruflo (MCP-сервер из .mcp.json) — раньше Phase 4, чтобы адаптировать реальный путь.
RUFLO_PATH=""
bootstrap_ruflo() {
  if ! command -v ruflo >/dev/null 2>&1; then
    if command -v npm >/dev/null 2>&1 && npm i -g ruflo@latest >/dev/null 2>&1; then :; fi
  fi
  if ! command -v ruflo >/dev/null 2>&1; then
    echo "  ⚠ ruflo не поставлен (нужен npm/сеть). Вручную: npm i -g ruflo@latest (>= $RUFLO_MIN)"
    rep "ruflo:            MISSING (npm i -g ruflo@latest)"
    return
  fi
  RUFLO_PATH="$(command -v ruflo)"
  local cur
  cur="$(ruflo --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
  if [ -n "$cur" ] && [ "$(printf '%s\n%s\n' "$RUFLO_MIN" "$cur" | sort -V | head -1)" != "$RUFLO_MIN" ]; then
    echo "  ⚠ ruflo $cur устарел (нужна >= $RUFLO_MIN). Обновите: npm i -g ruflo@latest"
    rep "ruflo:            DEGRADED ($cur < $RUFLO_MIN)"
  else
    echo "  ✓ ruflo ${cur:-найден}"
    rep "ruflo:            OK ${cur:-?}"
  fi
}
bootstrap_ruflo

# entire (session-tracking) — curl-инсталл в $HOME/.local/bin, без sudo.
bootstrap_entire() {
  if ! command -v entire >/dev/null 2>&1; then
    curl -fsSL https://entire.io/install.sh 2>/dev/null | bash >/dev/null 2>&1 || true
    [ -x "$HOME/.local/bin/entire" ] && export PATH="$HOME/.local/bin:$PATH"
  fi
  if ! command -v entire >/dev/null 2>&1; then
    echo "  ⚠ entire не поставлен. Вручную: curl -fsSL https://entire.io/install.sh | bash"
    rep "entire:           DEGRADED (curl -fsSL https://entire.io/install.sh | bash)"
    return
  fi
  local cur; cur="$(entire version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
  echo "  ✓ entire ${cur:-найден}"
  rep "entire:           OK ${cur:-?}"
  # enable — только в git-репо target
  if git -C "$TARGET" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if ( cd "$TARGET" && entire status 2>/dev/null | grep -qi 'enabled' ); then
      echo "    · entire уже включён в проекте"
    elif ( cd "$TARGET" && entire enable --agent claude-code --telemetry=false >/dev/null 2>&1 ); then
      echo "    ✓ entire включён (session-tracking активен)"
    else
      echo "    ⚠ entire enable не удался. Вручную: (cd $TARGET && entire enable --agent claude-code)"
    fi
  fi
}
bootstrap_entire

# backlog.md (операционный штаб) — bun/npm глобально.
bootstrap_backlog() {
  if ! command -v backlog >/dev/null 2>&1; then
    if command -v bun >/dev/null 2>&1 && bun add -g backlog.md >/dev/null 2>&1; then :
    elif command -v npm >/dev/null 2>&1 && npm i -g backlog.md >/dev/null 2>&1; then :; fi
  fi
  if ! command -v backlog >/dev/null 2>&1; then
    echo "  ⚠ backlog не поставлен. Вручную: bun add -g backlog.md  (или npm i -g backlog.md)"
    rep "backlog:          DEGRADED (bun add -g backlog.md)"
    return
  fi
  echo "  ✓ backlog $(backlog --version 2>/dev/null | head -1)"
  rep "backlog:          OK"
}
bootstrap_backlog

# serena — глобальный MCP через uvx; здесь только проверяем доступность рантайма.
bootstrap_serena() {
  if command -v uvx >/dev/null 2>&1 || command -v serena >/dev/null 2>&1; then
    echo "  ✓ serena-рантайм доступен (uvx/serena)"
    rep "serena:           OK"
  else
    echo "  ⚠ нет uvx для serena-MCP. Вручную: pip install uv  (или см. https://github.com/oraios/serena)"
    rep "serena:           DEGRADED (pip install uv)"
  fi
}
bootstrap_serena

# ============================================================================
# Phase 4 — адаптация конфигов (детерминированная; каждая правка идемпотентна)
# ============================================================================
echo "→ Phase 4: адаптация конфигов"

# 1) .mcp.json — хардкод пути ruflo → реальный путь (или bare "ruflo").
adapt_mcp() {
  local f="$TARGET/.mcp.json"
  [ -f "$f" ] || { rep "mcp_json:         SKIPPED (нет .mcp.json)"; return; }
  local want="${RUFLO_PATH:-ruflo}"
  if grep -q "\"command\": \"$want\"" "$f" 2>/dev/null; then
    echo "  · .mcp.json уже указывает на $want"
    rep "mcp_json:         SKIPPED (уже $want)"
    return
  fi
  # заменяем значение command у ruflo-сервера (строка с …ruflo")
  local tmp; tmp="$(mktemp)"
  sed -E "s#(\"command\": \")[^\"]*ruflo(\")#\1${want}\2#" "$f" > "$tmp" && mv "$tmp" "$f"
  echo "  ✓ .mcp.json: ruflo → $want"
  rep "mcp_json:         ADAPTED (ruflo → $want)"
}
adapt_mcp

# 2) .serena/project.yml — случайное project_name → basename проекта.
adapt_serena_name() {
  local f="$TARGET/.serena/project.yml"
  [ -f "$f" ] || { rep "serena_name:      SKIPPED (нет project.yml)"; return; }
  local cur
  cur="$(grep -E '^project_name:' "$f" | head -1 | sed -E 's/^project_name:[[:space:]]*"?([^"]*)"?.*/\1/')"
  # «случайное» имя серены: слово-слово-hex (напр. adoring-taussig-5427d4)
  if printf '%s' "$cur" | grep -qE '^[a-z]+-[a-z]+-[0-9a-f]{4,}$'; then
    local tmp; tmp="$(mktemp)"
    sed -E "s/^project_name:.*/project_name: \"${TARGET_NAME}\"/" "$f" > "$tmp" && mv "$tmp" "$f"
    echo "  ✓ .serena project_name: $cur → $TARGET_NAME"
    rep "serena_name:      SET $cur → $TARGET_NAME"
  else
    echo "  · .serena project_name уже кастомный ($cur) — не трогаю"
    rep "serena_name:      SKIPPED (уже $cur)"
  fi
}
adapt_serena_name

# 3) domain-profile — если нет заполненного, оставляем шаблон (интервью — в /paf-init).
adapt_domain_profile() {
  if [ -f "$TARGET/.claude/domain-profile.md" ]; then
    echo "  · domain-profile.md проекта существует — не трогаю"
    rep "domain_profile:   PRESENT"
    return
  fi
  # шаблон уже скопирован в корень; продублируем в .claude для удобства /paf-init
  if [ -f "$TARGET/domain-profile.template.md" ] && [ ! -f "$TARGET/.claude/domain-profile.template.md" ]; then
    cp "$TARGET/domain-profile.template.md" "$TARGET/.claude/domain-profile.template.md"
  fi
  echo "  · domain-profile.md отсутствует — нужен /paf-init (шаблон на месте)"
  rep "domain_profile:   TEMPLATE (запустите /paf-init)"
}
adapt_domain_profile

# 4) backlog init — операционный штаб в корне проекта.
adapt_backlog_init() {
  if ! command -v backlog >/dev/null 2>&1; then
    rep "backlog_init:     SKIPPED (нет backlog CLI)"; return
  fi
  if [ -d "$TARGET/backlog" ]; then
    echo "  · backlog/ уже инициализирован"
    rep "backlog_init:     SKIPPED (backlog/ существует)"
  elif ! git -C "$TARGET" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "  ⚠ target не git-репозиторий — backlog init пропущен (сначала git init)"
    rep "backlog_init:     SKIPPED (target не git-репо)"
    return
  else
    if ( cd "$TARGET" && backlog init "$TARGET_NAME" --defaults --integration-mode mcp --check-branches false >/dev/null 2>&1 ); then
      ( cd "$TARGET" && backlog config set remoteOperations false >/dev/null 2>&1 ) || true
      echo "  ✓ backlog/ инициализирован"
      rep "backlog_init:     OK"
    else
      echo "  ⚠ backlog init не удался — вручную: (cd $TARGET && backlog init)"
      rep "backlog_init:     FAILED"
    fi
  fi
  # конвенция операционного штаба рядом с доской
  if [ -f "$TARGET/backlog-ops.template.md" ] && [ -d "$TARGET/backlog" ]; then
    mkdir -p "$TARGET/backlog/docs"
    [ -f "$TARGET/backlog/docs/operational-hq.md" ] || \
      cp "$TARGET/backlog-ops.template.md" "$TARGET/backlog/docs/operational-hq.md"
  fi
}
adapt_backlog_init

# ============================================================================
# Phase 5 — self-check + машиночитаемый отчёт
# ============================================================================
echo "→ Phase 5: self-check"

check_present() {
  # key : путь
  if [ -e "$TARGET/$2" ]; then echo "  ✓ $2"; else echo "  ✗ $2 ОТСУТСТВУЕТ"; rep "MISSING_PATH:     $2"; fi
}
check_present skills   ".claude/skills"
check_present commands ".claude/commands"
check_present ground   "GROUND/NEXUS"
check_present docs      "docs"
check_present sadoc     "sa_documentation"
check_present mcp        ".mcp.json"

SKILL_N="$( { find "$TARGET/.claude/skills" -maxdepth 1 -mindepth 1 -type d 2>/dev/null || true; } | wc -l | tr -d ' ')"
CMD_N="$( { find "$TARGET/.claude/commands" -maxdepth 1 -name '*.md' 2>/dev/null || true; } | wc -l | tr -d ' ')"
rep "skills_count:     $SKILL_N"
rep "commands_count:   $CMD_N"

echo ""
echo "=== PAF-INSTALL-REPORT ==="
echo "mode:             $MODE"
echo "project:          $TARGET_NAME"
echo "target:           $TARGET"
for line in "${REPORT[@]}"; do echo "$line"; done
echo "=== END-REPORT ==="
echo ""

echo "✅ install.sh ($MODE) завершён: $TARGET ($SKILL_N скиллов, $CMD_N команд)"
echo "   Дальше (рассуждающие шаги — за /paf-install):"
echo "   1) заполнить .claude/domain-profile.md  →  /paf-init (интервью + засев GROUND)"
echo "   2) Reload Window в IDE — команды и MCP-серверы подхватятся"
echo "   3) OKR: /okr-context-gen <quarter> · БФТ: /bft-context-gen <epic> · Спринт: /sprint-roadmap <quarter>"
