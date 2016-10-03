#!/usr/bin/python

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

import os, sys, re, StringIO
import fcntl, termios, struct
import getopt

# unpack the current terminal width/height
data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
HEIGHT, WIDTH = struct.unpack('hh',data)

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

LAST_USED = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
KNOWN_TAGS = {
    "dalvikvm"        : BLUE,
    "Process"         : BLUE,
    "ActivityManager" : CYAN,
    "ActivityThread"  : CYAN,
}

def format(fg = None, bg = None, bright = False, bold = False, dim = False,
           reset = False):
    # manually derived from http://en.wikipedia.org/wiki/ANSI_escape_code#Codes
    codes = []
    if reset:
        codes.append("0")
    else:
        if not fg is None:
            codes.append("3%d" % (fg))
        if not bg is None:
            if not bright:
                codes.append("4%d" % (bg))
            else:
                codes.append("10%d" % (bg))
        if bold:
            codes.append("1")
        elif dim:
            codes.append("2")
        else:
            codes.append("22")
    return "\033[%sm" % (";".join(codes))

OWNER_WIDTH   = 7
THREAD_WIDTH  = 7
TIME_WIDTH    = 20
TAG_WIDTH     = 26
TAGTYPE_WIDTH = 3

TAGTYPEFORMAT = {
    "V": format(fg = WHITE, bg = BLACK),
    "D": format(fg = BLACK, bg = BLUE),
    "I": format(fg = BLACK, bg = GREEN),
    "W": format(fg = BLACK, bg = YELLOW),
    "E": format(fg = BLACK, bg = RED),
    "F": format(fg = RED,   bg = WHITE),
    "S": format(fg = BLACK, bg = CYAN),
}

rebeginning  = re.compile("^--------- beginning of ([^\)]+)([^\(]+)\r$")
rethreadtime = re.compile("^(\d+)-(\d+) (\d+):(\d+):(\d+).(\d+)([^\)]+) " \
                          "([^\)]+) ([VDIWEFS]) ([^\(]+?): (.*)$")
retime       = re.compile("^(\d+)-(\d+) (\d+):(\d+):(\d+).(\d+) " \
                          "([VDIWEFS])/([^\(]+)\(([^\)]+)\): (.*)$")
rethread     = re.compile("^([VDIWEFS])\(([^\)]+):([^\)]+)\) (.*)$")
rebrief      = re.compile("^([VDIWEFS])/([^\(]+)\(([^\)]+)\): (.*)$")
retag        = re.compile("^([VDIWEFS])/([^\(]+?): (.*)$")

def print_owner(linebuf, colorless, emptyHeader, owner):
    # center process owner info
    owner = owner.strip().center(OWNER_WIDTH)
    linebuf.write("%s%s%s" % (format(fg = CYAN, bg = BLACK), owner,
                              format(reset = True)))
    colorless.write("%s" % (owner));
    emptyHeader.write("%s%s%s" % (format(fg = CYAN, bg = BLACK),
                                  " " * OWNER_WIDTH, format(reset = True)))
    return OWNER_WIDTH

def print_thread(linebuf, colorless, emptyHeader, thread):
    # center thread info
    thread = thread.strip().center(THREAD_WIDTH)
    linebuf.write("%s%s%s" % (format(fg = CYAN, bg = BLACK), thread,
                              format(reset = True)))
    colorless.write("%s" % (thread));
    emptyHeader.write("%s%s%s" % (format(fg = CYAN, bg = BLACK),
                                  " " * THREAD_WIDTH,
                                  format(reset = True)))
    return THREAD_WIDTH

def print_time(linebuf, colorless, emptyHeader, m, d, h, mi, s, ms):
    linebuf.write("%s %s-%s %s:%s:%s.%s %s" % (format(fg = GREEN, bg = BLACK),
                                               m, d, h, mi, s, ms,
                                               format(reset = True)))
    colorless.write(" %s-%s %s:%s:%s.%s " % (m, d, h, mi, s, ms))
    emptyHeader.write("%s%s%s" % (format(fg = GREEN, bg = BLACK),
                                  " " * TIME_WIDTH, format(reset = True)))
    return TIME_WIDTH

def allocate_color(tag):
    # this will allocate a unique format for the given tag
    # since we don't have very many colors, we always keep track of the LRU
    if not tag in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    LAST_USED.remove(color)
    LAST_USED.append(color)
    return color

def print_tag(linebuf, colorless, emptyHeader, tag):
    # right-align tag title and allocate color if needed
    tag   = tag.strip()
    color = allocate_color(tag)
    tag   = tag[-(TAG_WIDTH - 1):].rjust((TAG_WIDTH - 1))
    linebuf.write("%s%s %s" % (format(fg = color), tag, format(reset = True)))
    colorless.write("%s " % (tag))
    emptyHeader.write("%s%s%s" % (format(fg = color), " " * TAG_WIDTH,
                                  format(reset = True)))
    return TAG_WIDTH

def print_tagtype(linebuf, colorless, emptyHeader, tagtype):
    linebuf.write("%s%s%s " % (TAGTYPEFORMAT[tagtype],
                               tagtype.center(TAGTYPE_WIDTH),
                               format(reset = True)))
    colorless.write("%s " % (tagtype.center(TAGTYPE_WIDTH)))

    emptyHeader.write("%s%s%s " % (format(bg = BLACK), " " * TAGTYPE_WIDTH,
                                   format(reset = True)))
    return TAGTYPE_WIDTH + 1

def print_msg(linebuf, colorless, emptyHeader, headerSize, msg):
    wrap_area = WIDTH - headerSize
    current   = 0

    while current < len(msg):
        next = min(current + wrap_area - 6*msg.count('\t'), len(msg))

        linebuf.write(msg[current:next])
        colorless.write(msg[current:next])

        if next < len(msg):
            linebuf.write("\n%s" % (emptyHeader.getvalue()))
            colorless.write("\n%s" % " " * len(emptyHeader.getvalue()))
        current = next

def usage():
    print "This script can be used in two manners, by piping a flux from an "  \
          "adb logcat command or by itself it uses the options you gave him "  \
          "and parse and color the flux."
    print ""
    print "In piping mode only the following format are handled (-v option):"
    print "    \"brief\" \"tag\" \"thread\" \"time\" \"threadtime\""
    print "Use \"brief\" instead of \"process\" their output from the script " \
          "would have been the same. For the same reason use \"threadtime\" "  \
          "instead of \"long\"."
    print "\"raw\" is a useless flux handled by this script, it doesn't have " \
          "enough information to generate a color distinction."
    print ""
    print "In non piping mode you have access to the following options"
    print "    -v <format>     Sets the log print format, where <format> is "  \
          "one of: "
    print ""
    print "                    \"brief\" \"tag\" \"thread\" \"time\" "         \
                              "\"threadtime\""
    print "    -c              Clear (flush) the entire log and exit"
    print "    -S <device>     Directs command to the device or emulator "     \
                              "with the given serial number or qualifier. "    \
                              "Overrides ANDROID_SERIAL environment variable."
    print ""
    print "In both mode you have access to the following options:"
    print "    --help / -h     Print this help"
    print "    -T <regexp>     Show only logs which tags that match the "      \
                              "specified regular expression"
    print "    -M <regexp>     Show logs which message match the specified "   \
                              "regular expression"
    print "    -A <regexp>     Show logs which tags or message match the "     \
                              "specified regular expression"
    print "    -i              Ignore case on the regular expression"
    print "    -w <path>       Write output in a file (colorless)"
    sys.exit(2)

# Regular expressions
reFlags        = None
reTagFilterExp = None
reMsgFilterExp = None
reTagFilter    = None
reMsgFilter    = None
writefile      = None

# adb logcat options
logcatOptv   = "time"
logcatOpt    = StringIO.StringIO()
adbOpt       = StringIO.StringIO()

try:
    opts, arg = getopt.getopt(sys.argv[1:], "S:hscit:t:A:T:M:v:w:", ["help"])
except getopt.GetoptError as err:
    print str(err)
    print ""
    usage()

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit(2)
    elif o == "-i":
        reFlags = re.IGNORECASE
    elif o == "-A":
        reTagFilterExp = a
        reMsgFilterExp = a
    elif o == "-T":
        reTagFilterExp = a
    elif o == "-M":
        reMsgFilterExp = a
    elif o == "-v":
        if a in ("brief", "tag", "thread", "time", "threadtime"):
            logcatOptv = a
        elif a == "long":
            logcatOptv = "threadtime"
        elif a == "process":
            logcatOptv = "brief"
        else:
            print "Bad format."
            print ""
            usage()
    elif o in ("-s", "-c", "-t"):
        logcatOpt.write(" %s%s" % (o, a))
    elif o == "-S":
        adbOpt.write(" -s %s" % a)
    elif o == "-w":
        writefile = open(a, 'a')


# if someone is piping in to us, use stdin as input.  if not, invoke adb logcat
if os.isatty(sys.stdin.fileno()):
    input = os.popen("adb%s logcat -v %s%s" % (adbOpt.getvalue(),
                                               logcatOptv,
                                               logcatOpt.getvalue()))
else:
    input = sys.stdin

if not reTagFilterExp is None:
    if reFlags is None:
        reTagFilter = re.compile(reTagFilterExp)
    else:
        reTagFilter = re.compile(reTagFilterExp, reFlags)

if not reMsgFilterExp is None:
    if reFlags is None:
        reMsgFilter = re.compile(reMsgFilterExp)
    else:
        reMsgFilter = re.compile(reMsgFilterExp, reFlags)

while True:
    try:
        line = input.readline()
    except KeyboardInterrupt:
        break

    matchbeginning  = rebeginning.match(line)
    matchthreadtime = rethreadtime.match(line)
    matchthread     = rethread.match(line)
    matchtime       = retime.match(line)
    matchbrief      = rebrief.match(line)
    matchtag        = retag.match(line)
    linebuf         = StringIO.StringIO()
    colorless       = StringIO.StringIO()
    emptyHeader     = StringIO.StringIO()
    headerSize      = 0
    m               = None
    d               = None
    h               = None
    mi              = None
    sec             = None
    ms              = None
    owner           = None
    thread          = None
    tagtype         = None
    tag             = None
    msg             = None

    if not matchbeginning is None:
        msg, l = matchbeginning.groups()
        print "%s%s%s" % (format(fg = WHITE, bg = BLACK, dim = False),
                ("Beginning of " + msg + l).center(WIDTH), format(reset = True))
        if not writefile is None:
            writefile.write("%s" % ("Beginning of " + msg + l).center(WIDTH))
        continue

    elif not matchthreadtime is None:
        m, d, h, mi, sec, ms, owner,
        thread, tagtype, tag, msg = matchthreadtime.groups()

    elif not matchthread is None:
        tagtype, owner, thread, msg = matchthread.groups()

    elif not matchtime is None:
        m, d, h, mi, sec, ms, tagtype, tag, owner, msg = matchtime.groups()

    elif not matchbrief is None:
        tagtype, tag, owner, msg = matchbrief.groups()

    elif not matchtag is None:
        tagtype, tag, msg = matchtag.groups()

    else:
        print (line)
        if not writefile is None:
            writefile.write(line)
        if len(line) == 0:
            break
        continue

    # Print parts
    if not owner is None:
        headerSize += print_owner(linebuf, colorless, emptyHeader, owner)

    if not thread is None:
        headerSize += print_thread(linebuf, colorless, emptyHeader, thread)

    if not m is None:
        headerSize += print_time(linebuf, colorless, emptyHeader, m, d, h, mi, sec, ms)

    if not tag is None:
        if not reTagFilter is None:
            matchTagFilter = reTagFilter.search(tag)
        headerSize += print_tag(linebuf, colorless, emptyHeader, tag)

    if not tagtype is None:
        headerSize += print_tagtype(linebuf, colorless, emptyHeader, tagtype)

    if not msg is None:
        if not reMsgFilter is None:
            matchMsgFilter = reMsgFilter.search(msg)
        print_msg(linebuf, colorless, emptyHeader, headerSize, msg)

    # Filter on the regular expression
    if not reTagFilter is None and not reMsgFilter is None:
        if matchTagFilter is None and matchMsgFilter is None:
            continue
    elif not reTagFilter is None:
        if matchTagFilter is None:
            continue
    elif not reMsgFilter is None and matchMsgFilter is None:
        continue

    # Actual print
    print linebuf.getvalue()
    if not writefile is None:
        writefile.write(colorless.getvalue() + '\n');
