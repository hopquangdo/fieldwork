import os
import sys

IMG = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")
base = os.path.abspath(sys.argv[1])
maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
lp = "\\\\?\\" + base
for root, dirs, files in os.walk(lp):
    rel = root[len(lp):].strip("\\")
    depth = rel.count("\\") if rel else 0
    if depth > maxdepth:
        dirs[:] = []
        continue
    dirs.sort()
    imgs = sum(1 for f in files if f.lower().endswith(IMG))
    name = os.path.basename(root) or os.path.basename(base)
    print(f"{'  ' * depth}{name}/  [{imgs}]")
