#!/usr/bin/env python3
"""
Generate admin/config.yml for Decap CMS using a GitHub backend + external OAuth proxy.

This version is designed for:
- GitHub Pages site
- Cloudflare Workers OAuth proxy (no Netlify)
- Year-based folders:
    _posts/announcements-YYYY
    _posts/concerts-YYYY
    _repertoire/YYYY
- Adds "Quick add" collections for CURRENT_YEAR at the top
- Generates curated collections for START_YEAR..END_YEAR (newest first)

Usage:
  python3 tools/generate_decap_config.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


# -------------------------
# EDIT THESE SETTINGS
# -------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]

GITHUB_REPO = "switchensemble/switchensemble.github.io"
GITHUB_BRANCH = "master"

# Cloudflare Worker OAuth proxy (workers.dev is fine)
OAUTH_BASE_URL = "https://decap-oauth.jasontbuchanan.workers.dev"
AUTH_ENDPOINT = "auth"  # keep "auth" unless your worker uses a different path

SITE_URL = "https://www.switchensemble.com"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

START_YEAR = 2021
END_YEAR = 2032
CURRENT_YEAR = date.today().year


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def header_yaml() -> str:
    # IMPORTANT: proxy flow => base_url + auth_endpoint
    # Do NOT include auth_type/app_id here.
    return f"""backend:
  name: github
  repo: {GITHUB_REPO}
  branch: {GITHUB_BRANCH}
  base_url: {OAUTH_BASE_URL}
  auth_endpoint: {AUTH_ENDPOINT}

publish_mode: editorial_workflow

media_folder: "{MEDIA_FOLDER}"
public_folder: "{PUBLIC_FOLDER}"

site_url: "{SITE_URL}"
display_url: "{SITE_URL}"

collections:
"""


def quick_announcement_block(year: int) -> str:
    return f"""  - name: "quick_announcement_{year}"
    label: "Quick add: Announcement ({year})"
    label_singular: "Announcement"
    folder: "_posts/announcements-{year}"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    summary: "{{{{date}}}} — {{{{title}}}}"
    sortable_fields: ["date", "title"]
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "post" }}
      - {{ label: "Category", name: "categories", widget: "hidden", default: "news" }}
      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Date", name: "date", widget: "datetime", date_format: "YYYY-MM-DD", time_format: false, format: "YYYY-MM-DD" }}
      - {{ label: "Author", name: "author", widget: "string", required: false }}
      - {{ label: "Thumbnail", name: "thumbnail", widget: "image", required: false }}
      - {{ label: "Header", name: "header", widget: "image", required: false }}
      - {{ label: "Body", name: "body", widget: "markdown" }}

"""


def quick_concert_block(year: int) -> str:
    return f"""  - name: "quick_concert_{year}"
    label: "Quick add: Concert / Performance ({year})"
    label_singular: "Concert / Performance"
    folder: "_posts/concerts-{year}"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    summary: "{{{{date}}}} — {{{{describe}}}}"
    sortable_fields: ["date", "describe"]
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "concert" }}
      - {{ label: "Category", name: "categories", widget: "hidden", default: "performance" }}
      - {{ label: "Short description (describe)", name: "describe", widget: "text" }}
      - {{ label: "Date", name: "date", widget: "datetime", date_format: "YYYY-MM-DD", time_format: false, format: "YYYY-MM-DD" }}
      - {{ label: "Time (optional)", name: "time", widget: "string", required: false }}

      - label: "Location"
        name: "location"
        widget: "object"
        required: false
        fields:
          - {{ label: "Institution", name: "institution", widget: "string", required: false }}
          - {{ label: "Building", name: "building", widget: "string", required: false }}
          - {{ label: "Venue", name: "venue", widget: "string", required: false }}
          - {{ label: "Address", name: "address", widget: "string", required: false }}
          - {{ label: "City", name: "city", widget: "string", required: false }}
          - {{ label: "State", name: "state", widget: "string", required: false }}

      - label: "Program"
        name: "program"
        widget: "list"
        required: false
        fields:
          - {{ label: "Composer", name: "composer", widget: "string" }}
          - {{ label: "Title", name: "title", widget: "string" }}
          - {{ label: "Year", name: "year", widget: "number", value_type: "int", required: false }}

      - {{ label: "Header image (headerImage)", name: "headerImage", widget: "image", required: false }}
      - {{ label: "Thumbnail", name: "thumbnail", widget: "image", required: false }}
      - {{ label: "Header (optional)", name: "header", widget: "image", required: false }}
      - {{ label: "500px image (optional)", name: "500pxImage", widget: "image", required: false }}

      - {{ label: "Photos folder (optional)", name: "photosFolder", widget: "string", required: false }}

      - label: "Tags"
        name: "tags"
        widget: "list"
        required: false
        field: {{ label: "Tag", name: "tag", widget: "string" }}

      - {{ label: "Body", name: "body", widget: "markdown", required: false }}

"""


def quick_repertoire_block(year: int) -> str:
    return f"""  - name: "quick_repertoire_{year}"
    label: "Quick add: Repertoire / Work ({year})"
    label_singular: "Work"
    folder: "_repertoire/{year}"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{slug}}}}"
    summary: "{year} — {{{{composer.last}}}}, {{{{composer.first}}}} — {{{{title}}}}"
    sortable_fields: ["title"]
    fields:
      - label: "Composer"
        name: "composer"
        widget: "object"
        fields:
          - {{ label: "First", name: "first", widget: "string", required: false }}
          - {{ label: "Last", name: "last", widget: "string", required: false }}

      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Movements", name: "movements", widget: "string", required: false }}
      - {{ label: "Duration (e.g. 25:00)", name: "duration", widget: "string", required: false }}
      - {{ label: "Year composed", name: "yearComposed", widget: "number", value_type: "int", default: {year} }}
      - {{ label: "Performed by Switch (e.g. 2023, 2024)", name: "performedBySwitch", widget: "string", required: false }}

      - label: "Commissioned / Written for"
        name: "commissionedOrWrittenFor"
        widget: "select"
        required: false
        options: ["commissioned", "written for", "arrangement", "existing", "unknown"]

      - {{ label: "Size (e.g. septet)", name: "size", widget: "string", required: false }}

      - label: "Instrumentation"
        name: "instrumentation"
        widget: "list"
        required: false
        field: {{ label: "Instrument", name: "instrument", widget: "string" }}

      - label: "Tags"
        name: "tags"
        widget: "list"
        required: false
        field: {{ label: "Tag", name: "tag", widget: "string" }}

      - label: "Media"
        name: "media"
        widget: "list"
        required: false
        fields:
          - {{ label: "Title", name: "title", widget: "string", required: false }}
          - label: "Type"
            name: "type"
            widget: "select"
            required: false
            options: ["audio", "video", "score", "website", "other"]
          - {{ label: "URL", name: "url", widget: "string", required: false }}

      - {{ label: "Body", name: "body", widget: "markdown", required: false }}

"""


def announcement_block(year: int) -> str:
    return f"""  - name: "announcements_{year}"
    label: "News / Announcements ({year})"
    label_singular: "Announcement"
    folder: "_posts/announcements-{year}"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    summary: "{{{{date}}}} — {{{{title}}}}"
    sortable_fields: ["date", "title"]
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "post" }}
      - {{ label: "Category", name: "categories", widget: "hidden", default: "news" }}
      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Date", name: "date", widget: "datetime", date_format: "YYYY-MM-DD", time_format: false, format: "YYYY-MM-DD" }}
      - {{ label: "Author", name: "author", widget: "string", required: false }}
      - {{ label: "Thumbnail", name: "thumbnail", widget: "image", required: false }}
      - {{ label: "Header", name: "header", widget: "image", required: false }}
      - {{ label: "Body", name: "body", widget: "markdown" }}

"""


def concert_block(year: int) -> str:
    # same as quick_concert but labeled as curated
    return quick_concert_block(year).replace(
        f'name: "quick_concert_{year}"',
        f'name: "concerts_{year}"'
    ).replace(
        f'label: "Quick add: Concert / Performance ({year})"',
        f'label: "Concerts / Performances ({year})"'
    )


def repertoire_block(year: int) -> str:
    return quick_repertoire_block(year).replace(
        f'name: "quick_repertoire_{year}"',
        f'name: "repertoire_{year}"'
    ).replace(
        f'label: "Quick add: Repertoire / Work ({year})"',
        f'label: "Repertoire / Works ({year})"'
    )


def main() -> None:
    posts_dir = REPO_ROOT / "_posts"
    rep_dir = REPO_ROOT / "_repertoire"
    admin_dir = REPO_ROOT / "admin"

    ensure_dir(posts_dir)
    ensure_dir(rep_dir)
    ensure_dir(admin_dir)

    # Ensure folders exist so Decap can create entries
    for y in range(START_YEAR, END_YEAR + 1):
        ensure_dir(posts_dir / f"announcements-{y}")
        ensure_dir(posts_dir / f"concerts-{y}")
        ensure_dir(rep_dir / f"{y}")

    ensure_dir(posts_dir / f"announcements-{CURRENT_YEAR}")
    ensure_dir(posts_dir / f"concerts-{CURRENT_YEAR}")
    ensure_dir(rep_dir / f"{CURRENT_YEAR}")

    out: list[str] = [header_yaml()]

    # Quick add
    out.append(quick_announcement_block(CURRENT_YEAR))
    out.append(quick_concert_block(CURRENT_YEAR))
    out.append(quick_repertoire_block(CURRENT_YEAR))

    # Curated years newest first
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(announcement_block(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(concert_block(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(repertoire_block(y))

    (admin_dir / "config.yml").write_text("".join(out), encoding="utf-8")
    print(f"✅ Wrote {admin_dir / 'config.yml'}")
    print(f"   Using OAuth proxy: {OAUTH_BASE_URL}/{AUTH_ENDPOINT}")


if __name__ == "__main__":
    main()