# Wallpapers

Private collection of wallpapers synchronized from this machine.

- `images/` -> `~/Pictures/Wallpapers`

## Automatic weekly synchronization

The `wallpapers.timer` synchronizes the collection every Sunday at 20:30 and pushes changes to the private GitHub repository.

## Gallery

The `pages.yml` workflow builds and deploys a masonry gallery to GitHub Pages whenever `main` changes. It includes format filters, lazy loading, original downloads, and a fullscreen viewer.

Check it with:

```bash
systemctl --user status wallpapers.timer
journalctl --user -u wallpapers.service
```
