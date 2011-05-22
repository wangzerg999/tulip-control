#!/usr/bin/env python
"""
Convert an AUT file (from JTLV) to a DOT (in Graphviz) file.

Note this is basically a wrapper to ease use of the Automaton class
and its writeDotFile method from the command-line. Accepts a *.aut
filename and, optionally, a destination filename. If no destination is
given, default is to use input filename with new ending ".dot"

Also note that command-line arguments are handled manually, since they
are so simple...

Example: suppose you have robotctrl.aut from a TuLiP (or JTLV)
session. Then to generate a corresponding DOT file and create a PNG
image, try

$ aut2dot.py robotctrl.aut
$ dot -Tpng -O robotctrl.dot

Depending on your graphviz installation, the resulting image file may
be called robotctrl.dot.png
"""

import sys
from tulip.automaton import Automaton


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print "Usage: aut2dot.py INPUT.aut [OUTPUT.dot]"
        exit(1)

    if len(sys.argv) == 3:
        destfile = sys.argv[2]
    else:
        if len(sys.argv[1]) < 4:  # Handle weirdly short names
            destfile = sys.argv[1] + ".dot"
        else:
            destfile = sys.argv[1][:-4] + ".dot"
    
    aut = Automaton(sys.argv[1])
    if not aut.writeDotFile(destfile):
        print "Failed to create DOT file, " + destfile
        exit(-1)
