#!/usr/bin/env python3
"""
Generate Decap CMS admin/config.yml for switchensemble.github.io

Key points:
- GitHub backend with PKCE
- Uses a custom OAuth proxy (Cloudflare Worker / Pages Function) via backend.base_url
  so Decap DOES NOT redirect to Netlify for auth.
- Curated collections for announcements, concerts, repertoire: START_YEAR–END_YEAR
- Adds "Quick add" collections for CURRENT_YEAR at the top
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


# -------------------------
# EDIT THESE SETTINGS
# -------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]

GITHUB_REPO = "switchensemble/switchensemble.github.io"
GITHUB_BRANCH = "master"

# Your GitHub OAuth App Client ID
GITHUB_OAUTH_CLIENT_ID = "Ov23liWfrNRFEBYQFhAW"

# IMPORTANT: Your Cloudflare Worker / Pages Function that implements the Decap OAuth proxy
# Example: https://decap-oauth.switchensemble.com
OAUTH_PROXY_BASE_URL = "https://decap-oauth.switchensemble.com"

# Where your public site lives (what you want Decap to show as “View site”)
SITE_URL = "https://www.switchensemble.com"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

START_YEAR = 2021
END_YEAR = 2032


# -------------------------
# INTERNALS
# -------------------------
CURRENT_YEAR = date.today().year
ADMIN_DIR = REPO_ROOT / "admin"
POSTS_DIR = REPO_ROOT / "_posts"
REPERTOIRE_DIR = REPO_ROOT / "_repertoire"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def yml_header() -> str:
    # NOTE: base_url is what stops the Netlify redirect.
    return f"""backend:
  name: github
  repo: {GITHUB_REPO}
  branch: {GITHUB_BRANCH}
  auth_type: pkce
  app_id: {GITHUB_OAUTH_CLIENT_ID}
  base_url: "{OAUTH_PROXY_BASE_URL}"

publish_mode: editorial_workflow

media_folder: "{MEDIA_FOLDER}"
public_folder: "{PUBLIC_FOLDER}"

site_url: "{SITE_URL}"
display_url: "{SITE_URL}"

collections:
"""


def quick_announcement(year: int) -> str:
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


def quick_concert(year: int) -> str:
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


def quick_repertoire(year: int) -> str:
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


def announcement(year: int) -> str:
    # same as quick, just different label/name
    return quick_announcement(year).replace(f'quick_announcement_{year}', f'announcements_{year}').replace(
        f'Quick add: Announcement ({year})', f'News / Announcements ({year})'
    )


def concert(year: int) -> str:
    return quick_concert(year).replace(f'quick_concert_{year}', f'concerts_{year}').replace(
        f'Quick add: Concert / Performance ({year})', f'Concerts / Performances ({year})'
    )


def repertoire(year: int) -> str:
    return quick_repertoire(year).replace(f'quick_repertoire_{year}', f'repertoire_{year}').replace(
        f'Quick add: Repertoire / Work ({year})', f'Repertoire / Works ({year})'
    )


def main() -> None:
    ensure_dir(ADMIN_DIR)
    ensure_dir(POSTS_DIR)
    ensure_dir(REPERTOIRE_DIR)

    # Make sure year folders exist so Decap can create new entries
    for y in range(START_YEAR, END_YEAR + 1):
        ensure_dir(POSTS_DIR / f"announcements-{y}")
        ensure_dir(POSTS_DIR / f"concerts-{y}")
        ensure_dir(REPERTOIRE_DIR / f"{y}")

    ensure_dir(POSTS_DIR / f"announcements-{CURRENT_YEAR}")
    ensure_dir(POSTS_DIR / f"concerts-{CURRENT_YEAR}")
    ensure_dir(REPERTOIRE_DIR / f"{CURRENT_YEAR}")

    parts: list[str] = [yml_header()]

    # Quick add at top
    parts += [quick_announcement(CURRENT_YEAR), quick_concert(CURRENT_YEAR), quick_repertoire(CURRENT_YEAR)]

    # Curated years (newest first)
    for y in range(END_YEAR, START_YEAR - 1, -1):
        parts.append(announcement(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        parts.append(concert(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        parts.append(repertoire(y))

    out_path = ADMIN_DIR / "config.yml"
    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {out_path} (years {START_YEAR}–{END_YEAR} + quick add {CURRENT_YEAR}).")
    print("IMPORTANT: backend.base_url must point at your OAuth proxy to avoid Netlify auth redirects.")


if __name__ == "__main__":
    main()