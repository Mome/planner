from math import ceil,floor
from functools import reduce
from operator import mul

"""
        0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+250x  ─   ━   │   ┃   ┄   ┅   ┆   ┇   ┈   ┉   ┊   ┋   ┌   ┍   ┎   ┏
U+251x  ┐   ┑   ┒   ┓   └   ┕   ┖   ┗   ┘   ┙   ┚   ┛   ├   ┝   ┞   ┟
U+252x  ┠   ┡   ┢   ┣   ┤   ┥   ┦   ┧   ┨   ┩   ┪   ┫   ┬   ┭   ┮   ┯
U+253x  ┰   ┱   ┲   ┳   ┴   ┵   ┶   ┷   ┸   ┹   ┺   ┻   ┼   ┽   ┾   ┿
U+254x  ╀   ╁   ╂   ╃   ╄   ╅   ╆   ╇   ╈   ╉   ╊   ╋   ╌   ╍   ╎   ╏
U+255x  ═   ║   ╒   ╓   ╔   ╕   ╖   ╗   ╘   ╙   ╚   ╛   ╜   ╝   ╞   ╟
U+256x  ╠   ╡   ╢   ╣   ╤   ╥   ╦   ╧   ╨   ╩   ╪   ╫   ╬   ╭   ╮   ╯
U+257x  ╰   ╱   ╲   ╳   ╴   ╵   ╶   ╷   ╸   ╹   ╺   ╻   ╼   ╽   ╾   ╿
"""

# oder: top, bottom, left, right
connection_code =  {
    0x0000 : ' ',
    0x0011 : '─',
    0x0022 : '━',
    0x1100 : '│',
    0x0022 : '┃',
    0x0101 : '┌',
    0x0102 : '┍',
    0x0201 : '┎',
    0x0202 : '┏',
    0x0110 : '┐',
    0x0120 : '┑',
    0x0210 : '┒',
    0x0220 : '┓',
    0x1001 : '└',
    0x1002 : '┕',
    0x2001 : '┖',
    0x2002 : '┗',
    0x1010 : '┘',
    0x1020 : '┙',
    0x2010 : '┚',
    0x2020 : '┛',
    0x1101 : '├',
    0x1102 : '┝',
    0x2101 : '┞',
    0x1201 : '┟',
    0x2201 : '┠',
    0x2102 : '┡',
    0x1202 : '┢',
    0x2202 : '┣',
    0x1110 : '┤',
    0x1120 : '┥',
    0x2110 : '┦',
    0x1210 : '┧',
    0x2210 : '┨',
    0x2120 : '┩',
    0x1220 : '┪',
    0x2220 : '┫',
    0x0111 : '┬',
    0x0121 : '┭',
    0x0112 : '┮',
    0x0122 : '┯',
    0x0211 : '┰',
    0x0221 : '┱',
    0x0212 : '┲',
    0x0222 : '┳',
    0x1011 : '┴',
    0x1021 : '┵',
    0x1012 : '┶',
    0x1022 : '┷',
    0x2011 : '┸',
    0x2021 : '┹',
    0x2012 : '┺',
    0x2022 : '┻',
    0x1111 : '┼',
    0x1121 : '┽',
    0x1112 : '┾',
    0x1122 : '┿',
    0x2111 : '╀',
    0x1211 : '╁',
    0x2211 : '╂',
    0x2121 : '╃',
    0x2112 : '╄',
    0x1221 : '╅',
    0x1212 : '╆',
    0x2122 : '╇',
    0x1222 : '╈',
    0x2221 : '╉',
    0x2212 : '╊',
    0x2222 : '╋',
    0x0033 : '═',
    0x3300 : '║',
    0x0103 : '╒',
    0x0301 : '╓',
    0x0303 : '╔',
    0x0130 : '╕',
    0x0310 : '╖',
    0x0330 : '╗',
    0x1003 : '╘',
    0x3001 : '╙',
    0x3003 : '╚',
    0x1030 : '╛',
    0x3010 : '╜',
    0x3030 : '╝',
    0x1103 : '╞',
    0x3301 : '╟',
    0x3303 : '╠',
    0x1130 : '╡',
    0x3310 : '╢',
    0x3330 : '╣',
    0x0133 : '╤',
    0x0311 : '╥',
    0x0333 : '╦',
    0x1033 : '╧',
    0x3011 : '╨',
    0x3033 : '╩',
    0x1133 : '╪',
    0x3311 : '╫',
    0x3333 : '╬',
    0x0010 : '╴',
    0x1000 : '╵',
    0x0001 : '╶',
    0x0100 : '╷',
    0x0020 : '╸',
    0x2000 : '╹',
    0x0002 : '╺',
    0x0200 : '╻',
    0x0012 : '╼',
    0x1200 : '╽',
    0x0021 : '╾',
    0x2100 : '╿',
}

"""ATTRIBUTES:
line_style : heavy, light, triple_dash, quadrupel_dash, double
"""

class ConnectionSupplier:
    def __ini__(self, line_code_):
        self.line_code = line_code(line_code_)

    def get_connection(*args):
        args = [keymap[a] for a in args]
        f = lambda x : self.line_code if x in args else None 
        top = f('top')
        bot = f('bottom')
        rig = f('right')
        lef = f('left')

        return ''.join([top,bot,rig,lef])

keymap = {
    None : None,
    'ascii' : 'ascii',
    'light' : 'light',
    'heavy' : 'heavy',
    'big' : 'heavy',
    'double': 'double',
    '=' : 'double',
    'solid' : 'solid',
    '-' : 'solid',
    'dashed' : 'dashed',
    '2dash' : 'dashed',
    '--' : 'dashed',
    'triple_dashed' : 'triple_dashed',
    '3dash' : 'triple_dashed',
    '---' : 'triple_dashed',
    'quadrupel_dashed' : 'quadrupel_dashed',
    '4dash' : 'quadrupel_dashed',
    '----' : 'quadrupel_dashed',
    'round' : 'rounded',
    'left':'left',
    'right':'right',
    'top':'top',
    'bottom':'bottom',
    'bot':'bottom',
    'rounded':'rounded',
    'round':'rounded',
}

line_code = {
    None     : '0',
    'light'  : '1',
    'heavy'  : '2',
    'double' : '3',
}


def get_linestyle(style1='solid', style2='light'):
    """Returns a dict with box drawing elements.

       Args:
       -----
       style1 : 'solid','dashed','triple_dashed','quadrupel_dashed','double','ascii'
       style2 : 'light','heavy','rounded'
    """
    style1 = keymap[style1.lower()]
    style2 = keymap[style2.lower()]

    if style1 in ('ascii', 'double'):
        lines = line_sets[style1]
        corners = corner_sets[style1]
    elif style2 == 'rounded':
        lines = line_sets[style1]['light']
        corners = corner_sets['rounded']
    else :
        lines = line_sets[style1][style2]
        corners = corner_sets[style2]
    
    # return { **lines, **corners} # requires python 3.5
    out = {}
    out.update(lines)
    out.update(corners)
    return out


def get_connection(top=None, bottom=None, left=None, right=None):
    code = [line_code[keymap[k]] for k in (top,bottom,left,right)]
    code = int(''.join(code), base=16)
    return connection_code[code]


line_sets = {
    'ascii' : {
        'horizontal' : '-',
        'vertical' : '|',
    },
    'solid' : {
        'light' : {
            'horizontal' : '─',
            'vertical' : '│',
        },
        'heavy' : {
            'horizontal' : '━',
            'vertical' : '┃',
        },
    },
    'dashed' : {
        'light' : {
            'horizontal' : '╌',
            'vertical' : '╎',
        },
        'heavy' : {
            'horizontal' : '╍',
            'vertical' : '╏',
        },
    },
    'triple_dashed' : {
        'light' : {
            'horizontal' : '┄',
            'vertical' : '┆',
        },
        'heavy' : {
            'horizontal' : '┅',
            'vertical' : '┇',
        },
    },
    'quadruple_dashed' :{
        'light' : {
            'horizontal' : '┈',
            'vertical' : '┊',
        },
        'heavy' : {
            'horizontal' : '┉',
            'vertical' : '┋',
        },
    },
    'double' : {
        'horizontal' : '═',
        'vertical' : '║',
    },
}

corner_sets = {
    'light' : {
        'down_right' : '┌',
        'down_left'  : '┐',
        'up_right'   : '└',
        'up_left'    : '┘',
        'junction'   : '┼',
    },
    'ascii' : {
        'down_right' : '+',
        'down_left'  : '+',
        'up_right'   : '+',
        'up_left'    : '+',
        'junction'   : '+',
    },
    'heavy' : {
        'down_right' : '┏',
        'down_left'  : '┓',
        'up_right'   : '┗',
        'up_left'    : '┛',
        'junction'   : '╋',
    },
    'rounded' : {
        'down_right' : '╭',
        'down_left'  : '╮',
        'up_right'   : '╰',
        'up_left'    : '╯',
        'junction'   : '┼',
    },
    'double' : {
        'down_right' : '╔',
        'down_left'  : '╗',
        'up_right'   : '╚',
        'up_left'    : '╝',
        'junction'   : '╬',
    },
}

class Box:
    def __init__(self,
            text='',
            height=None,
            width=None,
            line_style='-'):

        self.text=text
        self.set_line_style(line_style)       
 
        if height is None:
           self.fit_height()
        else:
            self.height = height
        
        if width is None:
            self.fit_width()
        else:
            self.width = width

    def fit_width(self):
        rows = self.text.splitlines()
        max_len = max(map(len, rows))
        self.width = max_len + 2
        
    def fit_height(self):
        row_num = len(self.text.splitlines())
        self.height = row_num + 2
        
    def fit_size(self):
        self.fit_width()
        self.fit_height()

    def set_line_style(self,style):
        style = get_line_style_identifier(style) 
        self.line_style = style
  
    def render(self):
        # load character set
        s = line_style_sets[self.line_style]
        rows = self.text.splitlines()
        rows = [
            s['vertical'] +
            ' '*floor(((self.width-2)-len(row))/2) +
            row +
            ' '*ceil(((self.width-2)-len(row))/2) +
            s['vertical']
            for row in rows
        ]
        top = s['down_right'] + (self.width-2)*s['horizontal'] + s['down_left']
        bot = s['up_right'] + (self.width-2)*s['horizontal'] + s['up_left']
        rows = [top] + rows + [bot]
        return rows
    
    def __str__(self):
        rows = self.render()
        return '\n'.join(rows)

    
class Canvas:

    horl = [0,0,1,1]
    verl = [1,1,0,0]

    def __init__(self, width, height):
        self.screen = [[' ']*width for _ in range(height)]
        self.width = width
        self.height = height

    def draw_string(self, string, x, y):
        if len(string)+x > self.width:
            offset = self.width - len(string) - x
            string = string[:offset]
        self.screen[y][x:x+len(string)] = string

    def draw_horz_line(x, y, length, fill_left=False, fill_right=False):
        row = self.screen[y]
        if self.width < x+length:
            length -= (x+length)-self.width
        for i in range(x,x+length):
            if type(row[i]) == str:
                row[i] = [0,0,1,1]
            else:
                for j in range(4):
                    if horl[j]:
                        row=...




        
        
