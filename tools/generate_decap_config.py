#!/usr/bin/env python3
"""
Generate Decap CMS admin/config.yml for switchensemble.com

- GitHub backend (PKCE)
- Curated collections 2021–2032
- Quick add collections for current year
"""

from datetime import date
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------
REPO = Path(__file__).resolve().parents[1]
ADMIN_DIR = REPO / "admin"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

SITE_URL = "https://www.switchensemble.com"

START_YEAR = 2021
END_YEAR = 2032
CURRENT_YEAR = date.today().year

GITHUB_REPO = "switchensemble/switchensemble.github.io"
GITHUB_BRANCH = "master"
GITHUB_APP_ID = "Ov23liWfrNRFEBYQFhAW"


# -----------------------------
# HEADER
# -----------------------------
def header_yaml() -> str:
    return f"""backend:
  name: github
  repo: {GITHUB_REPO}
  branch: {GITHUB_BRANCH}
  auth_type: pkce
  app_id: {GITHUB_APP_ID}

publish_mode: editorial_workflow

media_folder: "{MEDIA_FOLDER}"
public_folder: "{PUBLIC_FOLDER}"

site_url: "{SITE_URL}"
display_url: "{SITE_URL}"

collections:
"""


# -----------------------------
# GENERIC BLOCK BUILDERS
# -----------------------------
def announcement_block(year: int, quick=False) -> str:
    name = f'quick_announcement_{year}' if quick else f'announcements_{year}'
    label_prefix = "Quick add: " if quick else ""
    return f"""  - name: "{name}"
    label: "{label_prefix}Announcement ({year})"
    folder: "_posts/announcements-{year}"
    create: true
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "post" }}
      - {{ label: "Category", name: "categories", widget: "hidden", default: "news" }}
      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Date", name: "date", widget: "datetime", format: "YYYY-MM-DD", time_format: false }}
      - {{ label: "Author", name: "author", widget: "string", required: false }}
      - {{ label: "Thumbnail", name: "thumbnail", widget: "image", required: false }}
      - {{ label: "Header", name: "header", widget: "image", required: false }}
      - {{ label: "Body", name: "body", widget: "markdown" }}

"""


def concert_block(year: int, quick=False) -> str:
    name = f'quick_concert_{year}' if quick else f'concerts_{year}'
    label_prefix = "Quick add: " if quick else ""
    return f"""  - name: "{name}"
    label: "{label_prefix}Concert / Performance ({year})"
    folder: "_posts/concerts-{year}"
    create: true
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "concert" }}
      - {{ label: "Category", name: "categories", widget: "hidden", default: "performance" }}
      - {{ label: "Describe", name: "describe", widget: "text" }}
      - {{ label: "Date", name: "date", widget: "datetime", format: "YYYY-MM-DD", time_format: false }}
      - {{ label: "Time", name: "time", widget: "string", required: false }}

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
          - {{ label: "Year", name: "year", widget: "number", required: false }}

      - {{ label: "Header image", name: "headerImage", widget: "image", required: false }}
      - {{ label: "Thumbnail", name: "thumbnail", widget: "image", required: false }}
      - {{ label: "Header (optional)", name: "header", widget: "image", required: false }}
      - {{ label: "500px image", name: "500pxImage", widget: "image", required: false }}
      - {{ label: "Photos folder", name: "photosFolder", widget: "string", required: false }}

      - label: "Tags"
        name: "tags"
        widget: "list"
        required: false
        field: {{ label: "Tag", name: "tag", widget: "string" }}

      - {{ label: "Body", name: "body", widget: "markdown", required: false }}

"""


def repertoire_block(year: int, quick=False) -> str:
    name = f'quick_repertoire_{year}' if quick else f'repertoire_{year}'
    label_prefix = "Quick add: " if quick else ""
    return f"""  - name: "{name}"
    label: "{label_prefix}Repertoire / Work ({year})"
    folder: "_repertoire/{year}"
    create: true
    slug: "{{{{slug}}}}"
    fields:
      - label: "Composer"
        name: "composer"
        widget: "object"
        fields:
          - {{ label: "First", name: "first", widget: "string", required: false }}
          - {{ label: "Last", name: "last", widget: "string", required: false }}

      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Movements", name: "movements", widget: "string", required: false }}
      - {{ label: "Duration", name: "duration", widget: "string", required: false }}
      - {{ label: "Year composed", name: "yearComposed", widget: "number", default: {year} }}
      - {{ label: "Performed by Switch", name: "performedBySwitch", widget: "string", required: false }}
      - {{ label: "Commissioned / Written for", name: "commissionedOrWrittenFor", widget: "string", required: false }}
      - {{ label: "Size", name: "size", widget: "string", required: false }}

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
          - {{ label: "Type", name: "type", widget: "string", required: false }}
          - {{ label: "URL", name: "url", widget: "string", required: false }}

      - {{ label: "Body", name: "body", widget: "markdown", required: false }}

"""


# -----------------------------
# MAIN
# -----------------------------
def main():
    ADMIN_DIR.mkdir(exist_ok=True)

    content = [header_yaml()]

    # Quick add current year
    content.append(announcement_block(CURRENT_YEAR, quick=True))
    content.append(concert_block(CURRENT_YEAR, quick=True))
    content.append(repertoire_block(CURRENT_YEAR, quick=True))

    # Curated range
    for y in range(END_YEAR, START_YEAR - 1, -1):
        content.append(announcement_block(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        content.append(concert_block(y))
    for y in range(END_YEAR, START_YEAR - 1, -1):
        content.append(repertoire_block(y))

    (ADMIN_DIR / "config.yml").write_text("".join(content), encoding="utf-8")
    print("✔ Wrote admin/config.yml using GitHub PKCE backend.")


if __name__ == "__main__":
    main()