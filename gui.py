#!/usr/bin/env python
import cairo

# init canvas
WIDTH, HEIGHT = 2024, 2024
#surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
surface = cairo.SVGSurface("output.svg", WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.scale(10, 10)

ctx.set_source_rgb(1.0, 1.0, 1.0)
ctx.rectangle (0, 0, WIDTH, HEIGHT)
ctx.fill()

ctx.set_source_rgb(0.0, 0.0, 0.0)
ctx.set_line_width(0.1)

def custom_stroke(r, g, b):
	ctx.set_source_rgb(r, g, b)
	x, y = ctx.get_current_point()
	ctx.stroke ()
	ctx.move_to(x, y)

def move_to(x,y):
	ctx.line_to(x+WIDTH/10, y)
	custom_stroke(0, 0, 1)

def line_to(x,y):
	ctx.line_to(x+WIDTH/10, y)
	custom_stroke(0, 0, 0)

def relative_line_to(inc_x=0,inc_y=0):
	x,y = ctx.get_current_point()
	ctx.line_to(x+inc_x, y+inc_y)
	custom_stroke(1, 0, 0)

def relative_move_to(inc_x=0,inc_y=0):
	x,y = ctx.get_current_point()
	ctx.line_to(x+inc_x, y+inc_y)
	custom_stroke(0, 0, 1)

def draw():
	#surface.write_to_png("output.png")
	surface.flush()
