#!/usr/bin/env python3
"""
Insert Google Analytics tags into Japanese HTML pages that are missing them.
- Does NOT touch: -backup.html, files with http-equiv="refresh" or content="noindex",
  google739a609ca0f00aca.html, new-design/, en/
- Inserts GA snippet immediately before </head>
- Skips files that already have googletagmanager
- Skips files with no </head>
"""

import glob
import re
import sys

GA_SNIPPET = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-2VRTV8BZEJ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-2VRTV8BZEJ');
</script>'''

# Target file globs
TARGETS = [
    "photographers/*.html",
    "movements/*.html",
    "eras/*.html",
    "cards-archive.html",
    "index-v51.html",
]

def collect_files():
    files = []
    for pattern in TARGETS:
        files.extend(sorted(glob.glob(pattern)))
    return files

def process(files):
    inserted = {}  # dir -> list of filenames
    skipped = []   # (path, reason)

    for path in files:
        # Skip backups
        if path.endswith("-backup.html"):
            skipped.append((path, "backup file"))
            continue

        # Skip google site verification
        if "google739a609ca0f00aca" in path:
            skipped.append((path, "Google site verification"))
            continue

        with open(path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()

        # Skip redirect stubs
        if 'http-equiv="refresh"' in content or 'content="noindex' in content:
            skipped.append((path, "redirect stub / noindex"))
            continue

        # Skip already tagged
        if "googletagmanager" in content:
            skipped.append((path, "already has GA"))
            continue

        # Skip if no </head>
        if "</head>" not in content:
            skipped.append((path, "no </head> found"))
            continue

        # Insert before </head>
        new_content = content.replace("</head>", GA_SNIPPET + "\n</head>", 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_content)

        # Track by directory
        parts = path.split("/")
        dir_key = parts[0] if len(parts) > 1 else "."
        inserted.setdefault(dir_key, []).append(path)

    return inserted, skipped

def main():
    import os
    # Change to project root (script lives in scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    files = collect_files()
    print(f"Total candidate files: {len(files)}")
    inserted, skipped = process(files)

    print("\n=== INSERTED ===")
    total_inserted = 0
    for d, flist in sorted(inserted.items()):
        print(f"  {d}: {len(flist)} files")
        total_inserted += len(flist)
    print(f"  TOTAL: {total_inserted} files")

    print("\n=== SKIPPED ===")
    reason_counts = {}
    for path, reason in skipped:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    for reason, count in sorted(reason_counts.items()):
        print(f"  {reason}: {count} files")
    # Show individual skipped (non-trivial reasons)
    for path, reason in skipped:
        if reason not in ("already has GA",):
            print(f"    [{reason}] {path}")

if __name__ == "__main__":
    main()
