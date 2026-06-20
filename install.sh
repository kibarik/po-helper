#!/usr/bin/env bash
# po-helper installer — копирует навык bft-writer и команды /bft-gen, /bft-context-gen
# в .claude/ текущего проекта (Claude Code). Существующие файлы не удаляются.
set -euo pipefail

# Определяем папку источника (рядом с этим скриптом)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILLS="$SCRIPT_DIR/.claude/skills"
SRC_COMMANDS="$SCRIPT_DIR/.claude/commands"

if [ ! -d "$SRC_SKILLS" ]; then
  echo "❌ Не найден $SRC_SKILLS. Запускайте install.sh из корня клона po-helper." >&2
  exit 1
fi

# Целевой корень агента в проекте пользователя
DEST_ROOT="${1:-$PWD/.claude}"
DEST_SKILLS="$DEST_ROOT/skills"
DEST_COMMANDS="$DEST_ROOT/commands"

echo "→ Целевой корень: $DEST_ROOT"
mkdir -p "$DEST_SKILLS" "$DEST_COMMANDS"

# Копируем навык bft-writer (с сохранением структуры)
mkdir -p "$DEST_SKILLS/bft-writer"
cp -R "$SRC_SKILLS/bft-writer/." "$DEST_SKILLS/bft-writer/" 2>/dev/null || true

# Копируем команды (не перезаписываем существующие)
for cmd in bft-gen bft-context-gen; do
  if [ -f "$SRC_COMMANDS/$cmd.md" ]; then
    if [ -f "$DEST_COMMANDS/$cmd.md" ]; then
      echo "  · $cmd.md уже существует — пропускаю"
    else
      cp "$SRC_COMMANDS/$cmd.md" "$DEST_COMMANDS/$cmd.md"
      echo "  ✓ commands/$cmd.md"
    fi
  fi
done

echo ""
echo "✅ po-helper установлен в $DEST_ROOT"
echo "   Навык:   skills/bft-writer/ (SKILL + resources + examples)"
echo "   Команды: commands/bft-gen.md, commands/bft-context-gen.md"
echo ""
echo "Перезагрузите IDE (Reload Window), чтобы команды появились в чате."
echo "Дальше: /bft-context-gen <epic> <key>  →  /bft-gen <epic>"
