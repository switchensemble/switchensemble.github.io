import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POSTS_DIR = REPO / "_posts"
REPERTOIRE_DIR = REPO / "_repertoire"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "assets/images/auto-add"
SITE_URL = "https://switchensemble.com"

REPERTOIRE_START = 2021
REPERTOIRE_END = 2032

def find_year_folders(base: Path, pattern: str):
    rx = re.compile(pattern)
    items = []
    if not base.exists():
        return items
    for p in base.iterdir():
        if p.is_dir():
            m = rx.fullmatch(p.name)
            if m:
                items.append((int(m.group(1)), p.name))
    return sorted(items, key=lambda x: x[0], reverse=True)

def announcement_block(folder: str, year: int) -> str:
    return f"""  - name: "announcements_{year}"
    label: "News / Announcements ({year})"
    label_singular: "Announcement"
    folder: "_posts/{folder}"
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

def concert_block(folder: str, year: int) -> str:
    return f"""  - name: "concerts_{year}"
    label: "Concerts / Performances ({year})"
    label_singular: "Concert / Performance"
    folder: "_posts/{folder}"
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
    # Folder must exist or Decap will show it but errors when creating.
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

      - {{ label: "Body", name: "body", widget: "markdown", required: false }}

"""

def main():
    announcements = find_year_folders(POSTS_DIR, r"announcements-(\d{4})")
    concerts = find_year_folders(POSTS_DIR, r"concerts-(\d{4})")

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

    for y, folder in announcements:
        out.append(announcement_block(folder, y))

    for y, folder in concerts:
        out.append(concert_block(folder, y))

    # curated repertoire years only
    for year in range(REPERTOIRE_END, REPERTOIRE_START - 1, -1):
        if (REPERTOIRE_DIR / str(year)).exists():
            out.append(repertoire_block(year))

    (REPO / "admin" / "config.yml").write_text("".join(out), encoding="utf-8")
    print("Wrote admin/config.yml")

if __name__ == "__main__":
    main()