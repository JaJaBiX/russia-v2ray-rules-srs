#!/usr/bin/env python3
"""Generate an HTML and JSON index for published rule files."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
from urllib.parse import quote


def human_size(size: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def file_entry(root: Path, path: Path) -> dict[str, object]:
    relative_path = path.relative_to(root).as_posix()
    size = path.stat().st_size
    return {
        "path": relative_path,
        "size": size,
        "display_size": human_size(size),
    }


def collect_files(root: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    dat_files = [file_entry(root, path) for path in sorted(root.glob("*.dat"))]
    srs_files = [file_entry(root, path) for path in sorted(root.rglob("*.srs"))]

    if not dat_files:
        raise SystemExit(f"no .dat files found in {root}")
    if not srs_files:
        raise SystemExit(f"no .srs files found in {root}")

    return dat_files, srs_files


def render_file_list(title: str, entries: list[dict[str, object]]) -> str:
    rows = []
    for entry in entries:
        path = str(entry["path"])
        href = quote(path, safe="/")
        escaped_path = html.escape(path)
        escaped_size = html.escape(str(entry["display_size"]))
        rows.append(
            f'<li data-path="{escaped_path}">'
            f'<a href="{href}">{escaped_path}</a>'
            f"<span>{escaped_size}</span>"
            "</li>"
        )
    return "\n".join(
        [
            "<section>",
            f"<h2>{html.escape(title)} <small>{len(entries)}</small></h2>",
            '<ul class="file-list">',
            *rows,
            "</ul>",
            "</section>",
        ]
    )


def render_html(generated_at: str, dat_files: list[dict[str, object]], srs_files: list[dict[str, object]]) -> str:
    dat_section = render_file_list("DAT files", dat_files)
    srs_section = render_file_list("SRS files", srs_files)
    total_count = len(dat_files) + len(srs_files)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>russia-v2ray-rules-srs</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f7f7f4;
      --fg: #171717;
      --muted: #666b72;
      --border: #d8d8d0;
      --link: #0957d0;
      --panel: #ffffff;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #111214;
        --fg: #f1f1f1;
        --muted: #a5abb3;
        --border: #33363b;
        --link: #8bb8ff;
        --panel: #181a1d;
      }}
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font: 16px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    small, p {{
      color: var(--muted);
    }}
    input {{
      box-sizing: border-box;
      width: 100%;
      margin: 12px 0 8px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: var(--panel);
      color: var(--fg);
      font: inherit;
    }}
    .file-list {{
      margin: 0;
      padding: 0;
      list-style: none;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      background: var(--panel);
    }}
    .file-list li {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      padding: 9px 12px;
      border-top: 1px solid var(--border);
    }}
    .file-list li:first-child {{
      border-top: 0;
    }}
    a {{
      color: var(--link);
      overflow-wrap: anywhere;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .file-list span {{
      color: var(--muted);
      white-space: nowrap;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>russia-v2ray-rules-srs</h1>
      <p>{total_count} published DAT and SRS files. Generated at {html.escape(generated_at)}.</p>
      <input id="filter" type="search" placeholder="Filter files" autocomplete="off">
    </header>
    {dat_section}
    {srs_section}
  </main>
  <script>
    const filter = document.getElementById("filter");
    const rows = Array.from(document.querySelectorAll("[data-path]"));
    filter.addEventListener("input", () => {{
      const query = filter.value.trim().toLowerCase();
      for (const row of rows) {{
        row.hidden = query.length > 0 && !row.dataset.path.toLowerCase().includes(query);
      }}
    }});
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    dat_files, srs_files = collect_files(root)
    manifest = {
        "generated_at": generated_at,
        "dat": dat_files,
        "srs": srs_files,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_html(generated_at, dat_files, srs_files), encoding="utf-8")
    args.json_output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
