# !/usr/bin/env python3

"""
Inspired from the script to highlight adb logcat output for console
written by Jeff Sharkey (http://jsharkey.org/)

This scripts get what on a specified tty serial port parse it and color it.
The input format will be in the format "[TAG] MESSAGE" by line.
The output will add the time of the reception in front of the line and TAG
will be colored with a color that won't change for a given 'TAG'.

Written by Hubert Lefevre.
"""

import os
import sys
import re
from io import StringIO
import fcntl
import termios
import struct
import datetime
import getopt
import serial


def style_fmt(fgd=None, bgd=None, dim=False, reset=False):
    """
    @brief

    @param fgd
    @param bgd
    @param dim
    @param reset

    @return
    """
    # manually derived from http://en.wikipedia.org/wiki/ANSI_escape_code#Codes
    codes = []
    if reset:
        codes.append("0")
    else:
        if fgd is not None:
            codes.append("3%d" % (fgd))
        if bgd is not None:
            codes.append("10%d" % (bgd))
        if dim:
            codes.append("2")
        else:
            codes.append("22")
    return "\033[%sm" % (";".join(codes))


def usage():
    """
    Print script usage.
    """
    print(
        """
        cortex_log.py <tty> [-w <nocolor>]
        or
        <source> | cortex_log.py [-w <nocolor>]

       <tty> Specify which tty to use, the script will use "/dev/tty<tty>"
        -T <regexp>  Show only logs which tags that match the specified regular
                     expression.
        -M <regexp>  Show logs which message match the specified regular
                     expression.
        -A <regexp>  Show logs which tags or message match the specified
                     regular expression.
        -i           Ignore case on the regular expression.
        -w <path>    Write output in a file (colorless).
        """
    )
    sys.exit(2)


#############
# Constants #
#############
# Unpack the current terminal width/height
data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
HEIGHT, WIDTH = struct.unpack('hh', data)

# Colors
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# Tag color allocation context
LAST_USED = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
KNOWN_TAGS = {}

# Width setting
TIME_WIDTH = 19  # Hard coded size of the time format e.g. '08-31 10:55:02.357'
TAG_WIDTH = 10
HEADER_SIZE = TAG_WIDTH + TIME_WIDTH

# Regular expression to match
REBOOTLINE = re.compile(r"^\(@\)(.*) (.*)$")
RERBOOTLINE = re.compile(r"^\r\(@\)(.*) (.*)$")
REMATCH = re.compile(r"^\[([^\(]+?)\] (.*)$")
RERMATCH = re.compile(r"^\r\[([^\(]+?)\] (.*)$")
RETAGONLY = re.compile(r"^\[([^\(]+?)\](.*)$")
RERTAGONLY = re.compile(r"^\r\[([^\(]+?)\](.*)$")
RESIMPLE = re.compile(r"^([^\(]+)([^\(]+)$")
RERSIMPLE = re.compile(r"^\r([^\(]+)([^\(]+)$")


# Format function
def print_time(linebuf, nocolor):
    """
    @brief

    @param linebuf
    @param nocolor

    @return
    """
    linebuf.write(
        "{}{} {}".format(
            style_fmt(fgd=GREEN, bgd=BLACK, dim=False),
            datetime.datetime.now().strftime(
                "%m-%d %H:%M:%S.%f"
            )[:-3],
            style_fmt(reset=True)
        )
    )
    nocolor.write(
        datetime.datetime.now().strftime(
            "%m-%d %H:%M:%S.%f"
        )[:-3]
    )


def allocate_color(tag):
    """
    @brief

    @param tag

    @return
    """
    # This will allocate a unique format for the given tag
    # since we dont have very many colors, we always keep track of the LRU
    if tag not in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    LAST_USED.remove(color)
    LAST_USED.append(color)
    return color


def print_tag(linebuf, nocolor, tag, bootline=False):
    """
    @brief

    @param linebuf
    @param nocolor
    @param tag
    @param bootline

    @return
    """
    # Right-align tag title and allocate color if needed
    tag = tag.strip()
    if bootline:
        color = RED
    else:
        color = allocate_color(tag)
    tag = tag[-TAG_WIDTH:].rjust(TAG_WIDTH)
    linebuf.write("%s%s %s" % (style_fmt(fgd=color, dim=False), tag,
                               style_fmt(reset=True)))
    nocolor.write("%s " % (tag))


def print_message(linebuf, nocolor, headersize, message, bootline=False):
    """
    @brief

    @param linebuf
    @param nocolor
    @param headersize
    @param message
    @param bootline

    @return
    """
    # Insert line wrapping as needed
    wrap_area = WIDTH - headersize - 3
    current = 0
    while current < len(message):
        index_next = min(current + wrap_area, len(message))
        linebuf.write("%s %s %s" % (style_fmt(bgd=BLACK, dim=False),
                                    style_fmt(reset=True),
                                    message[current:index_next]))
        nocolor.write("  %s" % (message[current:index_next]))

        if bootline:
            linebuf.write("%s " % (style_fmt(reset=True)))
            nocolor.write(" ")

        if index_next < len(message):
            linebuf.write("\n%s " % (" " * headersize))
            nocolor.write("\n%s " % (" " * headersize))
        current = index_next


########
# Main #
########

def main():
    """
    @brief Main
    """
    # Context
    re_flags = None
    re_tag_filter_exp = None
    re_msg_filter_exp = None
    re_tag_filter = None
    re_msg_filter = None
    writefile = None

    # If someone is piping in to us, use stdin as input, otherwise use first
    # argument to know which tty you should open
    if os.isatty(sys.stdin.fileno()):
        if len(sys.argv) < 2:
            usage()
        source = serial.Serial()
        source.port = "/dev/tty%s" % sys.argv[1]
        ########################
        # Serial configuration #
        ########################
        source.baudrate = 115200
        source.bytesize = serial.EIGHTBITS
        source.parity = serial.PARITY_NONE
        source.stopbits = serial.STOPBITS_ONE
        source.timeout = 0      # Non-Block reading
        source.xonxoff = False  # Disable Software Flow Control
        source.rtscts = False  # Disable (RTS/CTS) flow Control
        source.dsrdtr = False  # Disable (DSR/DTR) flow Control
        source.timeout = None   # Wait forever
        source.writeTimeout = 2
        try:
            source.open()
        except serial.SerialException as err:
            print(err)
            print("")
            usage()
        source.flushInput()
        source.flushOutput()
    else:
        source = sys.stdin

    # Handle options
    try:
        opts, _ = getopt.getopt(sys.argv[2:], "hw:iA:T:M:", ["help"])
    except getopt.GetoptError as err:
        print(err)
        print("")
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt == "-i":
            re_flags = re.IGNORECASE
        elif opt == "-a":
            re_tag_filter_exp = arg
            re_msg_filter_exp = arg
        elif opt == "-T":
            re_tag_filter_exp = arg
        elif opt == "-M":
            re_msg_filter_exp = arg
        elif opt == "-w":
            writefile = open(arg, 'a')
            if writefile is not None:
                print("File opened")
            else:
                print("Error opening file\n")
                usage()

    # Set filtering regular expressions
    if re_tag_filter_exp is not None:
        if re_flags is None:
            re_tag_filter = re.compile(re_tag_filter_exp)
        else:
            re_tag_filter = re.compile(re_tag_filter_exp, re_flags)

    if re_msg_filter_exp is not None:
        if re_flags is None:
            re_msg_filter = re.compile(re_msg_filter_exp)
        else:
            re_msg_filter = re.compile(re_msg_filter_exp, re_flags)

    # Set terminal name so you know the argument used
    sys.stdout.write("\x1b]2;cortex_log %s\x07" % ' '.join(sys.argv[1:]))

    # Flush first line
    try:
        line = source.readline()
    except KeyboardInterrupt:
        exit

    # Main loop
    while True:
        try:
            line = source.readline()
        except KeyboardInterrupt:
            break

        isbootline = False
        bootline = REBOOTLINE.match(line)
        if bootline is None:
            bootline = RERBOOTLINE.match(line)

        match = RERMATCH.match(line)
        if match is None:
            match = REMATCH.match(line)

        tagonly = RERTAGONLY.match(line)
        if tagonly is None:
            tagonly = RETAGONLY.match(line)

        simple = RERSIMPLE.match(line)
        if simple is None:
            simple = RESIMPLE.match(line)

        if bootline is not None:
            tag, message = bootline.groups()
            isbootline   = True

        elif match is not None:
            tag, message = match.groups()

        elif tagonly is not None:
            tag, uu = tagonly.groups()
            message = " "

        elif simple is not None:
            message, uu = simple.groups()
            tag         = " "

        elif len(line) == 0:
            break

        else:
            print(line)
            if writefile is not None:
                writefile.write(line)
            continue

        if re_tag_filter is not None:
            match_tag_filter = re_tag_filter.search(tag)

        if re_msg_filter is not None:
            match_msg_filter = re_msg_filter.search(message)

        if re_tag_filter is not None and re_msg_filter is not None:
            if match_tag_filter is None and match_msg_filter is None:
                continue
        elif re_tag_filter is not None:
            if match_tag_filter is None:
                continue
        elif re_msg_filter is not None and match_msg_filter is None:
            continue

        linebuf = StringIO()
        nocolor = StringIO()

        print_time(linebuf, nocolor)
        print_tag(linebuf, nocolor, tag, isbootline)
        print_message(linebuf, nocolor, HEADER_SIZE, message, isbootline)
        print(linebuf.getvalue())
        if writefile is not None:
            writefile.write(nocolor.getvalue() + '\n')


if __name__ == '__main__':
    main()
