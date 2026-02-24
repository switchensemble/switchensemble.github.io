#!/usr/bin/env python3
"""
Generate Decap CMS admin/config.yml for a GitHub Pages Jekyll repo.

Key goals:
- NEVER emit invalid YAML (uses PyYAML safe_dump).
- Keep your year-folder structure:
    _posts/announcements-YYYY
    _posts/concerts-YYYY
    _repertoire/YYYY
- Create "Quick add" collections for CURRENT_YEAR first.
- Create full collections for 2021–2032 (newest first).

Requires: PyYAML
    python3 -m pip install pyyaml
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import yaml


# -------------------------
# USER CONFIG
# -------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]

OWNER_REPO = "switchensemble/switchensemble.github.io"
BRANCH = "master"

# Decap GitHub backend
AUTH_TYPE = "pkce"  # "oauth" or "pkce"
APP_ID = "Ov23liWfrNRFEBYQFhAW"

# URLs used by Decap (doesn't affect auth provider selection)
SITE_URL = "https://www.switchensemble.com"
DISPLAY_URL = "https://www.switchensemble.com"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

START_YEAR = 2021
END_YEAR = 2032
CURRENT_YEAR = date.today().year


# -------------------------
# HELPERS
# -------------------------
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def field(label: str, name: str, widget: str, **kwargs: Any) -> Dict[str, Any]:
    d: Dict[str, Any] = {"label": label, "name": name, "widget": widget}
    d.update(kwargs)
    return d


def hidden(name: str, default: str) -> Dict[str, Any]:
    return {"label": name.title(), "name": name, "widget": "hidden", "default": default}


def announcement_collection(name: str, label_txt: str, year: int) -> Dict[str, Any]:
    return {
        "name": name,
        "label": label_txt,
        "label_singular": "Announcement",
        "folder": f"_posts/announcements-{year}",
        "create": True,
        "extension": "md",
        "format": "frontmatter",
        "slug": "{{year}}-{{month}}-{{day}}-{{slug}}",
        "summary": "{{date}} — {{title}}",
        "sortable_fields": ["date", "title"],
        "fields": [
            {"label": "Layout", "name": "layout", "widget": "hidden", "default": "post"},
            {"label": "Category", "name": "categories", "widget": "hidden", "default": "news"},
            field("Title", "title", "string"),
            field("Date", "date", "datetime", date_format="YYYY-MM-DD", time_format=False, format="YYYY-MM-DD"),
            field("Author", "author", "string", required=False),
            field("Thumbnail", "thumbnail", "image", required=False),
            field("Header", "header", "image", required=False),
            field("Body", "body", "markdown"),
        ],
    }


def concert_collection(name: str, label_txt: str, year: int) -> Dict[str, Any]:
    return {
        "name": name,
        "label": label_txt,
        "label_singular": "Concert / Performance",
        "folder": f"_posts/concerts-{year}",
        "create": True,
        "extension": "md",
        "format": "frontmatter",
        "slug": "{{year}}-{{month}}-{{day}}-{{slug}}",
        "summary": "{{date}} — {{describe}}",
        "sortable_fields": ["date", "describe"],
        "fields": [
            {"label": "Layout", "name": "layout", "widget": "hidden", "default": "concert"},
            {"label": "Category", "name": "categories", "widget": "hidden", "default": "performance"},
            field("Short description (describe)", "describe", "text"),
            field("Date", "date", "datetime", date_format="YYYY-MM-DD", time_format=False, format="YYYY-MM-DD"),
            field("Time (optional)", "time", "string", required=False),
            {
                "label": "Location",
                "name": "location",
                "widget": "object",
                "required": False,
                "fields": [
                    field("Institution", "institution", "string", required=False),
                    field("Building", "building", "string", required=False),
                    field("Venue", "venue", "string", required=False),
                    field("Address", "address", "string", required=False),
                    field("City", "city", "string", required=False),
                    field("State", "state", "string", required=False),
                ],
            },
            {
                "label": "Program",
                "name": "program",
                "widget": "list",
                "required": False,
                "fields": [
                    field("Composer", "composer", "string"),
                    field("Title", "title", "string"),
                    field("Year", "year", "number", value_type="int", required=False),
                ],
            },
            field("Header image (headerImage)", "headerImage", "image", required=False),
            field("Thumbnail", "thumbnail", "image", required=False),
            field("Header (optional)", "header", "image", required=False),
            field("500px image (optional)", "500pxImage", "image", required=False),
            field("Photos folder (optional)", "photosFolder", "string", required=False),
            {"label": "Tags", "name": "tags", "widget": "list", "required": False, "field": field("Tag", "tag", "string")},
            field("Body", "body", "markdown", required=False),
        ],
    }


def repertoire_collection(name: str, label_txt: str, year: int) -> Dict[str, Any]:
    return {
        "name": name,
        "label": label_txt,
        "label_singular": "Work",
        "folder": f"_repertoire/{year}",
        "create": True,
        "extension": "md",
        "format": "frontmatter",
        "slug": "{{slug}}",
        "summary": f"{year} — {{composer.last}}, {{composer.first}} — {{title}}",
        "sortable_fields": ["title"],
        "fields": [
            {
                "label": "Composer",
                "name": "composer",
                "widget": "object",
                "fields": [
                    field("First", "first", "string", required=False),
                    field("Last", "last", "string", required=False),
                ],
            },
            field("Title", "title", "string"),
            field("Movements", "movements", "string", required=False),
            field("Duration (e.g. 25:00)", "duration", "string", required=False),
            field("Year composed", "yearComposed", "number", value_type="int", default=year),
            field("Performed by Switch (e.g. 2023, 2024)", "performedBySwitch", "string", required=False),
            {
                "label": "Commissioned / Written for",
                "name": "commissionedOrWrittenFor",
                "widget": "select",
                "required": False,
                "options": ["commissioned", "written for", "arrangement", "existing", "unknown"],
            },
            field("Size (e.g. septet)", "size", "string", required=False),
            {"label": "Instrumentation", "name": "instrumentation", "widget": "list", "required": False, "field": field("Instrument", "instrument", "string")},
            {"label": "Tags", "name": "tags", "widget": "list", "required": False, "field": field("Tag", "tag", "string")},
            {
                "label": "Media",
                "name": "media",
                "widget": "list",
                "required": False,
                "fields": [
                    field("Title", "title", "string", required=False),
                    {"label": "Type", "name": "type", "widget": "select", "required": False, "options": ["audio", "video", "score", "website", "other"]},
                    field("URL", "url", "string", required=False),
                ],
            },
            field("Body", "body", "markdown", required=False),
        ],
    }


def main() -> None:
    # Ensure year folders exist so Decap can create into future years
    posts = REPO_ROOT / "_posts"
    rep = REPO_ROOT / "_repertoire"
    ensure_dir(posts)
    ensure_dir(rep)
    ensure_dir(REPO_ROOT / "admin")

    for y in range(START_YEAR, END_YEAR + 1):
        ensure_dir(posts / f"announcements-{y}")
        ensure_dir(posts / f"concerts-{y}")
        ensure_dir(rep / f"{y}")
    ensure_dir(posts / f"announcements-{CURRENT_YEAR}")
    ensure_dir(posts / f"concerts-{CURRENT_YEAR}")
    ensure_dir(rep / f"{CURRENT_YEAR}")

    cfg: Dict[str, Any] = {
        "backend": {
            "name": "github",
            "repo": OWNER_REPO,
            "branch": BRANCH,
            "auth_type": AUTH_TYPE,
            "app_id": APP_ID,
        },
        "publish_mode": "editorial_workflow",
        "media_folder": MEDIA_FOLDER,
        "public_folder": PUBLIC_FOLDER,
        "site_url": SITE_URL,
        "display_url": DISPLAY_URL,
        "collections": [],
    }

    # Quick add (top)
    cfg["collections"].extend([
        announcement_collection(f"quick_announcement_{CURRENT_YEAR}", f"Quick add: Announcement ({CURRENT_YEAR})", CURRENT_YEAR),
        concert_collection(f"quick_concert_{CURRENT_YEAR}", f"Quick add: Concert / Performance ({CURRENT_YEAR})", CURRENT_YEAR),
        repertoire_collection(f"quick_repertoire_{CURRENT_YEAR}", f"Quick add: Repertoire / Work ({CURRENT_YEAR})", CURRENT_YEAR),
    ])

    # Curated years (newest first)
    for y in range(END_YEAR, START_YEAR - 1, -1):
        cfg["collections"].append(announcement_collection(f"announcements_{y}", f"News / Announcements ({y})", y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        cfg["collections"].append(concert_collection(f"concerts_{y}", f"Concerts / Performances ({y})", y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        cfg["collections"].append(repertoire_collection(f"repertoire_{y}", f"Repertoire / Works ({y})", y))

    out_path = REPO_ROOT / "admin" / "config.yml"
    out_text = yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True, width=120)
    out_path.write_text(out_text, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()