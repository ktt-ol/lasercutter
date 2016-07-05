#!/usr/bin/python
#
# Copyright (c) 2013 Florian Festi
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import parser

def dist(dx, dy):
    return (dx*dx+dy*dy)**0.5

class Timer:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.moves = 0
        self.cuts = []
    
    def command(self, name, params):
        method = getattr(self, name, None)
        if method:
            #print "%s:" % name, ', '.join((str(i) for i in params))
            method(*params)

    def speed(self, spd):
        self.cuts.append([spd, 0])

    def move_to(self, x, y):
        self.move_rel(x-self.x,y-self.y)

    def move_rel(self, x_inc, y_inc):
        self.moves += dist(x_inc, y_inc)
        self.x += x_inc
        self.y += y_inc

    def move_rel_vert(self, inc_y):
        self.move_rel(0, inc_y)

    def move_rel_hor(self, inc_x):
        self.move_rel(inc_x, 0)

    def line_to(self, x, y):
        self.line_rel(x-self.x, y-self.y)

    def line_rel(self, x_inc, y_inc):
        self.cuts[-1][1] += dist(x_inc, y_inc)
        self.x += x_inc
        self.y += y_inc

    def line_rel_vert(self, inc_y):
        self.line_rel(0, inc_y)

    def line_rel_hor(self, inc_x):
        self.line_rel(inc_x, 0)


    def end_of_file(self):
        pass


if __name__ == "__main__":
    import sys
    out = Timer()
    p = parser.Parser(sys.argv[1], callback=out.command)
    p.parse()
    t = out.moves/300.0 # XXX use right speed
    print "Moves %.1fmm takes %.1fs" % (out.moves, t)
    for speed, distance in out.cuts:
        print "Cut %.1fmm with speed %.1fmm/s taking %.1fs" % (
            distance, speed, distance/speed)
        t += distance/speed
    print "Total of %.1fs" % t
