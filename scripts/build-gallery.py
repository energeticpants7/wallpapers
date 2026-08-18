#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
from shutil import copytree, rmtree
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "images"
DIST = ROOT / "dist"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".mov"}


def url_for(path: Path) -> str:
    relative = path.relative_to(DIST).as_posix()
    return quote(relative, safe="/")


def card(path: Path) -> str:
    relative = path.relative_to(DIST / "images")
    title = relative.stem.replace("_", " ").replace("-", " ").strip()
    title = " ".join(title.split()).title()
    kind = "video" if path.suffix.lower() in VIDEO_EXTENSIONS else "image"
    source = url_for(path)
    safe_title = escape(title)

    if kind == "video":
        preview = (
            f'<video src="{source}" muted loop playsinline preload="metadata" '
            f'aria-label="{safe_title}"></video>'
        )
    else:
        preview = (
            f'<img src="{source}" loading="lazy" decoding="async" '
            f'alt="{safe_title}">'
        )

    return f"""\
<article class="card" data-name="{escape(title.lower())}" data-kind="{kind}">
  <button class="card-button" type="button" aria-label="Open {safe_title}" data-src="{source}" data-title="{safe_title}" data-kind="{kind}">
    <span class="media">{preview}</span>
    <span class="caption">{safe_title}</span>
  </button>
</article>
"""


def main() -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Missing wallpaper directory: {SOURCE}")

    if DIST.exists():
        rmtree(DIST)
    DIST.mkdir(parents=True)
    copytree(SOURCE, DIST / "images")
    (DIST / ".nojekyll").touch()

    files = sorted(
        path for path in (DIST / "images").rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
    )
    cards = "\n".join(card(path) for path in files)
    count = len(files)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0d0d12">
  <title>Wallpapers · {count} items</title>
  <style>
    :root {{ color-scheme: dark; --bg:#0d0d12; --panel:#15151d; --text:#f4f1f7; --muted:#aaa5b4; --accent:#c8b5ff; --line:#2b2935; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; min-height:100vh; background:radial-gradient(circle at 20% 0%,#25203a 0,transparent 38rem),var(--bg); color:var(--text); font:15px/1.45 system-ui,sans-serif; }}
    header {{ max-width:1500px; margin:auto; padding:34px 24px 22px; display:flex; align-items:end; justify-content:space-between; gap:20px; flex-wrap:wrap; }}
    h1 {{ margin:0; font-size:clamp(1.8rem,4vw,3.4rem); letter-spacing:-.05em; }}
    .subtitle {{ color:var(--muted); margin:.35rem 0 0; }}
    .tools {{ max-width:1500px; margin:auto; padding:0 24px 24px; display:flex; gap:10px; flex-wrap:wrap; position:sticky; top:0; z-index:2; background:linear-gradient(var(--bg) 72%,transparent); }}
    input, .filter {{ border:1px solid var(--line); background:var(--panel); color:var(--text); border-radius:999px; padding:10px 15px; font:inherit; }}
    input {{ min-width:min(100%,320px); flex:1; outline:none; }}
    input:focus {{ border-color:var(--accent); box-shadow:0 0 0 3px #c8b5ff22; }}
    .filter {{ cursor:pointer; }}
    .filter.active {{ background:var(--accent); color:#211c2d; border-color:var(--accent); }}
    main {{ max-width:1500px; margin:auto; padding:0 24px 50px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:14px; }}
    .card {{ min-width:0; }}
    .card-button {{ display:block; width:100%; padding:0; border:0; color:inherit; text-align:left; background:var(--panel); border-radius:16px; overflow:hidden; cursor:pointer; transition:transform .2s,box-shadow .2s; }}
    .card-button:hover {{ transform:translateY(-3px); box-shadow:0 12px 30px #0007; }}
    .media {{ display:block; aspect-ratio:16/10; background:#09090d; overflow:hidden; }}
    .media img, .media video {{ width:100%; height:100%; display:block; object-fit:cover; transition:transform .35s; }}
    .card-button:hover .media img, .card-button:hover .media video {{ transform:scale(1.04); }}
    .caption {{ display:block; overflow:hidden; padding:11px 12px 13px; color:var(--muted); text-overflow:ellipsis; white-space:nowrap; }}
    .empty {{ color:var(--muted); text-align:center; padding:60px 10px; display:none; }}
    dialog {{ width:min(94vw,1200px); max-height:92vh; padding:0; border:1px solid var(--line); border-radius:18px; background:#101017; color:var(--text); box-shadow:0 24px 100px #000b; }}
    dialog::backdrop {{ background:#000b; backdrop-filter:blur(8px); }}
    .lightbox {{ position:relative; padding:18px; }}
    .lightbox img, .lightbox video {{ width:100%; max-height:78vh; object-fit:contain; display:block; border-radius:10px; background:#08080b; }}
    .lightbox h2 {{ font-size:1rem; margin:12px 0 0; color:var(--muted); }}
    .close {{ position:absolute; top:12px; right:12px; border:0; border-radius:50%; width:36px; height:36px; cursor:pointer; background:#000a; color:white; font-size:1.3rem; }}
    @media (max-width:600px) {{ header, .tools, main {{ padding-left:14px; padding-right:14px; }} .grid {{ grid-template-columns:repeat(auto-fill,minmax(145px,1fr)); gap:9px; }} }}
  </style>
</head>
<body>
  <header>
    <div><h1>Wallpapers</h1><p class="subtitle">{count} wallpapers · private collection</p></div>
  </header>
  <section class="tools" aria-label="Gallery filters">
    <input id="search" type="search" placeholder="Search wallpapers…" aria-label="Search wallpapers">
    <button class="filter active" data-filter="all">All</button>
    <button class="filter" data-filter="image">Images</button>
    <button class="filter" data-filter="video">Videos</button>
  </section>
  <main>
    <section id="grid" class="grid">{cards}</section>
    <p id="empty" class="empty">No wallpapers match your search.</p>
  </main>
  <dialog id="viewer"><div class="lightbox"><button class="close" type="button" aria-label="Close">×</button><div id="preview"></div><h2 id="viewer-title"></h2></div></dialog>
  <script>
    const cards = [...document.querySelectorAll('.card')];
    const search = document.querySelector('#search');
    const empty = document.querySelector('#empty');
    let filter = 'all';
    function render() {{
      const query = search.value.toLowerCase().trim();
      let visible = 0;
      cards.forEach(card => {{
        const show = (filter === 'all' || card.dataset.kind === filter) && card.dataset.name.includes(query);
        card.hidden = !show;
        if (show) visible++;
      }});
      empty.style.display = visible ? 'none' : 'block';
    }}
    search.addEventListener('input', render);
    document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {{
      filter = button.dataset.filter;
      document.querySelectorAll('.filter').forEach(item => item.classList.toggle('active', item === button));
      render();
    }}));
    const viewer = document.querySelector('#viewer');
    const preview = document.querySelector('#preview');
    const viewerTitle = document.querySelector('#viewer-title');
    document.querySelectorAll('.card-button').forEach(button => button.addEventListener('click', () => {{
      const tag = button.dataset.kind === 'video' ? 'video' : 'img';
      preview.innerHTML = `<${{tag}} src="${{button.dataset.src}}" ${{tag === 'video' ? 'controls autoplay loop' : ''}}></${{tag}}>`;
      viewerTitle.textContent = button.dataset.title;
      viewer.showModal();
    }}));
    document.querySelector('.close').addEventListener('click', () => viewer.close());
    viewer.addEventListener('click', event => {{ if (event.target === viewer) viewer.close(); }});
    render();
  </script>
</body>
</html>
"""
    (DIST / "index.html").write_text(html, encoding="utf-8")
    print(f"Generated {count} wallpapers in {DIST}")


if __name__ == "__main__":
    main()
