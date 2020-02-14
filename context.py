
import click
import os
import shutil
import sys

from pathlib import Path
from textwrap import TextWrapper

# load configuration file
#conf = ConfigParser()
#CONFPATH = Path(__file__).parent / "context.conf"
#conf.read(CONFPATH)

DEF_SEP = "\n\n"
TERM_DESC_SEP = " - "
REF_SEP = "#"

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class Context:
    def __init__(self, defs=None):
        self.defs = defs or []

    def add(self, term, desc, ref=None):
        self.defs.append(term, desc, ref)

    def define(self, term):
        term = term.strip()
        for def_ in self.defs:
            if def_[0].lower() == term.lower():
                termsize = shutil.get_terminal_size((80, 20))
                print(Context.format_def(def_, termsize.columns))
                break
        else:
            print(color.RED + 'def not found !!', file=sys.stderr)

    def update(self, context):
        self.defs.extend(context.defs)

    @classmethod
    def from_path(csl, path):
        super_context= csl()
        for p, folders, files in os.walk(path):
            p = Path(p)
            for f in files:
                context = csl.from_file(p / f)
                super_context.update(context)
        return super_context

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            content = f.read()

        defs = content.split(DEF_SEP)
        defs = map(Context.filter_def, defs)
        defs = list(defs)
        return cls(defs)

    @staticmethod
    def filter_def(def_):

        # split term, description and references
        def_ = def_.strip()
        try:
            term, rest = def_.split(TERM_DESC_SEP, maxsplit=1)
            desc, *refs = rest.split(REF_SEP)
        except ValueError:
            print('Could not read:', def_, file=sys.stderr)
            term = def_
            desc = ''
            refs = []
        else:
            # remove double and surrounding white spaces
            clean = lambda str_ : ' '.join([part for part in str_.split() if part])
            term = clean(term)
            desc = clean(desc)
            refs = map(clean, refs)

        return term, desc, refs

    @staticmethod
    def format_def(def_, width):
        term, desc, refs = def_
        lines = []
        w = TextWrapper(
            initial_indent =color.YELLOW + term + color.END + TERM_DESC_SEP,
            subsequent_indent = ' ' * (len(term) + len(TERM_DESC_SEP)),
            width = width,
        )
        lines.extend(w.wrap(desc))
        for ref in refs:
            lines.extend(w.wrap(ref))
        return '\n'.join(lines)


    def __str__(self):
        termsize = shutil.get_terminal_size((80, 20))
        def_blocks = []
        #max_len = max(len(term) for term, *_ in self.defs)
        print('yea')
        for def_ in self.defs:
            text = Context.format_def(def_, termsize.columns)
            def_blocks.append(text)
        return DEF_SEP.join(def_blocks)


if __name__ == "__main__":
    PATH = "~/Documents/context"
    PATH = Path(PATH).expanduser()
    c = Context.from_path(PATH)

    if sys.argv[1] == 'define':
        for term in sys.argv[2:]:
            c.define(term)
    elif sys.argv[1] == 'list':
        for term,_,_ in c.defs:
            print(term)
    else:
        raise Exception("wrong argument: " + str(sys,argv[1]))
