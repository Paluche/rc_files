import logging
from enum import IntEnum
from copy import copy
from re import sub

#
# Global format option
#


##
# @brief Boolean which make all the color and blinking format from the function
#        below enabled or not.
format_enabled   = True

##
# @brief Boolean which make all the blinking format from the function below
#        enabled or not.
blinking_enabled = True


#
# String output format utils
#


##
# @brief The colors you can use in escape sequence formats.
class Color(IntEnum):
    BLACK   = 0
    RED     = 1
    GREEN   = 2
    YELLOW  = 3
    BLUE    = 4
    MAGENTA = 5
    CYAN    = 6
    WHITE   = 7


##
# @brief Escape sequence which will make a formatting coloring the text
#        printing after it. More information on the different formatting:
#        https://en.wikipedia.org/wiki/ANSI_escape_code#Codes
#
# @param reset        Boolean to indicate to reset all previous format. Default
#                     is True.
# @param fg           Foreground color. Color of the text printed. If None
#                     default foreground color from your terminal will be used.
#                     Default is None.
# @param fg_bright    Boolean to indicate to the bright version for the
#                     foreground color. Default is False.
# @param bg           Background color. If None default background color from
#                     your terminal will be used. Default is None.
# @param bg_bright    Boolean to indicate to the bright version for the
#                     background color. Default is False.
# @param bold         Boolean to indicate to the enable or disable the bold
#                     format on the text. If None the bold format is left
#                     untouched. If False it would also disable the faint
#                     formatting. Default is None.
# @param faint        Boolean to indicate to the enable or disable the faint
#                     format on the text. If None faint format is left
#                     untouched. If False it would also disable the bold
#                     formatting. Default is None.
# @param underline    Boolean to indicate to the enable or disable the
#                     underline format on the text. If None underline format is
#                     left untouched. Default is None.
#
# @return Escape sequence which will produce the desired format on the text
#         which follows it.
def get_color_format(reset=True, fg=None, fg_bright=False, bg=None,
                     bg_bright=False, bold=None, faint=None, underline=None):
    global format_enabled

    codes = []

    if not format_enabled:
        return ''

    if reset:
        codes.append('0')

    if fg is not None:
        if fg not in list(Color):
            raise ValueError()

        if fg_bright:
            codes.append(90 + fg)
        else:
            codes.append(30 + fg)

    if bg is not None:
        if bg not in list(Color):
            raise ValueError()

        if bg_bright:
            codes.append(100 + bg)
        else:
            codes.append(40 + bg)

    if bold is not None or faint is not None:
        if bold:
            codes.append(1)
        elif faint:
            codes.append(2)
        else:
            codes.append(22)

    if underline is not None:
        if underline:
            codes.append(4)
        else:
            codes.append(24)

    if codes:
        return '\033[{}m'.format(';'.join(f'{code}' for code in codes))

    return ''


##
# @brief Escape sequence which will make a formatting blink the text printing
#        after it. More information on the different formatting:
#        https://en.wikipedia.org/wiki/ANSI_escape_code#Codes
#
# @note Rendering depends on the terminal used. From some testing on one
#       terminal configuration the blinking does not work when background color
#       is set.
#
# @param enable Boolean to indicate to the enable or disable the blinking
#               format on the text. If None returns no escape sequence.
#
# @return The escape sequence desired.
def get_blink_format(enable):
    global format_enabled
    global blinking_enabled

    if enable is None or not blinking_enabled or not format_enabled:
        return ''

    if enable:
        return '\033[5m'

    return '\033[25m'


##
# @brief Escape sequence which will make a formatting. More information on the
#        different formatting:
#        https://en.wikipedia.org/wiki/ANSI_escape_code#Codes
#
# @param reset      Boolean to indicate to reset all previous format. Default
#                   is True.
# @param fg         Foreground color. Color of the text printed. If None
#                   default foreground color from your terminal will be used.
#                   Default is None.
# @param fg_bright  Boolean to indicate to the bright version for the
#                   foreground color. Default is False.
# @param bg         Background color. If None default background color from
#                   your terminal will be used. Default is None.
# @param bg_bright  Boolean to indicate to the bright version for the
#                   background color. Default is False.
# @param bold       Boolean to indicate to the enable or disable the bold
#                   format on the text. If None the bold format is left
#                   untouched. If False it would also disable the faint
#                   formatting. Default is None.
# @param faint      Boolean to indicate to the enable or disable the faint
#                   format on the text. If None faint format is left
#                   untouched. If False it would also disable the bold
#                   formatting. Default is None.
# @param underline  Boolean to indicate to the enable or disable the
#                   underline format on the text. If None underline format is
#                   left untouched. Default is None.
# @param blink      Boolean to indicate to the enable or disable the slow
#                   blink format on the text. If None blinking format is left
#                   untouched. If False it would also disable the fast blink
#                   formatting. Default is None.
#
# @return Escape sequence which will produce the desired format on the text
#         which follows it.
def get_format(reset=True, fg=None, fg_bright=False, bg=None, bg_bright=False,
               bold=None, faint=None, underline=None, blink=None):

    ret = get_color_format(reset=reset, fg=fg, fg_bright=fg_bright,
                           bg=bg, bg_bright=bg_bright, bold=bold,
                           faint=faint, underline=underline)

    ret += get_blink_format(blink)

    return ret


##
# @brief Print a message which is formatted with the specified parameters.
#
# @param *args     Positional arguments to be printed. Like the built-in
#                  print() method, each argument is printed separated by a
#                  space.
# @param **kwargs  Keyword arguments for the get_format() method.
def format_string(*args, **kwargs):
    if not args:
        return ''

    return get_format(**kwargs) + ' '.join([str(x) for x in args]) + \
           get_format()


##
# @brief Print a message which is formatted with the specified parameters.
#
# @param *args        Positional arguments to be printed.
# @param reset        Boolean to indicate to reset all previous format. Default
#                     is True.
# @param fg_bright    Boolean to indicate to the bright version for the
#                     foreground color. Default is False.
# @param bg           Background color. If None default background color from
#                     your terminal will be used. Default is None.
# @param bg_bright    Boolean to indicate to the bright version for the
#                     background color. Default is False.
# @param bold         Boolean to indicate to the enable or disable the bold
#                     format on the text. If None the bold format is left
#                     untouched. If False it would also disable the faint
#                     formatting. Default is None.
# @param faint        Boolean to indicate to the enable or disable the faint
#                     format on the text. If None faint format is left
#                     untouched. If False it would also disable the bold
#                     formatting. Default is None.
# @param underline    Boolean to indicate to the enable or disable the
#                     underline format on the text. If None underline format is
#                     left untouched. Default is None.
# @param slow_blink   Boolean to indicate to the enable or disable the slow
#                     blink format on the text. If None underline format is
#                     left untouched. If False it would also disable the fast
#                     blink formatting. Default is None.
# @param fast_blink   Boolean to indicate to the enable or disable the fast
#                     blink format on the text. If None underline format is
#                     left untouched. If False it would also disable the slow
#                     blink formatting. Default is None.
# @param **kwargs     Additional key-word arguments which will be provided to
#                     the builtin method print().
#
# @return Escape sequence which will produce the desired format on the text
#         which follows it.
def print_format(*args, reset=True, fg=None, fg_bright=None, bg=None,
                 bg_bright=False, bold=None, faint=None, underline=None,
                 blink=None, **kwargs):
    print(
        format_string(
            *args,
            reset=reset,
            fg=fg,
            fg_bright=fg_bright,
            bg=bg,
            bg_bright=bg_bright,
            bold=bold,
            faint=faint,
            underline=underline,
            blink=blink
        ),
        **kwargs
    )
