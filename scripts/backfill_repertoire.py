#!/usr/bin/env python3
import re
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from slugify import slugify

REPERTOIRE_ROOT = Path("_repertoire")
CONCERT_ROOT = Path("_posts")
CONCERT_GLOBS = ["concerts-*/*.md"]

YEAR_RE = re.compile(r"(19\d{2}|20\d{2})")
SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"}

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
    return int(m.group(1))

def split_composer_name(composer: str) -> Dict[str, str]:
    c = " ".join(composer.strip().split())
    if not c:
        return {"first": "", "last": ""}

    lc = c.lower()
    if " & " in lc or " and " in lc or ";" in c:
        return {"first": "", "last": c}

    if "," in c:
        parts = [p.strip() for p in c.split(",", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return {"first": parts[1], "last": parts[0]}

    tokens = c.split()
    if len(tokens) == 1:
        return {"first": "", "last": tokens[0]}

    maybe_suffix = tokens[-1].lower()
    if maybe_suffix in SUFFIXES and len(tokens) >= 3:
        return {"first": " ".join(tokens[:-2]), "last": tokens[-2] + " " + tokens[-1]}

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

def build_repertoire_index() -> Tuple[Dict[str, Path], Dict[Tuple[str, str, int], Path]]:
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

        work_id = str(fm.get("workId") or "").strip()
        if work_id:
            by_work_id[work_id] = md

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

def write_repertoire(path: Path, fm: Dict[str, Any], body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    front_matter = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    content = f"---\n{front_matter}\n---\n\n{body}".rstrip() + "\n"
    path.write_text(content, encoding="utf-8")

def main() -> None:
    by_work_id, by_combo = build_repertoire_index()

    created = 0
    updated = 0

    # 1) Backfill from ALL concert posts
    concert_files: List[Path] = []
    for globpat in CONCERT_GLOBS:
        concert_files.extend(CONCERT_ROOT.glob(globpat))

    for concert_path in sorted(concert_files):
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
            year = parse_year_first4(str(year_raw) if year_raw is not None else None)

            if not composer or not title or year is None:
                continue

            wid = stable_work_id(composer, title, int(year))
            combo_key = (normalize(composer), normalize(title), int(year))

            # If repertoire exists but missing workId/sourceConcert, patch it
            existing = by_work_id.get(wid) or by_combo.get(combo_key)
            if existing and existing.exists():
                ex_fm, ex_body = load_front_matter(existing)
                changed = False
                if not ex_fm.get("workId"):
                    ex_fm["workId"] = wid
                    changed = True
                if not ex_fm.get("sourceConcert"):
                    ex_fm["sourceConcert"] = source_concert
                    changed = True
                if ex_fm.get("draft") is None:
                    ex_fm["draft"] = True
                    changed = True
                if changed:
                    write_repertoire(existing, ex_fm, ex_body)
                    by_work_id[wid] = existing
                    by_combo[combo_key] = existing
                    updated += 1
                continue

            # Otherwise create new draft
            folder = REPERTOIRE_ROOT / str(year)
            base_slug = slugify(f"{composer}-{title}", lowercase=True)
            target = ensure_unique_filename(folder, base_slug)

            composer_obj = split_composer_name(composer)
            new_fm: Dict[str, Any] = {
                "draft": True,
                "workId": wid,
                "sourceConcert": source_concert,
                "composer": composer_obj,
                "title": title,
                "yearComposed": int(year),
                "movements": [],
                "duration": "",
                "performedBySwitch": "",
                "commissionedOrWrittenFor": "unknown",
                "size": "",
                "instrumentation": [],
                "tags": [],
                "media": [],
            }
            write_repertoire(target, new_fm, "")
            by_work_id[wid] = target
            by_combo[combo_key] = target
            created += 1

    print(f"Backfill complete. Created: {created}, Updated: {updated}")

if __name__ == "__main__":
    main()