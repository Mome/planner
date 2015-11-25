def style(lines, args):
    if isinstance(args, str):
        args = args.replace(' ','').upper().split(',')
    else:
        args = [a.strip().upper() for a in args]
    args = [style_map[a] for a in args]
    for i,line in enumerate(lines):
        lines[i] = _styled(line, *args)


def _styled(text, *args):
    if args:
        style_str = (postfix + prefix).join(args)
        str_list = [prefix,  style_str, postfix, text, prefix, style_map['RESET'], postfix]
        text = ''.join(str_list)
    return text


prefix = '\x1b['
var_prefix = '\033['
postfix = 'm'
    
style_map = {
    'BOLD' : '1',
    'DIM' : '2',
    'ITALIC' : '3',
    'UNDERLINE': '4',
    'BLINK' : '5',
    'REVERSE' : '6' ,
    'HIDDEN' : '7',
    'CROSSEDOUT' : '9',
    'RESET' : '0',
    'NOT_BOLD' : '21',
    'NOT_DIM' : '22',
    'NOT_ITALIC' : '23',
    'NOT_UNDERLINE' : '24',
    'NOT_BLINK' : '25',
    'STEADY' : '25',
    'NOT_REVERSE' : '26',
    'POSITIVE' : '26',
    'NOT_HIDDEN' : '27',
    'VISIBLE' : '27',
    'NOT_CROSSEDOUT' : '29',
    'F_DEFAULT' : '39',
    'F_BLACK' : '30',
    'F_RED' : '31',
    'F_GREEN' : '32',
    'F_YELLOW' : '33',
    'F_BLUE' : '34',
    'F_MAGENTA' : '35',
    'F_CYAN' : '36',
    'F_LIGHTGRAY' : '37',
    'F_DARKGRAY' : '90',
    'F_LIGHTRED' : '91',
    'F_LIGHTGREEN' : '92',
    'F_LIGHTYELLOW' : '93',
    'F_LIGHTBLUE' : '94',
    'F_LIGHTMAGENTA' : '95',
    'F_LIGHTCYAN' : '96',
    'F_WHITE' : '97',
    'B_DEFAULT' : '49',
    'B_BLACK' : '40',
    'B_RED' : '41',
    'B_GREEN' : '42',
    'B_YELLOW' : '43',
    'B_BLUE' : '44',
    'B_MAGENTA' : '45',
    'B_CYAN' : '46',
    'B_LIGHTGRAY' : '47',
    'B_DARKGRAY' : '100',
    'B_LIGHTRED' : '101',
    'B_LIGHTGREEN' : '102',
    'B_LIGHTYELLOW' : '103',
    'B_LIGHTBLUE' : '104',
    'B_LIGHTMAGENTA' : '105',
    'B_LIGHTCYAN' : '106',
    'B_WHITE' : '107'
}
