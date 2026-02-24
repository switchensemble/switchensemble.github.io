import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POSTS_DIR = REPO / "_posts"
REPERTOIRE_DIR = REPO / "_repertoire"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "assets/images/auto-add"
SITE_URL = "https://switchensemble.com"

START_YEAR = 2021
END_YEAR = 2032

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def find_year_folders(base: Path, prefix: str):
    """
    Returns dict {year:int -> foldername:str} for folders like f"{prefix}-{YYYY}"
    """
    out = {}
    if not base.exists():
        return out
    rx = re.compile(rf"{re.escape(prefix)}-(\d{{4}})$")
    for p in base.iterdir():
        if p.is_dir():
            m = rx.fullmatch(p.name)
            if m:
                out[int(m.group(1))] = p.name
    return out

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
    return f"""  - name: "concerts_{year}"
    label: "Concerts / Performances ({year})"
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

def repertoire_block(year: int) -> str:
    return f"""  - name: "repertoire_{year}"
    label: "Repertoire / Works ({year})"
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
        options:
          - "commissioned"
          - "written for"
          - "arrangement"
          - "existing"
          - "unknown"

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
            options:
              - "audio"
              - "video"
              - "score"
              - "website"
              - "other"
          - {{ label: "URL", name: "url", widget: "string", required: false }}

      - { label: "Body", name: "body", widget: "markdown", required: false }

"""

def main():
    ensure_dir(POSTS_DIR)
    ensure_dir(REPERTOIRE_DIR)

    # Ensure the curated folders exist so Decap can create new entries in future years.
    for y in range(START_YEAR, END_YEAR + 1):
        ensure_dir(POSTS_DIR / f"announcements-{y}")
        ensure_dir(POSTS_DIR / f"concerts-{y}")
        ensure_dir(REPERTOIRE_DIR / f"{y}")

    header = f"""backend:
  name: git-gateway
  branch: master

publish_mode: editorial_workflow

media_folder: "{MEDIA_FOLDER}"
public_folder: "{PUBLIC_FOLDER}"

site_url: "{SITE_URL}"
display_url: "{SITE_URL}"

collections:
"""
    out = [header]

    # Newest first in sidebar
    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(announcement_block(y))

    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(concert_block(y))

    for y in range(END_YEAR, START_YEAR - 1, -1):
        out.append(repertoire_block(y))

    (REPO / "admin" / "config.yml").write_text("".join(out), encoding="utf-8")
    print("Wrote curated admin/config.yml for 2021–2032 (announcements, concerts, repertoire).")

if __name__ == "__main__":
    main()