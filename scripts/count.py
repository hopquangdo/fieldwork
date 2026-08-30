import os
import sys

IMG = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")
lp = "\\\\?\\" + os.path.abspath(sys.argv[1])
n = sum(1 for _, _, fs in os.walk(lp) for f in fs if f.lower().endswith(IMG))
d = sum(1 for _, ds, _ in os.walk(lp) for _ in ds)
print(f"{sys.argv[1]}  ->  {n} images, {d} dirs")
