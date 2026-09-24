#!/usr/bin/env python3
"""
grepable.py - Split a large FSD/PRD markdown file into indexed section files.

What it does
- Splits at a heading level (default ##), ignoring headings inside code fences.
- Re-splits oversized sections at the next heading level (--max-lines).
- Line 1 of every shard is a source marker, so any citation traces back:
      <!-- source: docs/original-requirement.md:L343-L446 -->
- Writes INDEX.md (section map) and ID-MAP.md (every ID -> shard file:line).
- An ID is "defined" where it appears in a heading or as the FIRST cell of a
  table row. Everywhere else it is a reference.
- Reports duplicate definitions and IDs referenced but never defined.
- Flags sections containing open markers (default: "Decision pending|TBD|TODO").
- Lossless check: concatenated shard bodies must equal the source byte-for-byte.
- Never modifies the source.

Usage
  python grepable.py SOURCE OUT_DIR [--level 2] [--max-lines 800]
         [--id-pattern REGEX ...] [--flag-pattern REGEX] [--discover]
         [--dry-run] [--force]

  --discover   print candidate ID families found in the source, write nothing.
Standard library only (Python 3.8+).
"""
import argparse
import os
import re
import sys
from collections import Counter, OrderedDict

# IDs must not be part of a longer hyphenated token (so AC-ST-01-1 does not also count as ST-01)
DEFAULT_ID_PATTERNS = [
    r"(?<![\w-])[A-Z]{1,5}-\d{1,4}(?:\.R\d+)?(?![\w-])",   # ST-01, POV-002, ADR-038, ST-05.R1
    r"(?<![\w-])AC-[A-Z]{1,5}-\d{1,4}-\d{1,3}(?![\w-])",   # AC-ST-03-1
]
DEFAULT_FLAGS = r"Decision pending|\bTBD\b|\bTODO\b|NOT IN SPEC"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BOLD_LABEL_RE = re.compile(r"^\*\*([^*]{2,80})\*\*\s*$")          # a line that is only **Label**
TABLE_FIRST_CELL_RE = re.compile(r"^\|\s*([^|]+?)\s*\|")
TABLE_SEP_RE = re.compile(r"^\|\s*:?-{3,}")
SLASH_RANGE_RE = re.compile(r"\b([A-Z]{1,5})-(\d{1,4})((?:\s*/\s*\d{1,4})+)")  # POV-003 / 004


def slugify(text, maxlen=48):
    text = re.sub(r"[`*_\[\]()]", "", text)
    text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)  # drop "9." / "3.2 " numbering
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:maxlen].rstrip("-") or "section"


def classify_lines(lines):
    """Per line: (is_heading_level or 0, title, in_fence)."""
    info, in_fence, tok = [], False, None
    for line in lines:
        m = FENCE_RE.match(line)
        if m:
            if not in_fence:
                in_fence, tok = True, m.group(1)
            elif m.group(1) == tok:
                in_fence, tok = False, None
            info.append((0, None, True))
            continue
        if in_fence:
            info.append((0, None, True))
            continue
        h = HEADING_RE.match(line)
        info.append((len(h.group(1)), h.group(2).strip(), False) if h else (0, None, False))
    return info


def split_range(info, start, end, level, max_lines, max_level=4):
    cuts = [i for i in range(start, end) if info[i][0] == level]
    if not cuts:
        return [(start, end, None)]
    chunks = []
    if cuts[0] > start:
        chunks.append((start, cuts[0], None))
    for n, i in enumerate(cuts):
        chunks.append((i, cuts[n + 1] if n + 1 < len(cuts) else end, info[i][1]))
    out = []
    for s, e, title in chunks:
        if e - s > max_lines and level < max_level:
            sub = split_range(info, s, e, level + 1, max_lines, max_level)
            if len(sub) > 1:
                sub[0] = (sub[0][0], sub[0][1], sub[0][2] or title)
                out.extend(sub)
                continue
        out.append((s, e, title))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--level", type=int, default=2)
    ap.add_argument("--max-lines", type=int, default=800)
    ap.add_argument("--id-pattern", action="append", help="regex for IDs; repeatable. Replaces the default.")
    ap.add_argument("--flag-pattern", default=DEFAULT_FLAGS)
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.source):
        sys.exit(f"ERROR: source not found: {a.source}")
    with open(a.source, encoding="utf-8", newline="") as f:
        raw = f.read()
    lines = raw.splitlines(keepends=True)
    if not lines:
        sys.exit("ERROR: source is empty")
    info = classify_lines(lines)
    id_re = re.compile("|".join(f"(?:{p})" for p in (a.id_pattern or DEFAULT_ID_PATTERNS)))
    flag_re = re.compile(a.flag_pattern) if a.flag_pattern else None

    if a.discover:
        fam = Counter()
        cand = re.compile(r"\b([A-Z]{1,5})-?\d{1,4}\b")
        for i, line in enumerate(lines):
            if info[i][2]:
                continue
            m = TABLE_FIRST_CELL_RE.match(line)
            if m and not TABLE_SEP_RE.match(line):
                tok = m.group(1).split()[0] if m.group(1).split() else ""
                if cand.fullmatch(tok):
                    fam[f"{re.sub(r'[0-9]+', 'NN', tok)} (defined as table first cell)"] += 1
            for c in re.finditer(r"\b([A-Z]{1,5})-\d{1,4}\b", line):
                fam[f"{c.group(1)}-NN (anywhere)"] += 1
        print("Candidate ID families (count):")
        for k, v in fam.most_common(40):
            print(f"  {v:>4}  {k}")
        print("\nPass the families you want as --id-pattern, e.g. --id-pattern '\\b[A-Z]{1,5}-\\d{1,4}\\b' --id-pattern '\\b[DJQ]\\d{1,2}\\b'")
        return

    if not a.out_dir:
        sys.exit("ERROR: OUT_DIR is required unless --discover")
    if not any(x[0] == a.level for x in info):
        lv = sorted({x[0] for x in info if x[0]})
        sys.exit(f"ERROR: no level-{a.level} headings. Levels present: {lv}")

    chunks = split_range(info, 0, len(lines), a.level, a.max_lines)
    src_label = a.source.replace("\\", "/")

    # collect IDs: definitions (heading or table first cell) vs references
    defs, refs, expanded = OrderedDict(), OrderedDict(), {}
    for i, line in enumerate(lines):
        if info[i][2]:
            continue
        def_span = None
        if info[i][0]:
            # only an ID that STARTS the heading text is a definition ("### ST-03 — Title")
            hm = re.match(r"^#+\s+", line)
            first = id_re.search(line, hm.end()) if hm else None
            if first and first.start() == hm.end():
                def_span = first.span()
        else:
            m = TABLE_FIRST_CELL_RE.match(line)
            if m and not TABLE_SEP_RE.match(line):
                def_span = m.span(1)
        for m in id_re.finditer(line):
            rid = m.group(0)
            if def_span and def_span[0] <= m.start() < def_span[1]:
                defs.setdefault(rid, []).append(i)
            else:
                refs.setdefault(rid, []).append(i)
        # expand shorthand ranges in definitions: "POV-003 / 004" -> POV-003, POV-004
        if def_span:
            seg = line[def_span[0]:def_span[1]]
            for m in SLASH_RANGE_RE.finditer(seg):
                prefix, first, rest = m.group(1), m.group(2), m.group(3)
                for num in re.findall(r"\d+", rest):
                    rid = f"{prefix}-{num.zfill(len(first))}"
                    if id_re.fullmatch(rid) and i not in defs.get(rid, []):
                        defs.setdefault(rid, []).append(i)
                        expanded[rid] = f"{prefix}-{first}{rest}".strip()

    shards, used = [], set()
    width = max(2, len(str(len(chunks))))
    for n, (s, e, title) in enumerate(chunks):
        t = title or ("preamble" if n == 0 else "section")
        base = f"{str(n).zfill(width)}-{slugify(t)}"
        fn, k = f"{base}.md", 2
        while fn in used:
            fn, k = f"{base}-{k}.md", k + 1
        used.add(fn)
        heads, bolds = [], []
        for i in range(s + 1, e):
            if info[i][2]:
                continue
            if 0 < info[i][0] <= a.level + 2:
                heads.append(info[i][1])
            else:
                b = BOLD_LABEL_RE.match(lines[i].strip())
                if b:
                    bolds.append(b.group(1).rstrip(".:"))
        # prefer real sub-headings; fall back to bold pseudo-headings; drop repeats
        labels = list(OrderedDict.fromkeys(heads or bolds))
        ids = [r for r, locs in defs.items() if any(s <= li < e for li in locs)]
        flags = sum(len(flag_re.findall(lines[i])) for i in range(s, e)) if flag_re else 0
        shards.append(dict(file=fn, s=s, e=e, title=t, labels=labels, ids=ids, flags=flags))

    def shard_of(li):
        for sh in shards:
            if sh["s"] <= li < sh["e"]:
                return sh
    dups = {r: l for r, l in defs.items() if len(l) > 1}
    undefined = [r for r in refs if r not in defs]
    lossless = "".join("".join(lines[sh["s"]:sh["e"]]) for sh in shards) == raw

    print(f"Source: {src_label} ({len(lines)} lines, {len(raw)//1024} KB)")
    print(f"Shards: {len(shards)} (level {a.level}, max {a.max_lines} lines)")
    for sh in shards:
        print(f"  {sh['file']:<50} L{sh['s']+1}-L{sh['e']:<5} {sh['e']-sh['s']:>4} lines {len(sh['ids']):>3} IDs {sh['flags']:>2} flags")
    print(f"IDs defined: {len(defs)}   referenced-only (never defined): {len(undefined)}   duplicates: {len(dups)}")
    for r, l in dups.items():
        print(f"  DUPLICATE {r}: source lines " + ", ".join(f"L{x+1}" for x in l))
    print(f"Lossless check: {'PASS' if lossless else 'FAIL'}")
    if not lossless:
        sys.exit("ERROR: lossless check failed; nothing written")
    if a.dry_run:
        print("Dry run: nothing written.")
        return

    os.makedirs(a.out_dir, exist_ok=True)
    existing = [f for f in os.listdir(a.out_dir) if f.endswith(".md")]
    if existing and not a.force:
        sys.exit(f"ERROR: {a.out_dir} has {len(existing)} .md files. Re-run with --force to replace them.")
    for f in existing:
        os.remove(os.path.join(a.out_dir, f))

    for sh in shards:
        with open(os.path.join(a.out_dir, sh["file"]), "w", encoding="utf-8", newline="") as f:
            f.write(f"<!-- source: {src_label}:L{sh['s']+1}-L{sh['e']} (generated; do not edit) -->\n")
            f.write("".join(lines[sh["s"]:sh["e"]]))

    def id_summary(ids):
        if not ids:
            return "—"
        fams = OrderedDict()
        for r in ids:
            fams.setdefault(re.sub(r"[-.]?\d.*$", "", r) or r, []).append(r)
        parts = []
        for _, v in fams.items():
            parts.append(v[0] if len(v) == 1 else f"{v[0]}…{v[-1]} ({len(v)})")
        s = ", ".join(parts)
        return s if len(s) <= 120 else s[:117] + "..."

    out = [
        "# Spec Index", "",
        f"> Generated by grepable.py from `{src_label}`. Do not edit; change the source and re-run.",
        "> **Claude: read this first.** Pick the section by topic, look up IDs in `ID-MAP.md`, then read only that shard.",
        "> Shard line N = source line (start + N − 2); line 1 of each shard is the source marker.", "",
        "| File | Covers | IDs defined | Lines | Source | ⚠ |",
        "|---|---|---|---|---|---|",
    ]
    for sh in shards:
        covers = sh["title"] + (": " + "; ".join(sh["labels"][:8]) if sh["labels"] else "")
        covers = covers.replace("|", "/")
        covers = covers if len(covers) <= 180 else covers[:177] + "..."
        out.append(f"| `{sh['file']}` | {covers} | {id_summary(sh['ids'])} | {sh['e']-sh['s']+1} | L{sh['s']+1}–L{sh['e']} | {sh['flags'] or ''} |")
    out += ["", "⚠ = count of open markers (`" + (a.flag_pattern or "") + "`). Items there are **not buildable** until resolved.",
            "", "## Lookups", "- Every ID and where it is defined: `ID-MAP.md`"]
    if dups:
        out += ["", "## Duplicate definitions (fix in source)"] + [f"- {r}" for r in dups]
    with open(os.path.join(a.out_dir, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    mp = ["# ID Map", "", f"> Generated from `{src_label}`. Where each ID is **defined** (heading or first table cell).",
          "> Grep this file for an ID, then read the shard at that line.", "",
          "| ID | Definition (truncated) | Shard file:line | Source line |", "|---|---|---|---|"]
    for rid, locs in defs.items():
        for li in locs:
            sh = shard_of(li)
            text = lines[li].strip()
            if text.startswith("|"):
                cells = [c.strip() for c in text.strip("|").split("|")]
                text = cells[1] if len(cells) > 1 else cells[0]
            else:
                text = re.sub(r"^#+\s*", "", text)
                text = re.sub(re.escape(rid) + r"\s*[:\-–—]?\s*", "", text, count=1)
            text = text.replace("|", "/")
            text = text if len(text) <= 90 else text[:87] + "..."
            if rid in expanded:
                text = f"(written as `{expanded[rid]}`) {text}"
            mp.append(f"| {rid} | {text} | `{sh['file']}:{li - sh['s'] + 2}` | L{li+1} |")
    if undefined:
        mp += ["", "## Referenced but never defined here",
               "> Either defined in another document (e.g. TSD ADRs), a typo, or a gap.", ""]
        mp += [f"- {r}: " + ", ".join(f"L{x+1}" for x in refs[r][:6]) for r in undefined]
    with open(os.path.join(a.out_dir, "ID-MAP.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(mp) + "\n")
    print(f"Wrote {len(shards)} shards + INDEX.md + ID-MAP.md to {a.out_dir}")


if __name__ == "__main__":
    main()
