
import argparse
from pathlib import Path
import subprocess

path = Path('~/Documents/notes')
path = path.expanduser()

editor = 'vim "+normal Go" +startinsert {filename} -c ":set syntax=markdown"'

parser = argparse.ArgumentParser(description='Take a note.')
parser.add_argument('filename',
        nargs='?',
        default='note',
        help='Name of the note to edit.')
args = parser.parse_args()

filepath = path / args.filename
cmd = editor.format(filename=filepath)
subprocess.call(cmd, shell=True)
