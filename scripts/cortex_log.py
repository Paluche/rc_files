# !/usr/bin/python

# Inspired from the script to highlight adb logcat output for console
# written by Jeff Sharkey (http://jsharkey.org/)
#
# This scripts get what on a specified tty serial port parse it and color it.
# The input format will be in the format "[TAG] MESSAGE" by line.
# The output will add the time of the reception in front of the line and TAG
# will be colored with a color that won't change for a given 'TAG'.
#
# Written by Hubert Lefevre.

import os, sys, re, StringIO
import fcntl, termios, struct
import datetime
import getopt
import serial

def format(fg = None, bg = None, bright = False, bold = False, dim = False, reset = False):
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

def usage():
    print "cortex_log.py <tty> [-w <nocolor>]"
    print " or"
    print "<source> | cortex_log.py [-w <nocolor>]"
    print ""
    print "   <tty> Specify which tty to use, the script will use "\
          "\'/dev/tty<tty>\'"
    print "    -T <regexp>     Show only logs which tags that match the "      \
                              "specified regular expression"
    print "    -M <regexp>     Show logs which message match the specified "   \
                              "regular expression"
    print "    -A <regexp>     Show logs which tags or message match the "     \
                              "specified regular expression"
    print "    -i              Ignore case on the regular expression"
    print "    -w <path>       Write output in a file (colorless)"
    sys.exit(2)


#############
# Constants #
#############
# Unpack the current terminal width/height
data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
HEIGHT, WIDTH = struct.unpack('hh',data)

# Colors
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# Tag color allocation context
LAST_USED = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
KNOWN_TAGS = {}

# Width setting
TIME_WIDTH  = 19 # Hard coded size of the time format e.g. '08-31 10:55:02.357'
TAG_WIDTH   = 10
HEADER_SIZE = TAG_WIDTH + TIME_WIDTH

# Regular expression to match
rebootline  = re.compile("^\(@\)(.*) (.*)$")
rerbootline = re.compile("^\r\(@\)(.*) (.*)$")
rematch     = re.compile("^\[([^\(]+?)\] (.*)$")
rermatch    = re.compile("^\r\[([^\(]+?)\] (.*)$")
retagonly   = re.compile("^\[([^\(]+?)\](.*)$")
rertagonly  = re.compile("^\r\[([^\(]+?)\](.*)$")
resimple    = re.compile("^([^\(]+)([^\(]+)$")
rersimple   = re.compile("^\r([^\(]+)([^\(]+)$")

# Format function
def print_time(linebuf, nocolor):
    linebuf.write("%s%s %s" % (format(fg = GREEN, bg = BLACK, dim = False),
                               datetime.datetime.now().strftime(
                                   "%m-%d %H:%M:%S.%f")[:-3],
                               format(reset = True)))
    nocolor.write("%s " % (datetime.datetime.now().strftime(
                               "%m-%d %H:%M:%S.%f")[:-3]))

def allocate_color(tag):
    # This will allocate a unique format for the given tag
    # since we dont have very many colors, we always keep track of the LRU
    if not tag in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    LAST_USED.remove(color)
    LAST_USED.append(color)
    return color

def print_tag(linebuf, nocolor, tag, bootline = False):
    # Right-align tag title and allocate color if needed
    tag = tag.strip()
    if bootline:
        color = RED
    else:
        color = allocate_color(tag)
    tag = tag[-TAG_WIDTH:].rjust(TAG_WIDTH)
    linebuf.write("%s%s %s" % (format(fg = color, dim = False), tag,
                               format(reset = True)))
    nocolor.write("%s " % (tag))

def print_message(linebuf, nocolor, headersize, message, bootline = False):
    # Insert line wrapping as needed
    wrap_area = WIDTH - headersize - 3
    current = 0
    while current < len(message):
        next = min(current + wrap_area, len(message))
        linebuf.write("%s %s %s" % (format(bg = BLACK, dim = False),
                                    format(reset = True), message[current:next]))
        nocolor.write("  %s" % (message[current:next]))

        if bootline:
            linebuf.write("%s " % (format(reset = True)))
            nocolor.write(" ")

        if next < len(message):
            linebuf.write("\n%s " % (" " * headersize))
            nocolor.write("\n%s " % (" " * headersize))
        current = next

########
# Main #
########

# Context
reFlags        = None
reTagFilterExp = None
reMsgFilterExp = None
reTagFilter    = None
reMsgFilter    = None
writefile      = None

# If someone is piping in to us, use stdin as input, otherwise use first
# argument to know which tty you should open
if os.isatty(sys.stdin.fileno()):
    if len(sys.argv) < 2:
        usage()
    source              = serial.Serial()
    source.port         = "/dev/tty%s" % sys.argv[1]
    ########################
    # Serial configuration #
    ########################
    source.baudrate     = 115200
    source.bytesize     = serial.EIGHTBITS
    source.parity       = serial.PARITY_NONE
    source.stopbits     = serial.STOPBITS_ONE
    source.timeout      = 0     # Non-Block reading
    source.xonxoff      = False # Disable Software Flow Control
    source.rtscts       = False # Disable (RTS/CTS) flow Control
    source.dsrdtr       = False # Disable (DSR/DTR) flow Control
    source.timeout      = None  # Wait forever
    source.writeTimeout = 2
    try:
        source.open()
    except serial.SerialException as err:
        print str(err)
        print ""
        usage()
    source.flushInput()
    source.flushOutput()
else:
    source = sys.stdin

# Handle options
try:
    opts, arg = getopt.getopt(sys.argv[2:], "hw:iA:T:M:", ["help"])
except getopt.GetoptError as err:
    print str(err)
    print ""
    usage()


for o, a in opts:
    if o in ("-h", "--help"):
        usage()
    elif o == "-i":
        reFlags = re.IGNORECASE
    elif o == "-A":
        reTagFilterExp = a
        reMsgFilterExp = a
    elif o == "-T":
        reTagFilterExp = a
    elif o == "-M":
        reMsgFilterExp = a
    elif o == "-w":
        writefile = open(a, 'a')
        if not writefile is None:
            print "File opened"
        else:
            print "Error opening file"
            print ""
            usage()

# Set filtering regular expressions
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
    bootline = rebootline.match(line)
    if bootline is None:
        bootline = rerbootline.match(line)

    match = rermatch.match(line)
    if match is None:
        match = rematch.match(line)

    tagonly = rertagonly.match(line)
    if tagonly is None:
        tagonly = retagonly.match(line)

    simple = rersimple.match(line)
    if simple is None:
        simple = resimple.match(line)

    if not bootline is None:
        tag, message = bootline.groups()
        isbootline   = True

    elif not match is None:
        tag, message = match.groups()

    elif not tagonly is None:
        tag, uu = tagonly.groups()
        message = " "

    elif not simple is None:
        message, uu = simple.groups()
        tag         = " "

    elif len(line) == 0:
        break;

    else:
        print(line)
        if not writefile is None:
            writefile.write(line)
        continue

    if not reTagFilter is None:
        matchTagFilter = reTagFilter.search(tag)

    if not reMsgFilter is None:
        matchMsgFilter = reMsgFilter.search(message)

    if not reTagFilter is None and not reMsgFilter is None:
        if matchTagFilter is None and matchMsgFilter is None:
            continue
    elif not reTagFilter is None:
        if matchTagFilter is None:
            continue
    elif not reMsgFilter is None and matchMsgFilter is None:
        continue

    linebuf = StringIO.StringIO()
    nocolor = StringIO.StringIO()

    print_time(linebuf, nocolor)
    print_tag(linebuf, nocolor, tag, isbootline)
    print_message(linebuf, nocolor, HEADER_SIZE, message, isbootline)
    print linebuf.getvalue()
    if not writefile is None:
        writefile.write(nocolor.getvalue() + '\n');
