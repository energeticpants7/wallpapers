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
<article class="item" data-name="{escape(title.lower())}" data-kind="{kind}">
  <button class="card-button" type="button" aria-label="Open {safe_title}" data-src="{source}" data-title="{safe_title}" data-kind="{kind}">
    <span class="media">{preview}</span>
  </button>
  <a class="dl-btn" href="{source}" download title="Download original" aria-label="Download original">↓</a>
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
  <meta name="theme-color" content="#15130f">
  <title>Wallpapers · {count} images</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&family=Shippori+Mincho:wght@500;600&display=swap');
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    :root {{ --bg:#15130f; --surface:#1b1812; --border:#35302a; --accent:#a8492e; --text:#e6e0d2; --muted:#8c8272; }}
    html {{ scroll-behavior:smooth; }}
    body {{ background:var(--bg); color:var(--text); font-family:'JetBrains Mono',monospace; min-height:100vh; }}
    header {{ padding:3.5rem 2.5rem 2.5rem; border-bottom:1px solid var(--border); display:flex; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:1rem; }}
    header h1 {{ font-family:'Shippori Mincho',serif; font-weight:500; font-size:clamp(1.7rem,3.5vw,2.5rem); letter-spacing:.04em; line-height:1; }}
    header h1 span {{ color:var(--accent); }}
    .meta {{ font-size:.7rem; color:var(--muted); line-height:1.8; text-align:right; letter-spacing:.02em; }}
    .controls {{ padding:1rem 2.5rem; display:flex; align-items:center; gap:1.5rem; border-bottom:1px solid var(--border); flex-wrap:wrap; }}
    #count {{ font-size:.65rem; color:var(--muted); margin-left:auto; letter-spacing:.03em; }}
    .filter {{ font-family:'JetBrains Mono',monospace; font-size:.65rem; padding:.2rem 0 .4rem; border:0; border-bottom:1px solid transparent; background:none; color:var(--muted); cursor:pointer; letter-spacing:.1em; text-transform:uppercase; transition:color .15s,border-color .15s; }}
    .filter:hover {{ color:var(--text); }}
    .filter.active {{ border-color:var(--accent); color:var(--text); }}
    main {{ padding:1.5rem; }}
    .grid {{ columns:4 280px; column-gap:.6rem; }}
    .item {{ break-inside:avoid; margin-bottom:.6rem; position:relative; overflow:hidden; cursor:pointer; background:var(--surface); }}
    .card-button {{ display:block; width:100%; padding:0; border:0; color:inherit; background:none; cursor:pointer; }}
    .card-button:focus-visible {{ outline:1px solid var(--accent); outline-offset:3px; }}
    .media {{ display:block; overflow:hidden; }}
    .media img, .media video {{ width:100%; height:auto; min-height:120px; display:block; object-fit:cover; filter:brightness(.94); transition:filter .3s ease; }}
    .item:hover .media img, .item:hover .media video {{ filter:brightness(1); }}
    .dl-btn {{ position:absolute; right:.5rem; bottom:.5rem; display:flex; align-items:center; justify-content:center; width:1.6rem; height:1.6rem; background:#15130fc2; color:var(--text); font-size:.75rem; text-decoration:none; opacity:0; transform:translateY(4px); transition:opacity .2s ease,transform .2s ease,color .15s ease; }}
    .item:hover .dl-btn, .dl-btn:focus-visible {{ opacity:1; transform:translateY(0); }}
    .dl-btn:hover {{ color:var(--accent); }}
    .empty {{ color:var(--muted); text-align:center; padding:4rem 1rem; display:none; font-size:.7rem; }}
    .lightbox {{ position:fixed; inset:0; background:#15130ff7; z-index:100; display:none; align-items:center; justify-content:center; flex-direction:column; gap:1rem; padding:2rem; }}
    .lightbox.open {{ display:flex; }}
    .lightbox-content {{ display:flex; flex-direction:column; align-items:center; gap:1rem; max-width:100%; }}
    .lightbox-media img, .lightbox-media video {{ max-width:min(90vw,1400px); max-height:78vh; object-fit:contain; border:1px solid var(--border); display:block; }}
    .lightbox-bar {{ display:flex; align-items:baseline; gap:1rem; font-family:'JetBrains Mono',monospace; font-size:.7rem; max-width:90vw; }}
    .lightbox-index {{ color:var(--muted); }}
    .lightbox-name {{ color:var(--text); max-width:40ch; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
    .lb-dl {{ color:var(--muted); text-decoration:none; transition:color .15s; }}
    .lb-dl:hover {{ color:var(--accent); }}
    .lb-close {{ position:absolute; top:1.75rem; right:1.75rem; background:none; border:0; color:var(--muted); font-family:'JetBrains Mono',monospace; font-size:.7rem; letter-spacing:.05em; cursor:pointer; transition:color .15s; }}
    .lb-close:hover {{ color:var(--accent); }}
    footer {{ padding:2rem 2.5rem; border-top:1px solid var(--border); font-size:.65rem; color:var(--muted); display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem; }}
    @media (max-width:600px) {{ header {{ padding:2rem 1.25rem 1.5rem; }} main {{ padding:.75rem; }} .grid {{ column-gap:.4rem; }} .item {{ margin-bottom:.4rem; }} .controls {{ padding:.75rem 1.25rem; }} footer {{ padding:1.5rem 1.25rem; }} .lightbox {{ padding:1rem; }} .lightbox-bar {{ gap:.6rem; font-size:.6rem; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Wallpapers<span>·</span>Gallery</h1>
    <div class="meta">{count} images<br>personal collection</div>
  </header>
  <section class="controls" aria-label="Gallery filters">
    <button class="filter active" data-filter="all">All</button>
    <button class="filter" data-filter="image">Images</button>
    <button class="filter" data-filter="video">Videos</button>
    <span id="count">{count} images</span>
  </section>
  <main>
    <section id="grid" class="grid">{cards}</section>
    <p id="empty" class="empty">No wallpapers match this filter.</p>
  </main>
  <div class="lightbox" id="viewer" aria-modal="true" role="dialog">
    <button class="lb-close" type="button" aria-label="Close" id="close">[ esc ]</button>
    <div class="lightbox-content">
      <div id="preview" class="lightbox-media"></div>
      <div class="lightbox-bar"><span class="lightbox-index" id="viewer-index"></span><span class="lightbox-name" id="viewer-title"></span><a id="viewer-download" class="lb-dl" href="" download>↓ original</a></div>
    </div>
  </div>
  <footer><span>{count} wallpapers · personal collection</span><span>↓ original available on each image</span></footer>
  <script>
    const cards = [...document.querySelectorAll('.item')];
    const empty = document.querySelector('#empty');
    const count = document.querySelector('#count');
    let filter = 'all';
    function render() {{
      let visible = 0;
      cards.forEach(card => {{
        const show = filter === 'all' || card.dataset.kind === filter;
        card.hidden = !show;
        if (show) visible++;
      }});
      count.textContent = `${{visible}} images`;
      empty.style.display = visible ? 'none' : 'block';
    }}
    document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {{
      filter = button.dataset.filter;
      document.querySelectorAll('.filter').forEach(item => item.classList.toggle('active', item === button));
      render();
    }}));
    const viewer = document.querySelector('#viewer');
    const preview = document.querySelector('#preview');
    const viewerIndex = document.querySelector('#viewer-index');
    const viewerTitle = document.querySelector('#viewer-title');
    const viewerDownload = document.querySelector('#viewer-download');
    let currentIndex = 0;
    function openViewer(button) {{
      const tag = button.dataset.kind === 'video' ? 'video' : 'img';
      preview.innerHTML = `<${{tag}} src="${{button.dataset.src}}" alt="${{button.dataset.title}}" ${{tag === 'video' ? 'controls autoplay loop' : ''}}></${{tag}}>`;
      const visibleCards = cards.filter(card => !card.hidden);
      currentIndex = visibleCards.indexOf(button.closest('.item'));
      viewerIndex.textContent = `No.${{String(currentIndex + 1).padStart(3, '0')}}`;
      viewerTitle.textContent = button.dataset.title;
      viewerDownload.href = button.dataset.src;
      viewer.classList.add('open');
      document.body.style.overflow = 'hidden';
    }}
    document.querySelectorAll('.card-button').forEach(button => button.addEventListener('click', () => openViewer(button)));
    document.querySelector('#close').addEventListener('click', closeViewer);
    viewer.addEventListener('click', event => {{ if (event.target === viewer) closeViewer(); }});
    document.addEventListener('keydown', event => {{ if (event.key === 'Escape') closeViewer(); }});
    function closeViewer() {{
      viewer.classList.remove('open');
      document.body.style.overflow = '';
      preview.innerHTML = '';
    }}
    render();
  </script>
</body>
</html>
"""
    (DIST / "index.html").write_text(html, encoding="utf-8")
    print(f"Generated {count} wallpapers in {DIST}")


if __name__ == "__main__":
    main()
