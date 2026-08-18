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
    :root {{ color-scheme:dark; --bg:#08090d; --panel:#12141b; --text:#f8f7fb; --muted:#a8aab8; --accent:#cbb8ff; --line:#ffffff1c; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; min-height:100vh; background:radial-gradient(ellipse 70% 45% at 50% -10%,#4a386e 0,transparent 68%),radial-gradient(circle at 100% 35%,#172f42 0,transparent 32rem),var(--bg); color:var(--text); font:15px/1.45 system-ui,-apple-system,BlinkMacSystemFont,sans-serif; }}
    header {{ max-width:1800px; margin:auto; padding:clamp(42px,7vw,100px) 32px 34px; }}
    h1 {{ margin:0; font-size:clamp(2.5rem,7vw,6.5rem); line-height:.95; letter-spacing:-.075em; background:linear-gradient(120deg,#fff 20%,#d7c8ff 60%,#91c9e8); -webkit-background-clip:text; background-clip:text; color:transparent; }}
    .subtitle {{ color:var(--muted); margin:18px 0 0; font-size:clamp(.9rem,1.4vw,1.05rem); letter-spacing:.02em; }}
    .tools {{ max-width:1800px; margin:auto; padding:0 32px 32px; display:flex; gap:10px; flex-wrap:wrap; position:sticky; top:0; z-index:2; background:linear-gradient(#08090df2 55%,transparent); backdrop-filter:blur(12px); }}
    input, .filter {{ border:1px solid var(--line); background:#ffffff0d; color:var(--text); border-radius:999px; padding:12px 17px; font:inherit; backdrop-filter:blur(16px); }}
    input {{ min-width:min(100%,360px); flex:1; outline:none; }}
    input::placeholder {{ color:#a8aab899; }}
    input:focus {{ border-color:var(--accent); box-shadow:0 0 0 4px #cbb8ff1c; }}
    .filter {{ cursor:pointer; transition:background .2s,border-color .2s,transform .2s; }}
    .filter:hover {{ transform:translateY(-1px); border-color:#ffffff40; }}
    .filter.active {{ background:var(--accent); color:#211c2d; border-color:var(--accent); }}
    main {{ max-width:1800px; margin:auto; padding:0 32px 72px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); gap:18px; }}
    .card {{ min-width:0; }}
    .card-button {{ display:block; width:100%; padding:0; border:1px solid var(--line); color:inherit; text-align:left; background:var(--panel); border-radius:22px; overflow:hidden; cursor:pointer; box-shadow:0 10px 30px #0003; transition:transform .3s,box-shadow .3s,border-color .3s; }}
    .card-button:hover {{ transform:translateY(-6px); border-color:#ffffff45; box-shadow:0 22px 45px #0008,0 0 28px #bda7ff18; }}
    .media {{ display:block; aspect-ratio:16/10; background:#090a0f; overflow:hidden; }}
    .media img, .media video {{ width:100%; height:100%; display:block; object-fit:cover; transition:transform .6s cubic-bezier(.2,.7,.2,1),filter .3s; }}
    .card-button:hover .media img, .card-button:hover .media video {{ transform:scale(1.06); filter:saturate(1.08) brightness(1.06); }}
    .empty {{ color:var(--muted); text-align:center; padding:80px 10px; display:none; }}
    dialog {{ width:min(94vw,1400px); max-height:92vh; padding:0; border:1px solid #ffffff30; border-radius:24px; background:#101219; color:var(--text); box-shadow:0 30px 120px #000d; }}
    dialog::backdrop {{ background:#000c; backdrop-filter:blur(14px); }}
    .lightbox {{ position:relative; padding:20px; }}
    .lightbox img, .lightbox video {{ width:100%; max-height:78vh; object-fit:contain; display:block; border-radius:14px; background:#08090d; }}
    .close {{ position:absolute; top:14px; right:14px; z-index:1; border:1px solid #ffffff30; border-radius:50%; width:40px; height:40px; cursor:pointer; background:#08090dcc; color:white; font-size:1.4rem; line-height:1; }}
    .close:hover {{ background:#ffffff25; }}
    @media (max-width:700px) {{ header, .tools, main {{ padding-left:16px; padding-right:16px; }} .grid {{ grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:11px; }} .card-button {{ border-radius:16px; }} }}
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
  <dialog id="viewer"><div class="lightbox"><button class="close" type="button" aria-label="Close">×</button><div id="preview"></div></div></dialog>
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
    document.querySelectorAll('.card-button').forEach(button => button.addEventListener('click', () => {{
      const tag = button.dataset.kind === 'video' ? 'video' : 'img';
      preview.innerHTML = `<${{tag}} src="${{button.dataset.src}}" ${{tag === 'video' ? 'controls autoplay loop' : ''}}></${{tag}}>`;
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
