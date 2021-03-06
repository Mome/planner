
import argparse
from pathlib import Path
import subprocess
import os

note_path = Path('~/Documents/notes')
note_path = note_path.expanduser()

editor = 'vim "+normal Go" +startinsert {filename} -c ":set syntax=markdown"'

# Terminal Colors
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    YELLOW = '\033[33m'

super_parser = argparse.ArgumentParser()
subparsers = super_parser.add_subparsers(dest='subparser')

parser = subparsers.add_parser(
    name = 'edit',
    help = 'Edit a note file')
parser.add_argument('filename',
    nargs='?',
    default='note',
    help='Name of the note to edit.')

parser = subparsers.add_parser(
    name = 'push',
    help = 'Append a note to a note file')
parser.add_argument('--filename', '-f',
    nargs='?',
    default='note',
    help='Name of the note file to be edited.')
parser.add_argument('line',
    nargs="+",
    default='note',
    help='Note line.')

parser = subparsers.add_parser(
    name = 'list',
    help = 'List all notes.')
parser.add_argument('--all', '-a',
    action="store_true",
)

args = super_parser.parse_args()

#print(args)

if args.subparser is None:
    args.subparser = "edit"
    args.filename = "note"

if args.subparser == "edit":
    filepath = note_path / args.filename
    cmd = editor.format(filename=filepath)
    subprocess.call(cmd, shell=True)
elif args.subparser == "push":
    filepath = note_path / args.filename
    line = ' '.join(args.line)
    with open(filepath, 'a') as notefile:
        notefile.write(line)
elif args.subparser == "list":
    note_path_len = len(note_path.parts)
    for path, folders, files in os.walk(note_path):
        relative_path = '.'.join(Path(path).parts[note_path_len:])
        if not args.all and relative_path == "archive":
            continue
        print()
        if relative_path:
            print(colors.HEADER + relative_path + colors.END)
            #print("="*len(relative_path))
        for f in files:
            print(colors.YELLOW + ' -' + colors.END, f)
    print()
