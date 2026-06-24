#!/usr/bin/env bash
# po-helper installer — копирует навыки и команды фреймворка в .claude/ проекта (Claude Code).
#
# Режимы:
#   bash install.sh              — install: framework-файлы копируются, существующие НЕ трогаются
#   bash install.sh --update     — update:  framework-файлы ПЕРЕЗАПИСЫВАЮТСЯ свежими из po-helper
#
# В любом режиме domain-profile проекта (.claude/domain-profile.md) и доменные данные
# НЕ трогаются никогда — обновляется только generic-слой фреймворка.
set -euo pipefail

# --- разбор аргументов ---
MODE="install"
DEST_ROOT=""
for arg in "$@"; do
  case "$arg" in
    --update) MODE="update" ;;
    --install) MODE="install" ;;
    *) DEST_ROOT="$arg" ;;  # позиционный: целевой .claude
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILLS="$SCRIPT_DIR/.claude/skills"
SRC_COMMANDS="$SCRIPT_DIR/.claude/commands"
SRC_WORKFLOWS="$SCRIPT_DIR/.claude/workflows"
SRC_PROFILE_TPL="$SCRIPT_DIR/domain-profile.template.md"

if [ ! -d "$SRC_SKILLS" ]; then
  echo "❌ Не найден $SRC_SKILLS. Запускайте install.sh из корня клона po-helper." >&2
  exit 1
fi

DEST_ROOT="${DEST_ROOT:-$PWD/.claude}"
DEST_SKILLS="$DEST_ROOT/skills"
DEST_COMMANDS="$DEST_ROOT/commands"
DEST_WORKFLOWS="$DEST_ROOT/workflows"

echo "→ Режим: $MODE"
echo "→ Целевой корень: $DEST_ROOT"
mkdir -p "$DEST_SKILLS" "$DEST_COMMANDS" "$DEST_WORKFLOWS"

# Навыки фреймворка (каждый — каталог с SKILL.md + resources + examples)
SKILLS=(bft-writer okr-planner po-research)

# Команды фреймворка
COMMANDS=(
  bft-context-gen bft-context-gen-deep bft-problem bft-concept bft-debate bft-draft bft-validate bft-deliver
  okr-context-gen okr-objectives okr-key-results okr-debate okr-enrich okr-validate okr-deliver
  po-research
)

# --- навыки ---
# examples/ — доменный слой: в --update НЕ перезаписываем уже существующие
# эталоны проекта (это его few-shot под свой домен), но добавляем новые.
# SKILL.md и resources/ — generic-логика фреймворка, обновляются всегда.
for skill in "${SKILLS[@]}"; do
  [ -d "$SRC_SKILLS/$skill" ] || continue
  if [ -d "$DEST_SKILLS/$skill" ] && [ "$MODE" = "install" ]; then
    echo "  · skills/$skill уже есть — пропускаю (для обновления: --update)"
    continue
  fi
  mkdir -p "$DEST_SKILLS/$skill"
  if [ "$MODE" = "update" ] && [ -d "$DEST_SKILLS/$skill/examples" ]; then
    # обновляем SKILL.md + resources/, сохраняем кастомные examples проекта
    [ -f "$SRC_SKILLS/$skill/SKILL.md" ] && cp "$SRC_SKILLS/$skill/SKILL.md" "$DEST_SKILLS/$skill/SKILL.md"
    if [ -d "$SRC_SKILLS/$skill/resources" ]; then
      mkdir -p "$DEST_SKILLS/$skill/resources"
      cp -R "$SRC_SKILLS/$skill/resources/." "$DEST_SKILLS/$skill/resources/"
    fi
    if [ -d "$SRC_SKILLS/$skill/examples" ]; then
      mkdir -p "$DEST_SKILLS/$skill/examples"
      for ex in "$SRC_SKILLS/$skill/examples/"*; do
        [ -e "$ex" ] || continue
        exname="$(basename "$ex")"
        [ -e "$DEST_SKILLS/$skill/examples/$exname" ] || cp -R "$ex" "$DEST_SKILLS/$skill/examples/$exname"
      done
    fi
    echo "  ✓ skills/$skill/ (SKILL+resources обновлены, examples проекта сохранены)"
  else
    cp -R "$SRC_SKILLS/$skill/." "$DEST_SKILLS/$skill/"
    echo "  ✓ skills/$skill/"
  fi
done

# --- команды ---
for cmd in "${COMMANDS[@]}"; do
  [ -f "$SRC_COMMANDS/$cmd.md" ] || continue
  if [ -f "$DEST_COMMANDS/$cmd.md" ] && [ "$MODE" = "install" ]; then
    echo "  · commands/$cmd.md уже есть — пропускаю (для обновления: --update)"
  else
    cp "$SRC_COMMANDS/$cmd.md" "$DEST_COMMANDS/$cmd.md"
    echo "  ✓ commands/$cmd.md"
  fi
done

# --- workflows (.js для Workflow-оркестрации) ---
if [ -d "$SRC_WORKFLOWS" ]; then
  for wf in "$SRC_WORKFLOWS"/*.js; do
    [ -f "$wf" ] || continue
    name="$(basename "$wf")"
    if [ -f "$DEST_WORKFLOWS/$name" ] && [ "$MODE" = "install" ]; then
      echo "  · workflows/$name уже есть — пропускаю (для обновления: --update)"
    else
      cp "$wf" "$DEST_WORKFLOWS/$name"
      echo "  ✓ workflows/$name"
    fi
  done
fi

# --- доменный профиль: НИКОГДА не перезаписываем заполненный профиль проекта ---
if [ -f "$SRC_PROFILE_TPL" ]; then
  if [ -f "$DEST_ROOT/domain-profile.md" ]; then
    echo "  · domain-profile.md проекта существует — НЕ трогаю (это ваш домен)"
  else
    cp "$SRC_PROFILE_TPL" "$DEST_ROOT/domain-profile.template.md"
    echo "  ✓ domain-profile.template.md (скопируйте в domain-profile.md и заполните под проект)"
  fi
fi

echo ""
echo "✅ po-helper $MODE завершён в $DEST_ROOT"
echo "   Навыки:  ${SKILLS[*]}"
echo "   Пайплайны: /bft-* (БФТ)  ·  /okr-* (квартальный OKR)  ·  /po-research (контекст)"
echo ""
echo "Дальше:"
echo "  1) cp $DEST_ROOT/domain-profile.template.md $DEST_ROOT/domain-profile.md  и заполните под проект"
echo "  2) Reload Window в IDE — команды появятся в чате"
echo "  3) OKR: /okr-context-gen <quarter>   ·   БФТ: /bft-context-gen <epic>"
