import readline
import sys

def rlinput(prompt, prefill=''):
    if prefill is None:
        prefill = ''
    if not isinstance(prefill, str):
        prefill = str(prefill)
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()

def print_percent(num):
    num = int(num)
    if num < 10 :
        num = '0' + str(num)
    else :
        num = str(num)
    print('\b\b\b' + num + '%', end='')
    sys.stdout.flush()

def isint(num):
    try:
        int(num)
        b = True
    except:
        b = False
    return b