#!/usr/bin/env python3
"""
Generate Decap CMS admin/config.yml for switchensemble.com (GitHub backend + Cloudflare Worker OAuth proxy)

This generates:
- backend: github
- base_url: your site origin (so OAuth callback can postMessage reliably)
- auth_endpoint: /oauth/auth (Worker route: www.switchensemble.com/oauth/*)

Collections:
- "Quick add" for CURRENT_YEAR at top
- Curated year-based collections for announcements, concerts, repertoire
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

# -------------------------
# CONFIG YOU MAY CHANGE
# -------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]

GITHUB_REPO = "switchensemble/switchensemble.github.io"
BRANCH = "master"

SITE_ORIGIN = "https://www.switchensemble.com"

# Cloudflare Worker is attached via a Worker Route like:
#   www.switchensemble.com/oauth/*
# and the worker serves /oauth/auth and /oauth/callback
OAUTH_AUTH_ENDPOINT = "/oauth/auth"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

START_YEAR = 2021
END_YEAR = 2032
CURRENT_YEAR = date.today().year


def header_yaml() -> str:
    return f"""backend:
  name: github
  repo: {GITHUB_REPO}
  branch: {BRANCH}

  # OAuth proxy (Cloudflare Worker Route)
  base_url: {SITE_ORIGIN}
  auth_endpoint: {OAUTH_AUTH_ENDPOINT}

publish_mode: editorial_workflow

media_folder: "{MEDIA_FOLDER}"
public_folder: "{PUBLIC_FOLDER}"

site_url: "{SITE_ORIGIN}"
display_url: "{SITE_ORIGIN}"

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
    # Same schema as quick announcement, just different label/name
    return quick_announcement_block(year).replace(
        f'name: "quick_announcement_{year}"', f'name: "announcements_{year}"'
    ).replace(
        f'Quick add: Announcement ({year})', f'News / Announcements ({year})'
    )


def concert_block(year: int) -> str:
    return quick_concert_block(year).replace(
        f'name: "quick_concert_{year}"', f'name: "concerts_{year}"'
    ).replace(
        f'Quick add: Concert / Performance ({year})', f'Concerts / Performances ({year})'
    )


def repertoire_block(year: int) -> str:
    return quick_repertoire_block(year).replace(
        f'name: "quick_repertoire_{year}"', f'name: "repertoire_{year}"'
    ).replace(
        f'Quick add: Repertoire / Work ({year})', f'Repertoire / Works ({year})'
    )


def main() -> None:
    out = [header_yaml()]

    # Quick add at top
    out.append(quick_announcement_block(CURRENT_YEAR))
    out.append(quick_concert_block(CURRENT_YEAR))
    out.append(quick_repertoire_block(CURRENT_YEAR))

    # Curated years (newest first)
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(announcement_block(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(concert_block(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(repertoire_block(y))

    admin_dir = REPO_ROOT / "admin"
    admin_dir.mkdir(parents=True, exist_ok=True)
    (admin_dir / "config.yml").write_text("".join(out), encoding="utf-8")
    print("Wrote admin/config.yml (GitHub backend + CF Worker OAuth; curated years + quick add).")


if __name__ == "__main__":
    main()