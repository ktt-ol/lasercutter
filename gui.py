#!/usr/bin/env python
import cairo

class GraphicalOutput:

	def __init__(self, width, height, scale=10, output="output.svg"):
		# init canvas
		self.width = width
		self.height = height
		self.scale = scale
                #self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
		self.surface = cairo.SVGSurface(output, self.width, self.height)
		self.ctx = ctx = cairo.Context(self.surface)
		ctx.scale(scale, scale)

		ctx.set_source_rgb(1.0, 1.0, 1.0)
		ctx.rectangle (0, 0, self.width, self.height)
		ctx.fill()

		ctx.set_source_rgb(0.0, 0.0, 0.0)
		ctx.set_line_width(0.1)

	def _custom_stroke(self, r, g, b):
		self.ctx.set_source_rgb(r, g, b)
		x, y = self.ctx.get_current_point()
		self.ctx.stroke ()
		self.ctx.move_to(x, y)

	def command(self, name, params):
		print "%s:" % name, ', '.join((str(i) for i in params))
		method = getattr(self, name, None)
		if method:
			method(*params)

	def move_to(self, x, y):
		self.ctx.line_to(x+self.width/10, y)
		self._custom_stroke(0, 0, 1)

	def line_to(self, x, y):
		self.ctx.line_to(x+self.width/10, y)
		self._custom_stroke(0, 0, 0)

	def line_rel(self, inc_x=0, inc_y=0):
		x,y = self.ctx.get_current_point()
		self.ctx.line_to(x+inc_x, y+inc_y)
		self._custom_stroke(1, 0, 0)

	def line_rel_vert(self, inc_y):
		self.line_rel(0, inc_y)

	def line_rel_hor(self, inc_x):
		self.line_rel(inc_x, 0)

	def move_rel(self, inc_x=0, inc_y=0):
		x,y = self.ctx.get_current_point()
		self.ctx.line_to(x+inc_x, y+inc_y)
		self._custom_stroke(0, 0, 1)

	def move_rel_vert(self, inc_y):
		self.move_rel(0, inc_y)

	def move_rel_hor(self, inc_x):
		self.move_rel(inc_x, 0)

	def end_of_file(self):
		#surface.write_to_png("output.png")
		self.surface.flush()
