import os
from sys import argv
from pyment import PyComment

filename = argv[1]

c = PyComment(filename)
c.proceed()
c.diff(os.path.basename(filename) + ".patch")
c.write_patch_file(filename + ".patch", c.get_output_docs())
for s in c.get_output_docs():
    print(s)