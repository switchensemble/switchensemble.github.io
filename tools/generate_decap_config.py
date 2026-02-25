#!/usr/bin/env python3
"""
Generate Decap CMS admin/config.yml for switchensemble.com

Anchor-free (Decap schema-safe) config:
- Announcements 2026: layout=post, categories=news
- Concerts/Performances 2026–2029: layout=concert, categories=performance + program/location fields
- Repertoire 2023–2032: _repertoire/<year>/
"""

from pathlib import Path

GITHUB_REPO = "switchensemble/switchensemble.github.io"
BRANCH = "master"

OAUTH_BASE_URL = "https://www.switchensemble.com"
AUTH_ENDPOINT = "/auth"

SITE_ORIGIN = "https://www.switchensemble.com"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

OUTPUT_PATH = Path("admin/config.yml")

REPERTOIRE_MEDIA_TYPES = ["audio", "video", "score", "link", "other"]

REPERTOIRE_START_YEAR = 2023
REPERTOIRE_END_YEAR = 2032

CONCERT_START_YEAR = 2026
CONCERT_END_YEAR = 2029


def header_block() -> str:
    return f"""backend:
  name: github
  repo: {GITHUB_REPO}
  branch: {BRANCH}

  # OAuth proxy (Cloudflare Worker)
  base_url: {OAUTH_BASE_URL}
  auth_endpoint: {AUTH_ENDPOINT}

publish_mode: editorial_workflow

media_folder: "{MEDIA_FOLDER}"
public_folder: "{PUBLIC_FOLDER}"

site_url: "{SITE_ORIGIN}"
display_url: "{SITE_ORIGIN}"

collections:
"""


def announcements_collection_block() -> str:
    return """  - name: "quick_announcement_2026"
    label: "Quick add: Announcement (2026)"
    label_singular: "Announcement"
    folder: "_posts/announcements-2026"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{year}}-{{month}}-{{day}}-{{slug}}"
    summary: "{{date}} – {{title}}"
    sortable_fields: ["date", "title"]
    fields:
      - { label: "Layout", name: "layout", widget: "hidden", default: "post" }
      - { label: "Category", name: "categories", widget: "hidden", default: "news" }

      - { label: "Title", name: "title", widget: "string" }

      - label: "Date"
        name: "date"
        widget: "datetime"
        format: "YYYY-MM-DD"
        time_format: false
        picker_utc: true

      # Decap doesn't auto-fill author from GitHub login; commit author reflects the GitHub user.
      - { label: "Author", name: "author", widget: "string", required: false, default: "Switch Ensemble" }

      - { label: "Thumbnail", name: "thumbnail", widget: "image", required: true }
      - { label: "Header", name: "header", widget: "image", required: true }

      - { label: "Body", name: "body", widget: "markdown" }
"""


def concert_collection_block(year: int) -> str:
    return f"""  - name: "quick_concert_{year}"
    label: "Quick add: Concert / Performance ({year})"
    label_singular: "Concert"
    folder: "_posts/concerts-{year}"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    summary: "{{{{date}}}} – {{{{location.institution}}}} ({{{{location.city}}}}, {{{{location.state}}}})"
    sortable_fields: ["date", "title"]
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "concert" }}
      - {{ label: "Category", name: "categories", widget: "hidden", default: "performance" }}

      - {{ label: "Title (internal)", name: "title", widget: "string", required: false, hint: "Optional. Used only for CMS listing; site may ignore it." }}

      - {{ label: "Describe", name: "describe", widget: "string", required: true }}

      - label: "Date"
        name: "date"
        widget: "datetime"
        format: "YYYY-MM-DD"
        time_format: false
        picker_utc: true

      - {{ label: "Time", name: "time", widget: "string", required: true, hint: "Example: 7:30pm" }}

      - label: "Location"
        name: "location"
        widget: "object"
        fields:
          - {{ label: "Institution", name: "institution", widget: "string", required: true }}
          - {{ label: "Building", name: "building", widget: "string", required: false }}
          - {{ label: "Venue", name: "venue", widget: "string", required: false }}
          - {{ label: "Address", name: "address", widget: "string", required: false }}
          - {{ label: "City", name: "city", widget: "string", required: true }}
          - {{ label: "State", name: "state", widget: "string", required: true }}
          - {{ label: "Zip", name: "zip", widget: "string", required: false }}

      - label: "Program"
        name: "program"
        widget: "list"
        summary: "{{{{fields.composer}}}} — {{{{fields.title}}}} ({{{{fields.year}}}})"
        fields:
          - {{ label: "Composer", name: "composer", widget: "string", required: true }}
          - {{ label: "Title", name: "title", widget: "string", required: true }}
          - {{ label: "Year", name: "year", widget: "string", required: false }}

      - label: "Text"
        name: "text"
        widget: "object"
        required: false
        fields:
          - {{ label: "Below", name: "below", widget: "string", required: false }}

      - {{ label: "Author", name: "author", widget: "string", required: false, default: "Switch Ensemble" }}

      - {{ label: "Thumbnail", name: "thumbnail", widget: "image", required: true }}
      - {{ label: "Header", name: "header", widget: "image", required: true }}

      - {{ label: "Body", name: "body", widget: "markdown" }}
"""


def repertoire_fields_block(indent: str = "    ") -> str:
    mtypes = REPERTOIRE_MEDIA_TYPES
    return f"""{indent}fields:
{indent}  - label: "Composer"
{indent}    name: "composer"
{indent}    widget: "object"
{indent}    fields:
{indent}      - {{ label: "First", name: "first", widget: "string" }}
{indent}      - {{ label: "Last", name: "last", widget: "string" }}

{indent}  - {{ label: "Title", name: "title", widget: "string" }}

{indent}  - label: "Movements"
{indent}    name: "movements"
{indent}    widget: "list"
{indent}    required: false

{indent}  - {{ label: "Duration (mm:ss)", name: "duration", widget: "string", required: false }}

{indent}  - label: "Year Composed"
{indent}    name: "yearComposed"
{indent}    widget: "number"
{indent}    value_type: "int"
{indent}    min: 0

{indent}  - label: "Performed By Switch (years)"
{indent}    name: "performedBySwitch"
{indent}    widget: "string"
{indent}    required: false

{indent}  - label: "Commissioned or Written For"
{indent}    name: "commissionedOrWrittenFor"
{indent}    widget: "select"
{indent}    options: ["commissioned", "written for", "unknown"]
{indent}    default: "unknown"

{indent}  - {{ label: "Size", name: "size", widget: "string", required: false }}

{indent}  - label: "Instrumentation"
{indent}    name: "instrumentation"
{indent}    widget: "list"
{indent}    required: false

{indent}  - label: "Tags"
{indent}    name: "tags"
{indent}    widget: "list"
{indent}    required: false

{indent}  - label: "Media"
{indent}    name: "media"
{indent}    widget: "list"
{indent}    required: false
{indent}    fields:
{indent}      - {{ label: "Title", name: "title", widget: "string", required: false }}
{indent}      - {{ label: "Type", name: "type", widget: "select", required: false, options: {mtypes} }}
{indent}      - {{ label: "URL", name: "url", widget: "string", required: false }}
"""


def repertoire_collection_block(year: int, anchor_first: bool) -> str:
    if anchor_first:
        fields = repertoire_fields_block(indent="    ").replace("fields:", "fields: &repertoire_fields", 1)
        fields_ref = fields
    else:
        fields_ref = "    fields: *repertoire_fields\n"

    return f"""  - name: "repertoire_{year}"
    label: "Repertoire ({year})"
    label_singular: "Repertoire Work"
    folder: "_repertoire/{year}"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{slug}}}}"
    summary: "{{{{title}}}} — {{{{composer.last}}}} ({{{{yearComposed}}}})"
    sortable_fields: ["title", "yearComposed"]
{fields_ref}"""


def build_yaml() -> str:
    parts = [header_block(), announcements_collection_block()]

    for y in range(CONCERT_START_YEAR, CONCERT_END_YEAR + 1):
        parts.append(concert_collection_block(y))

    first = True
    for y in range(REPERTOIRE_START_YEAR, REPERTOIRE_END_YEAR + 1):
        parts.append(repertoire_collection_block(y, anchor_first=first))
        first = False

    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_yaml(), encoding="utf-8")
    print(f"✅ Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()