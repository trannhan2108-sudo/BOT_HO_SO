
import hashlib, os, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
mapping_active = ROOT/"mapping/placeholder_mapping_ACTIVE.xlsx"
templates_active = ROOT/"code/HO_SO_BOT/templates/_ACTIVE"
out = ROOT/"MANIFEST.md"

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def fmt_line(p: Path):
    ts = dt.datetime.fromtimestamp(p.stat().st_mtime)
    return f"- `{p.relative_to(ROOT)}` | {p.stat().st_size} bytes | {ts:%Y-%m-%d %H:%M:%S} | {sha256(p)}"

lines = []
lines.append(f"# MANIFEST – BOT_HO_SO\nGenerated: {dt.datetime.now():%Y-%m-%d %H:%M:%S}\n")

lines.append("## Active mapping")
if mapping_active.exists():
    lines.append(fmt_line(mapping_active))
else:
    lines.append("- (NOT FOUND) mapping/placeholder_mapping_ACTIVE.xlsx")

lines.append("\n## Active templates (_ACTIVE)")
if templates_active.exists():
    for p in sorted(templates_active.glob("*")):
        if p.is_file():
            lines.append(fmt_line(p))
else:
    lines.append("- (NOT FOUND) code/HO_SO_BOT/templates/_ACTIVE")

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Wrote {out}")
