#!/usr/bin/python3.8

'''
    Copyright 2009, The Android Open Source Project

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

# script to highlight adb logcat output for console
# written by jeff sharkey, http://jsharkey.org/
# piping detection and popen() added by other android team members
# Highlighting of the other logcat format by Hubert Lefevre

import os
import sys
import re
from io import StringIO
import fcntl
import termios
import struct
import getopt

# unpack the current terminal width
try:
    data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
    _, WIDTH = struct.unpack('hh', data)
except IOError:
    WIDTH = 134

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

LAST_USED = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
KNOWN_TAGS = {
    "dalvikvm": BLUE,
    "Process": BLUE,
    "ActivityManager": CYAN,
    "ActivityThread": CYAN,
}


def style_fmt(fgd=None, bgd=None, bright=False, dim=False, reset=False):
    """
    @brief

    @param fgd
    @param bgd
    @param bright
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
            if not bright:
                codes.append("4%d" % (bgd))
            else:
                codes.append("10%d" % (bgd))
        if dim:
            codes.append("2")
        else:
            codes.append("22")
    return "\033[%sm" % (";".join(codes))


OWNER_WIDTH = 7
THREAD_WIDTH = 7
TIME_WIDTH = 20
TAG_WIDTH = 26
TAG_TYPE_WIDTH = 3

TAG_TYPE_FORMAT = {
    "V": style_fmt(fgd=WHITE, bgd=BLACK),
    "D": style_fmt(fgd=BLACK, bgd=BLUE),
    "I": style_fmt(fgd=BLACK, bgd=GREEN),
    "W": style_fmt(fgd=BLACK, bgd=YELLOW),
    "E": style_fmt(fgd=BLACK, bgd=RED),
    "F": style_fmt(fgd=RED, bgd=WHITE),
    "S": style_fmt(fgd=BLACK, bgd=CYAN),
}

rebeginning = re.compile(r"^--------- beginning of ([^\)]+)([^\(]+)\r$")
rethreadtime = re.compile(r"^(\d+)-(\d+) (\d+):(\d+):(\d+).(\d+)([^\)]+) "
                          r"([^\)]+) ([VDIWEFS]) ([^\(]+?): (.*)$")
retime = re.compile(r"^(\d+)-(\d+) (\d+):(\d+):(\d+).(\d+) "
                    r"([VDIWEFS])/([^\(]+)\(([^\)]+)\): (.*)$")
rethread = re.compile(r"^([VDIWEFS])\(([^\)]+):([^\)]+)\) (.*)$")
rebrief = re.compile(r"^([VDIWEFS])/([^\(]+)\(([^\)]+)\): (.*)$")
retag = re.compile(r"^([VDIWEFS])/([^\(]+?): (.*)$")


def print_owner(linebuf, colorless, empty_header, owner):
    """
    @brief

    @param linebuf
    @param colorless
    @param empty_header
    @param owner

    @return
    """
    # center process owner info
    owner = owner.strip().center(OWNER_WIDTH)
    linebuf.write(
        "{}{}{}".format(
            style_fmt(fgd=CYAN, bgd=BLACK),
            owner,
            style_fmt(reset=True)
        )
    )
    colorless.write(f'{owner}')
    empty_header.write(
        "{}{}{}".format(
            style_fmt(fgd=CYAN, bgd=BLACK),
            " " * OWNER_WIDTH,
            style_fmt(reset=True)
        )
    )
    return OWNER_WIDTH


def print_thread(linebuf, colorless, empty_header, thread):
    """
    @brief

    @param linebuf
    @param colorless
    @param empty_header
    @param thread

    @return
    """
    # center thread info
    thread = thread.strip().center(THREAD_WIDTH)
    linebuf.write(
        "{}{}{}".format(
            style_fmt(fgd=CYAN, bgd=BLACK),
            thread,
            style_fmt(reset=True)
        )
    )
    colorless.write(f'{thread}')
    empty_header.write(
        "{}{}{}".format(
            style_fmt(fgd=CYAN, bgd=BLACK),
            " " * THREAD_WIDTH,
            style_fmt(reset=True)
        )
    )
    return THREAD_WIDTH


def print_time(linebuf, colorless, empty_header, date):
    """
    @brief

    @param linebuf
    @param colorless
    @param empty_header
    @param m
    @param d
    @param h
    @param mi
    @param s
    @param ms

    @return
    """
    linebuf.write(
        "{} {}-{} {}:{}:{}.{} {}".format(
            style_fmt(fgd=GREEN, bgd=BLACK),
            *date,
            style_fmt(reset=True)
        )
    )
    colorless.write(
        " {}-{} {}:{}:{}.{} ".format(
            *date
        )
    )
    empty_header.write(
        "{}{}{}".format(
            style_fmt(fgd=GREEN, bgd=BLACK),
            " " * TIME_WIDTH,
            style_fmt(reset=True)
        )
    )
    return TIME_WIDTH


def allocate_color(tag):
    """
    @brief

    @param tag

    @return
    """
    # this will allocate a unique format for the given tag
    # since we don't have very many colors, we always keep track of the LRU
    if tag not in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    LAST_USED.remove(color)
    LAST_USED.append(color)
    return color


def print_tag(linebuf, colorless, empty_header, tag):
    """
    @brief

    @param linebuf
    @param colorless
    @param empty_header
    @param tag

    @return
    """
    # right-align tag title and allocate color if needed
    tag = tag.strip()
    color = allocate_color(tag)
    tag = tag[-(TAG_WIDTH - 1):].rjust((TAG_WIDTH - 1))
    linebuf.write(
        "{}{} {}".format(
            style_fmt(fgd=color),
            tag,
            style_fmt(reset=True)
        )
    )
    colorless.write(f'{tag} ')
    empty_header.write(
        "{}{}{}".format(
            style_fmt(fgd=color),
            " " * TAG_WIDTH,
            style_fmt(reset=True)
        )
    )
    return TAG_WIDTH


def print_tag_type(linebuf, colorless, empty_header, tag_type):
    """
    @brief

    @param linebuf
    @param colorless
    @param empty_header
    @param tag_type

    @return
    """
    linebuf.write(
        "{}{}{} ".format(
            TAG_TYPE_FORMAT[tag_type],
            tag_type.center(TAG_TYPE_WIDTH),
            style_fmt(reset=True)
        )
    )
    colorless.write("{} ".format(tag_type.center(TAG_TYPE_WIDTH)))

    empty_header.write(
        "{}{}{} ".format(
            style_fmt(bgd=BLACK),
            " " * TAG_TYPE_WIDTH,
            style_fmt(reset=True)
        )
    )
    return TAG_TYPE_WIDTH + 1


def print_msg(linebuf, colorless, empty_header, header_size, msg):
    """
    @brief

    @param linebuf
    @param colorless
    @param empty_header
    @param header_size
    @param msg

    @return
    """
    wrap_area = WIDTH - header_size
    index_current = 0

    while index_current < len(msg):
        index_next = min(index_current + wrap_area - 6 * msg.count('\t'),
                         len(msg))

        linebuf.write(msg[index_current:index_next])
        colorless.write(msg[index_current:index_next])

        if index_next < len(msg):
            linebuf.write("\n%s" % (empty_header.getvalue()))
            colorless.write("\n%s" % (" " * header_size))
        index_current = index_next


def usage():
    """
    @brief Print script usage.
    """
    print(
        """
        This script can be used in two manners, by piping a flux from an
         adb logcat command or by itself it uses the options you gave him
         and parse and color the flux.

        In piping mode only the following format are handled (-v option):
            "brief" "tag" "thread" "time" "threadtime"
        Use "brief" instead of "process" their output from the script would
        have been the same. For the same reason use "threadtime" instead of
        "long".
        "raw" is a useless flux handled by this script, it doesn't have enough
        information to generate a color distinction.

        In non piping mode you have access to the following options
            -v <format>  Sets the log print format, where <format> is one of:
                           "brief", "tag", "thread", "time" or "threadtime"
            -c           Clear (flush) the entire log and exit.
            -S <device>  Directs command to the device or emulator with the
                         given serial number or qualifier. Overrides
                         ANDROID_SERIAL environment variable.

        In both mode you have access to the following options:
            --help / -h  Print this help.
            -T <regexp>  Show only logs which tags that match the specified
                         regular expression.
            -M <regexp>  Show logs which message match the specified regular
                         expression.
            -A <regexp>  Show logs which tags or message match the specified
                         regular expression.
            -i           Ignore case on the regular expression.
            -w <path>    Write output in a file (colorless).
        """
    )
    sys.exit(2)


def main():
    """
    The script.
    """
    # Regular expressions
    re_flags = None
    re_tag_filter_exp = None
    re_msg_filter_exp = None
    re_tag_filter = None
    re_msg_filter = None
    writefile = None

    # adb logcat options
    logcat_option_v = "time"
    logcat_option = StringIO()
    adb_option = StringIO()

    try:
        opts, arg = getopt.getopt(sys.argv[1:],
                                  "S:hscit:t:A:T:M:v:w:",
                                  ["help"])
    except getopt.GetoptError as err:
        print(err)
        print("")
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt == "-i":
            re_flags = re.IGNORECASE
        elif opt == "-A":
            re_tag_filter_exp = arg
            re_msg_filter_exp = arg
        elif opt == "-T":
            re_tag_filter_exp = arg
        elif opt == "-M":
            re_msg_filter_exp = arg
        elif opt == "-v":
            if arg in ("brief", "tag", "thread", "time", "threadtime"):
                logcat_option_v = arg
            elif arg == "long":
                logcat_option_v = "threadtime"
            elif arg == "process":
                logcat_option_v = "brief"
            else:
                print("Bad format.\n")
                usage()
        elif opt in ("-s", "-c", "-t"):
            logcat_option.write(" %s%s" % (opt, arg))
        elif opt == "-S":
            adb_option.write(" -s %s" % arg)
        elif opt == "-w":
            writefile = open(arg, 'a')

    # If someone is piping in to us, use stdin as input.  if not, invoke
    # adb logcat
    if os.isatty(sys.stdin.fileno()):
        input_line = os.popen(
            "adb{} logcat -v {}{}".format(
                adb_option.getvalue(),
                logcat_option_v,
                logcat_option.getvalue()
            )
        )
    else:
        input_line = sys.stdin

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

    while True:
        try:
            line = input_line.readline()
        except KeyboardInterrupt:
            break

        matchbeginning = rebeginning.match(line)
        matchthreadtime = rethreadtime.match(line)
        matchthread = rethread.match(line)
        matchtime = retime.match(line)
        matchbrief = rebrief.match(line)
        matchtag = retag.match(line)
        linebuf = StringIO()
        colorless = StringIO()
        empty_header = StringIO()
        header_size = 0
        date = None
        owner = None
        thread = None
        tag_type = None
        tag = None
        msg = None

        if matchbeginning is not None:
            msg, line = matchbeginning.groups()
            print(
                "{}{}{}".format(
                    style_fmt(fgd=WHITE, bgd=BLACK, dim=False),
                    (f"Beginning of {msg}{line}").center(WIDTH),
                    style_fmt(reset=True)
                )
            )

            if writefile is not None:
                writefile.write("Beginning of {msg}{line}".center(WIDTH))

            continue

        if matchthreadtime is not None:
            *date, owner, thread, tag_type, tag, msg = matchthreadtime.groups()

        elif matchthread is not None:
            tag_type, owner, thread, msg = matchthread.groups()

        elif matchtime is not None:
            *date, tag_type, tag, owner, msg = matchtime.groups()

        elif matchbrief is not None:
            tag_type, tag, owner, msg = matchbrief.groups()

        elif matchtag is not None:
            tag_type, tag, msg = matchtag.groups()

        else:
            print(line)
            if writefile is not None:
                writefile.write(line)
            if len(line) == 0:
                break
            continue

        # Print parts
        if owner is not None:
            header_size += print_owner(linebuf, colorless, empty_header, owner)

        if thread is not None:
            header_size += print_thread(linebuf,
                                        colorless,
                                        empty_header,
                                        thread)

        if date is not None:
            header_size += print_time(linebuf,
                                      colorless,
                                      empty_header,
                                      date)

        if tag is not None:
            if re_tag_filter is not None:
                match_tag_filter = re_tag_filter.search(tag)
            header_size += print_tag(linebuf, colorless, empty_header, tag)

        if tag_type is not None:
            header_size += print_tag_type(linebuf,
                                          colorless,
                                          empty_header,
                                          tag_type)

        if msg is not None:
            if re_msg_filter is not None:
                match_msg_filter = re_msg_filter.search(msg)
            print_msg(linebuf, colorless, empty_header, header_size, msg)

        # Filter on the regular expression
        if re_tag_filter is not None and re_msg_filter is not None:
            if match_tag_filter is None and match_msg_filter is None:
                continue
        elif re_tag_filter is not None:
            if match_tag_filter is None:
                continue
        elif re_msg_filter is not None and match_msg_filter is None:
            continue

        # Actual print
        print(linebuf.getvalue())
        if writefile is not None:
            writefile.write(colorless.getvalue() + '\n')


if __name__ == '__main__':
    main()
