import os
import sys

base = os.path.abspath(sys.argv[1])
lp = "\\\\?\\" + base
for root, _, files in os.walk(lp):
    for f in sorted(files):
        print(os.path.join(root, f)[len(lp):].strip("\\"))
