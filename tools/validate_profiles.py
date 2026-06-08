#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILTIN_RULES = {
    "placeholder-text",
    "repeated-punctuation",
    "cjk-spacing",
    "long-paragraph",
    "consecutive-empty-paragraphs",
    "missing-references",
    "missing-heading-styles",
}
SEVERITIES = {"error", "warning", "info"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)]

    if data.get("version") != 1:
        errors.append("version must be 1")
    settings = data.get("settings", {})
    if not isinstance(settings, dict):
        errors.append("settings must be an object")
    elif not isinstance(settings.get("max_paragraph_chars", 600), int):
        errors.append("max_paragraph_chars must be an integer")
    disabled = data.get("disabled_rules", [])
    if not isinstance(disabled, list) or set(disabled) - BUILTIN_RULES:
        errors.append("disabled_rules contains an unknown rule")
    overrides = data.get("severity_overrides", {})
    if not isinstance(overrides, dict) or set(overrides) - BUILTIN_RULES:
        errors.append("severity_overrides contains an unknown rule")
    elif any(value not in SEVERITIES for value in overrides.values()):
        errors.append("severity_overrides contains an invalid severity")

    custom_ids: set[str] = set()
    for index, rule in enumerate(data.get("pattern_rules", [])):
        if not isinstance(rule, dict):
            errors.append(f"pattern_rules[{index}] must be an object")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or rule_id in BUILTIN_RULES | custom_ids:
            errors.append(f"pattern_rules[{index}] has an invalid or duplicate id")
        else:
            custom_ids.add(rule_id)
        if rule.get("severity", "warning") not in SEVERITIES:
            errors.append(f"pattern_rules[{index}] has an invalid severity")
        try:
            re.compile(rule.get("pattern", ""))
        except (re.error, TypeError) as exc:
            errors.append(f"pattern_rules[{index}] has an invalid pattern: {exc}")
        if not isinstance(rule.get("message"), str) or not rule.get("message"):
            errors.append(f"pattern_rules[{index}] must have a message")
    return errors


def main() -> int:
    failed = False
    for profile in sorted((ROOT / "profiles").glob("*.json")):
        errors = validate(profile)
        if errors:
            failed = True
            for error in errors:
                print(f"{profile.relative_to(ROOT)}: {error}")
        else:
            print(f"{profile.relative_to(ROOT)}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

