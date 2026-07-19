"""Validate that all SKILL.md files have valid YAML frontmatter."""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

VALID_FIELDS = {"name", "description", "metadata", "license", "compatibility"}
REQUIRED_FIELDS = {"name", "description"}


def find_skill_files():
    """Find all SKILL.md files."""
    return list(SKILLS_DIR.glob("*/SKILL.md"))


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fm_text = match.group(1)
    fields = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            fields[key] = value
    return fields


def test_all_skills_have_skill_md():
    """Every skill directory should have a SKILL.md."""
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith("."):
            skill_md = skill_dir / "SKILL.md"
            assert skill_md.exists(), f"Missing SKILL.md in {skill_dir.name}"


def test_all_skill_files_have_frontmatter():
    """Every SKILL.md should have YAML frontmatter."""
    for skill_file in find_skill_files():
        content = skill_file.read_text()
        assert content.startswith("---\n"), f"{skill_file} missing YAML frontmatter"


def test_required_fields_present():
    """Every SKILL.md should have 'name' and 'description' fields."""
    for skill_file in find_skill_files():
        content = skill_file.read_text()
        fields = parse_frontmatter(content)
        for req in REQUIRED_FIELDS:
            assert req in fields, f"{skill_file.name} missing required field '{req}'"


def test_no_invalid_fields():
    """No SKILL.md should have invalid frontmatter fields."""
    for skill_file in find_skill_files():
        content = skill_file.read_text()
        fields = parse_frontmatter(content)
        for key in fields:
            assert key in VALID_FIELDS, (
                f"{skill_file.name} has invalid field '{key}'. "
                f"Allowed: {VALID_FIELDS}"
            )


def test_description_with_colons_is_quoted():
    """Description fields containing colons should be quoted."""
    for skill_file in find_skill_files():
        content = skill_file.read_text()
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue
        fm_text = match.group(1)
        for line in fm_text.split("\n"):
            if line.strip().startswith("description:"):
                value = line.split(":", 1)[1].strip()
                if ":" in value:
                    assert value.startswith('"') or value.startswith("'"), (
                        f"{skill_file.name} has unquoted description with colon: {value}"
                    )


def test_skill_count():
    """Should have exactly 7 skills."""
    skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    assert len(skill_dirs) == 7, f"Expected 7 skills, found {len(skill_dirs)}: {[d.name for d in skill_dirs]}"
