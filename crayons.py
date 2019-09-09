# -*- coding: utf-8 -*-
"""A simple and elegant wrapper for colorama."""

import os
from random import choice, seed
import re
import sys

import colorama

PY3 = sys.version_info[0] >= 3


__all__ = (
    'red', 'green', 'yellow', 'blue',
    'black', 'magenta', 'cyan', 'white',
    'clean', 'disable', 'enable', 'random'
)

colorama.init()
seed()
COLORS = __all__[:-4]


if 'get_ipython' in dir():
    """
       when ipython is fired lot of variables like _oh, etc are used.
       There are so many ways to find current python interpreter is ipython.
       get_ipython is easiest is most appealing for readers to understand.
    """
    DISABLE_COLOR = True
else:
    DISABLE_COLOR = False

if os.getenv("TERM") == "dumb":
    DISABLE_COLOR = True


class ColoredString(object):
    """Enhanced string for __len__ operations on Colored output."""

    def __init__(self, color, s, always_color=False, bold=False):
        super(ColoredString, self).__init__()
        if not PY3 and isinstance(s, unicode):  # noqa: F821
            self.s = s.encode('utf-8')
        else:
            self.s = s
        self.color = color
        self.always_color = always_color
        self.bold = bold
        if os.environ.get('CLINT_FORCE_COLOR'):
            self.always_color = True

    def __getattr__(self, att):
        def func_help(*args, **kwargs):
            result = getattr(self.s, att)(*args, **kwargs)
            try:
                is_result_string = isinstance(result, basestring)
            except NameError:
                is_result_string = isinstance(result, str)
            if is_result_string:
                return self._new(result)
            elif isinstance(result, list):
                return [self._new(x) for x in result]
            else:
                return result
        return func_help

    @property
    def color_str(self):
        style = 'BRIGHT' if self.bold else 'NORMAL'
        c = '%s%s' % (
            getattr(colorama.Fore, self.color),
            getattr(colorama.Style, style)
        )

        # Find ANSI terminal escape sequences and add color info
        # after them in the string
        s = self.s
        escape_regex = re.compile(
            r"""(?:\x1b\[[0-9]+m){2} # the first two ANSI esc seqs
                (?:(?!\x1b)+.*)+     # anything not starting with esc seq
                (?:\x1b\[[0-9]+m){2} # the last two ANSI esc seqs""", re.X
        )
        escape_seqs = set(re.findall(escape_regex, s))
        for seq in escape_seqs:
            spl = s.split(seq)
            s = (seq + c).join(spl)

        c = '%s%s%s%s' % (c, s, colorama.Style.NORMAL, colorama.Fore.RESET)

        if self.always_color:
            return c
        elif sys.stdout.isatty() and not DISABLE_COLOR:
            return c
        else:
            return self.s

    def __len__(self):
        return len(self.s)

    def __repr__(self):
        return "<%s-string: '%s'>" % (self.color, self.s)

    def __unicode__(self):
        value = self.color_str
        if isinstance(value, bytes):
            return value.decode('utf8')
        return value

    if PY3:
        __str__ = __unicode__
    else:
        def __str__(self):
            return self.color_str

    def __iter__(self):
        return iter(self.color_str)

    def __add__(self, other):
        return str(self.color_str) + str(other)

    def __radd__(self, other):
        return str(other) + str(self.color_str)

    def __mul__(self, other):
        return (self.color_str * other)

    def _new(self, s):
        return ColoredString(self.color, s)


def clean(s):
    strip = re.compile(r"([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")  # noqa: E501
    txt = strip.sub('', str(s))

    strip = re.compile(r'\[\d+m')
    txt = strip.sub('', txt)

    return txt


_colors = {x: x.upper() for x in COLORS}
_colors['normal'] = 'RESET'

for key, val in _colors.items():
    function = eval(
        'lambda s, always=False, bold=False: ColoredString("{}", s, always_color=always, bold=bold)'.format(val))  # noqa: E501
    locals()[key] = function

del key, val, _colors, function


def random(string, always=False, bold=False, colors=COLORS):
    """Selects a color at random from a list."""
    colors = list(filter(lambda color: color in COLORS, colors)) or COLORS
    return ColoredString(
        choice(colors).upper(),
        string,
        always_color=always,
        bold=bold
    )


def disable():
    """Disables colors."""
    global DISABLE_COLOR

    DISABLE_COLOR = True


def enable():
    """Enables colors."""
    global DISABLE_COLOR

    DISABLE_COLOR = False
