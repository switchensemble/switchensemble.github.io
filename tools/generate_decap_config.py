#!/usr/bin/env python3
"""
Generate Decap CMS admin/config.yml
Configured for:
- GitHub backend
- Cloudflare Worker OAuth proxy (workers.dev)
- switchensemble.github.io repo
"""

from pathlib import Path


# -------------------------
# HARD-CODED CONFIGURATION
# -------------------------

GITHUB_REPO = "switchensemble/switchensemble.github.io"
BRANCH = "master"

# Cloudflare Worker OAuth proxy (Option B)
OAUTH_BASE_URL = "https://decap-oauth.switchensemble.workers.dev"
AUTH_ENDPOINT = "/auth"

# Site origin (must match how you open /admin/)
SITE_ORIGIN = "https://www.switchensemble.com"

MEDIA_FOLDER = "assets/images/auto-add"
PUBLIC_FOLDER = "/assets/images/auto-add"

OUTPUT_PATH = Path("admin/config.yml")


# -------------------------
# YAML GENERATION
# -------------------------

def build_yaml() -> str:
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
  - name: "quick_announcement_2026"
    label: "Quick add: Announcement (2026)"
    label_singular: "Announcement"
    folder: "_posts/announcements-2026"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    summary: "{{{{date}}}} – {{{{title}}}}"
    sortable_fields: ["date", "title"]
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "post" }}
      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Date", name: "date", widget: "datetime" }}
      - {{ label: "Body", name: "body", widget: "markdown" }}

  - name: "quick_concert_2026"
    label: "Quick add: Concert / Performance (2026)"
    label_singular: "Concert"
    folder: "_posts/concerts-2026"
    create: true
    extension: "md"
    format: "frontmatter"
    slug: "{{{{year}}}}-{{{{month}}}}-{{{{day}}}}-{{{{slug}}}}"
    summary: "{{{{date}}}} – {{{{title}}}}"
    sortable_fields: ["date", "title"]
    fields:
      - {{ label: "Layout", name: "layout", widget: "hidden", default: "post" }}
      - {{ label: "Title", name: "title", widget: "string" }}
      - {{ label: "Date", name: "date", widget: "datetime" }}
      - {{ label: "Body", name: "body", widget: "markdown" }}
"""


# -------------------------
# WRITE FILE
# -------------------------

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_yaml(), encoding="utf-8")
    print(f"✅ Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()