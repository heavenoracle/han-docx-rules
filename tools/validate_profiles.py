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
    else:
        max_chars = settings.get("max_paragraph_chars", 600)
        if (
            not isinstance(max_chars, int)
            or isinstance(max_chars, bool)
            or max_chars < 1
        ):
            errors.append("max_paragraph_chars must be a positive integer")
        if not isinstance(settings.get("require_references", True), bool):
            errors.append("require_references must be a boolean")
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
            flags_text = rule.get("flags", "")
            if not isinstance(flags_text, str) or any(
                flag not in "im" for flag in flags_text
            ):
                errors.append(f"pattern_rules[{index}] has invalid flags")
                flags_text = ""
            flags = (re.I if "i" in flags_text else 0) | (
                re.M if "m" in flags_text else 0
            )
            re.compile(rule.get("pattern", ""), flags)
        except (re.error, TypeError) as exc:
            errors.append(f"pattern_rules[{index}] has an invalid pattern: {exc}")
        if not isinstance(rule.get("message"), str) or not rule.get("message"):
            errors.append(f"pattern_rules[{index}] must have a message")
        if "rationale" in rule and (
            not isinstance(rule["rationale"], str) or not rule["rationale"]
        ):
            errors.append(f"pattern_rules[{index}] has an invalid rationale")
        false_positives = rule.get("false_positives", [])
        if not isinstance(false_positives, list) or not all(
            isinstance(item, str) and item for item in false_positives
        ):
            errors.append(f"pattern_rules[{index}] has invalid false_positives")
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
