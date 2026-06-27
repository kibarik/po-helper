"""Render-check для Mermaid-блока Blueprint. Блокирующий гейт.

Выбор рендерера: mmdc → npx @mermaid-js/mermaid-cli → None.
Если None или рендер падает после N попыток — задача блокируется (см. block_message).
"""
import shutil
import subprocess
import tempfile
import pathlib

NPX_CMD = ["npx", "-y", "@mermaid-js/mermaid-cli", "-i"]

# Маркеры, по которым сбой рендера — проблема ОКРУЖЕНИЯ (Chrome/puppeteer/сеть),
# а НЕ синтаксиса Mermaid. Используются classify_failure().
_ENV_MARKERS = (
    "could not find chrome",
    "chrome-headless-shell",
    "puppeteer",
    "browsers install",
    "failed to launch",
    "could not determine executable",
    "enotfound",
    "etimedout",
    "network",
    "npm error",
    "no mermaid renderer available",
    "renderer failed to run",
    "timed out",
)


def pick_renderer():
    """Вернуть базовую команду рендерера или None, если ни один недоступен."""
    if shutil.which("mmdc"):
        return ["mmdc", "-i"]
    if shutil.which("npx"):
        return list(NPX_CMD)
    return None


def render_check(mermaid_code, timeout=120):
    """Отрендерить mermaid_code во временный SVG.

    Возвращает (ok: bool, log: str). ok=False, если рендерера нет или рендер упал.
    """
    cmd = pick_renderer()
    if cmd is None:
        return False, "no Mermaid renderer available (install mmdc or Node/npx)"
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "in.mmd"
        out = pathlib.Path(d) / "out.svg"
        src.write_text(mermaid_code, encoding="utf-8")
        try:
            r = subprocess.run(
                cmd + [str(src), "-o", str(out)],
                capture_output=True, text=True, timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            return False, f"renderer failed to run: {e}"
        if r.returncode != 0 or not out.exists():
            return False, (r.stderr or r.stdout or "render failed").strip()
        return True, "OK"


def classify_failure(log):
    """Классифицировать причину сбоя рендера.

    'environment' — рендерер/Chrome/сеть недоступны (НЕ ошибка Mermaid).
    'syntax'      — Mermaid не распарсился (ошибка в диаграмме).
    """
    low = (log or "").lower()
    if any(mk in low for mk in _ENV_MARKERS):
        return "environment"
    return "syntax"


def block_message(log):
    """Текст блокировки для пользователя (жёсткий гейт)."""
    return (
        "⛔ Не могу продолжить: ошибка рендера Mermaid.\n"
        "Для успешного завершения задачи нужно исправить:\n"
        f"{log}\n"
        "Задача НЕ завершена, пока Mermaid не рендерится чисто."
    )


def unavailable_message(log):
    """Текст, когда рендерер недоступен (окружение). НЕ выдаём за ошибку Mermaid."""
    return (
        "⛔ Не могу продолжить: Mermaid-рендерер недоступен в окружении "
        "(это НЕ ошибка диаграммы).\n"
        "Разовая установка для стабильного цикла отладки:\n"
        "  npx -y puppeteer browsers install chrome-headless-shell\n"
        f"Детали: {log}\n"
        "Задача НЕ завершена, пока рендер не выполнится."
    )


if __name__ == "__main__":
    import sys
    ok, log = render_check(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    if ok:
        print("OK")
        sys.exit(0)
    if classify_failure(log) == "environment":
        print(unavailable_message(log))
    else:
        print(block_message(log))
    sys.exit(1)
