"""Smoke-test helper for the PR-Agent (GLM-5) GitHub Actions workflow.

This file exists only to give PR-Agent a small, self-contained diff to
describe and review. Safe to delete once the workflow is confirmed working.
"""

from __future__ import annotations


def summarize_changes(files: list[str]) -> str:
    """Return a one-line summary of changed files.

    Intentionally trivial so the PR-Agent review has something to comment on.
    """
    if not files:
        return "no files changed"
    count = len(files)
    noun = "file" if count == 1 else "files"
    return f"{count} {noun} changed: {', '.join(sorted(files))}"


if __name__ == "__main__":
    print(summarize_changes(["a.py", "b.py"]))
