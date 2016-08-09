#! /usr/bin/python
import os
import sys
from time import localtime, strftime
args = sys.argv[1:]

ppath = "~/context/protocol"
ppath = os.path.expanduser(ppath)

time_str = "__" + strftime("%d.%m %H:%M", localtime()) + "__ - "

post = ' '.join([time_str] + args + ['\n\n'])

with open(ppath, 'r+') as f:
    content = f.readlines()
    f.seek(0,0)
    f.writelines([post] + content)

