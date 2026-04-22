#!/usr/bin/env python3
"""Converte Markdown simples (deste repositório) em .docx via HTML + LibreOffice."""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path


def inline_md(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code style='font-size:10pt'>\1</code>", s)
    return s


def md_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'/><title>Documento</title></head><body style='font-family:Calibri,Arial,sans-serif;font-size:11pt;'>",
    ]
    i = 0
    in_list = False
    while i < len(lines):
        line = lines[i]
        raw = line

        if line.strip() == "---":
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<hr/>")
            i += 1
            continue

        if line.strip().startswith("|") and line.count("|") >= 2:
            if in_list:
                out.append("</ul>")
                in_list = False
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            if len(table_lines) < 2:
                out.append(f"<p>{inline_md(raw)}</p>")
                continue
            # pular linha |---|---| se existir
            rows: list[list[str]] = []
            for tl in table_lines:
                if re.match(r"^\|\s*[-:\s|]+\s*\|$", tl.strip()):
                    continue
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                rows.append(cells)
            if not rows:
                continue
            out.append("<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;margin:0.4em 0;width:100%;'>")
            header = rows[0]
            out.append("<thead><tr>")
            for c in header:
                out.append(f"<th style='background:#f0f0f0;'>{inline_md(c)}</th>")
            out.append("</tr></thead><tbody>")
            for row in rows[1:]:
                out.append("<tr>")
                for c in row:
                    out.append(f"<td>{inline_md(c)}</td>")
                out.append("</tr>")
            out.append("</tbody></table>")
            continue

        if line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h1>{inline_md(line[2:].strip())}</h1>")
            i += 1
            continue
        if line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{inline_md(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("### "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{inline_md(line[4:].strip())}</h3>")
            i += 1
            continue

        if line.strip().startswith("- ") or line.strip().startswith("* "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = line.strip()[2:].strip()
            out.append(f"<li>{inline_md(item)}</li>")
            i += 1
            continue

        if in_list and line.strip() == "":
            out.append("</ul>")
            in_list = False
            i += 1
            continue

        if line.strip() == "":
            if in_list:
                out.append("</ul>")
                in_list = False
            i += 1
            continue

        if in_list:
            out.append("</ul>")
            in_list = False

        li_match = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
        if li_match:
            out.append(f"<p style='margin:0.2em 0'>{inline_md(line.strip())}</p>")
            i += 1
            continue

        out.append(f"<p style='margin:0.35em 0'>{inline_md(line.strip())}</p>")
        i += 1

    if in_list:
        out.append("</ul>")
    out.append("</body></html>")
    return "\n".join(out)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: md_to_docx.py <arquivo.md>", file=sys.stderr)
        sys.exit(1)
    md_path = Path(sys.argv[1]).resolve()
    out_dir = md_path.parent
    stem = md_path.stem
    html_path = out_dir / f"_{stem}_export.html"
    odt_path = out_dir / f"_{stem}_export.odt"
    docx_path = out_dir / f"{stem}.docx"

    md_to = md_path.read_text(encoding="utf-8")
    html_path.write_text(md_to_html(md_to), encoding="utf-8")

    for cmd, name in (
        (
            ["soffice", "--headless", "--convert-to", "odt", str(html_path), "--outdir", str(out_dir)],
            "HTML→ODT",
        ),
        (
            ["soffice", "--headless", "--convert-to", "docx", str(odt_path), "--outdir", str(out_dir)],
            "ODT→DOCX",
        ),
    ):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"Falha {name}: {r.stderr or r.stdout}", file=sys.stderr)
            sys.exit(r.returncode)

    # LibreOffice nomeia igual ao ficheiro de entrada
    generated = out_dir / f"_{stem}_export.docx"
    if generated.exists():
        generated.replace(docx_path)
    else:
        print("Ficheiro .docx esperado não encontrado.", file=sys.stderr)
        sys.exit(1)

    html_path.unlink(missing_ok=True)
    odt_path.unlink(missing_ok=True)
    print(str(docx_path))


if __name__ == "__main__":
    main()
