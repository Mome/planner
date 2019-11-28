
import argparse
import os
import subprocess

NOTE_DIR = '~/Documents/notes'

editor = 'vim "+normal G$" +startinsert'

parser = argparse.ArgumentParser(description='Take a note.')
parser.add_argument('filename',
        nargs='?',
        default='note',
        help='Name of the note to edit.')
args = parser.parse_args()

path = os.path.expanduser(NOTE_DIR)
path = os.path.join(path, args.filename)
cmd = editor + ' ' + path

subprocess.call(cmd, shell=True)
