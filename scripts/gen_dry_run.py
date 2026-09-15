#!/usr/bin/env python3
"""Shared dry-run reporting for HTML generators."""

from pathlib import Path


class DryRunReport:
    """Classify generated text without writing it to disk."""

    _CATEGORIES = ("would-create", "would-change", "unchanged")

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.paths = {category: [] for category in self._CATEGORIES}

    def record(self, path, content, encoding="utf-8"):
        output_path = Path(path)
        if not output_path.exists():
            category = "would-create"
        elif output_path.read_bytes() != content.encode(encoding):
            category = "would-change"
        else:
            category = "unchanged"
        self.paths[category].append(self._display_path(output_path))
        return category

    def print_summary(self):
        print("\n=== Dry-run summary ===")
        for category in self._CATEGORIES:
            print(f"{category}: {len(self.paths[category])}")
        for category in self._CATEGORIES[:2]:
            print(f"{category} paths:")
            paths = sorted(self.paths[category])
            if paths:
                for path in paths:
                    print(f"  {path}")
            else:
                print("  (none)")

    def _display_path(self, path):
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return path.resolve().as_posix()
