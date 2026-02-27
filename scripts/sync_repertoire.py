#!/usr/bin/env python3
import os
import re
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from slugify import slugify

REPERTOIRE_ROOT = Path("_repertoire")
CONCERT_PREFIX = "_posts/concerts-"

YEAR_MIN = 1950
YEAR_MAX = 2100
YEAR_RE = re.compile(r"(19\d{2}|20\d{2})")  # first 4-digit year

SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"}

def run(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def stable_work_id(composer: str, title: str, year: int) -> str:
    key = f"{normalize(composer)}|{normalize(title)}|{int(year)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

def parse_year_first4(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    m = YEAR_RE.search(str(raw))
    if not m:
        return None
    y = int(m.group(1))
    if YEAR_MIN <= y <= YEAR_MAX:
        return y
    return y

def split_composer_name(composer: str) -> Dict[str, str]:
    """
    Better heuristics:
    - If multiple composers (contains '&', ' and ', ';') => store full string in last.
    - If "Last, First" => parse.
    - Otherwise => last token is last name, rest is first; keep suffixes with last.
    """
    c = " ".join(composer.strip().split())
    if not c:
        return {"first": "", "last": ""}

    lc = c.lower()
    if " & " in lc or " and " in lc or ";" in c:
        return {"first": "", "last": c}

    # "Last, First" format
    if "," in c:
        parts = [p.strip() for p in c.split(",", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return {"first": parts[1], "last": parts[0]}

    tokens = c.split()
    if len(tokens) == 1:
        return {"first": "", "last": tokens[0]}

    # Handle suffixes like "John Doe Jr."
    last = tokens[-1]
    maybe_suffix = tokens[-1].lower()
    if maybe_suffix in SUFFIXES and len(tokens) >= 3:
        last = tokens[-2] + " " + tokens[-1]
        first = " ".join(tokens[:-2])
        return {"first": first, "last": last}

    return {"first": " ".join(tokens[:-1]), "last": tokens[-1]}

def load_front_matter(path: Path) -> Tuple[Dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_raw = parts[1].strip()
    body = parts[2].lstrip("\n")
    data = yaml.safe_load(fm_raw) or {}
    return data, body

def get_changed_concert_files() -> List[Path]:
    base_ref = os.environ.get("BASE_REF", "master")
    run(["git", "fetch", "origin", base_ref])
    merge_base = run(["git", "merge-base", "HEAD", f"origin/{base_ref}"])
    diff = run(["git", "diff", "--name-only", f"{merge_base}...HEAD"])

    files: List[Path] = []
    for line in diff.splitlines():
        if not line.endswith(".md"):
            continue
        if line.startswith(CONCERT_PREFIX):
            files.append(Path(line))
    return files

def build_repertoire_index() -> Tuple[Dict[str, Path], Dict[Tuple[str, str, int], Path]]:
    """
    Returns:
      - by_work_id: workId -> path
      - by_combo: (composer_norm, title_norm, year) -> path
    """
    by_work_id: Dict[str, Path] = {}
    by_combo: Dict[Tuple[str, str, int], Path] = {}

    if not REPERTOIRE_ROOT.exists():
        return by_work_id, by_combo

    for md in REPERTOIRE_ROOT.rglob("*.md"):
        fm, _ = load_front_matter(md)

        title = str(fm.get("title") or "").strip()
        year = fm.get("yearComposed")

        composer = fm.get("composer") or {}
        if isinstance(composer, dict):
            composer_full = " ".join(filter(None, [composer.get("first", ""), composer.get("last", "")])).strip()
        else:
            composer_full = str(composer).strip()

        # Index by workId if present
        work_id = str(fm.get("workId") or "").strip()
        if work_id:
            by_work_id[work_id] = md

        # Index by combo
        try:
            y_int = int(year)
        except Exception:
            continue
        if title and composer_full:
            by_combo[(normalize(composer_full), normalize(title), y_int)] = md

    return by_work_id, by_combo

def ensure_unique_filename(folder: Path, base_slug: str) -> Path:
    candidate = folder / f"{base_slug}.md"
    if not candidate.exists():
        return candidate
    i = 2
    while True:
        candidate = folder / f"{base_slug}-{i}.md"
        if not candidate.exists():
            return candidate
        i += 1

def write_repertoire_draft(
    path: Path,
    work_id: str,
    composer_str: str,
    title: str,
    year_composed: int,
    source_concert: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    composer_obj = split_composer_name(composer_str)

    fm: Dict[str, Any] = {
        "draft": True,
        "workId": work_id,
        "sourceConcert": source_concert,
        "composer": composer_obj,
        "title": title,
        "yearComposed": int(year_composed),

        # Editor-fill fields:
        "movements": [],
        "duration": "",
        "performedBySwitch": "",
        "commissionedOrWrittenFor": "unknown",
        "size": "",
        "instrumentation": [],
        "tags": [],
        "media": [],
    }

    front_matter = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    content = f"---\n{front_matter}\n---\n\n"  # empty body => program notes live in body
    path.write_text(content, encoding="utf-8")

def main() -> None:
    changed = get_changed_concert_files()
    if not changed:
        print("No changed concert files.")
        return

    by_work_id, by_combo = build_repertoire_index()

    created = 0
    for concert_path in changed:
        if not concert_path.exists():
            continue

        fm, _ = load_front_matter(concert_path)
        program = fm.get("program") or []
        if not isinstance(program, list):
            continue

        source_concert = concert_path.stem

        for item in program:
            if not isinstance(item, dict):
                continue

            composer = str(item.get("composer") or "").strip()
            title = str(item.get("title") or "").strip()
            year_raw = item.get("year")

            if not composer or not title:
                continue

            year = parse_year_first4(str(year_raw) if year_raw is not None else None)
            if year is None:
                continue

            wid = stable_work_id(composer, title, int(year))
            combo_key = (normalize(composer), normalize(title), int(year))

            # Check existence
            if wid in by_work_id or combo_key in by_combo:
                continue

            folder = REPERTOIRE_ROOT / str(year)
            base_slug = slugify(f"{composer}-{title}", lowercase=True)
            target = ensure_unique_filename(folder, base_slug)

            write_repertoire_draft(target, wid, composer, title, int(year), source_concert)

            by_work_id[wid] = target
            by_combo[combo_key] = target
            created += 1
            print(f"Created repertoire draft: {target} (workId={wid})")

    print(f"Done. Created {created} new repertoire draft(s).")

if __name__ == "__main__":
    main()