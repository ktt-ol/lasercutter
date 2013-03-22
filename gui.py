#!/usr/bin/env python
import cairo

class GraphicalOutput:

	def __init__(self, output="output.svg"):
		# output
		self.output = output

		# init origin
		self.origin_x = 0
		self.origin_y = 0

		# init bounding box
		self.bb1_x = 0
		self.bb1_y = 0
		self.bb2_x = 0
		self.bb2_y = 0

		self._init_surface()

	def _init_surface(self):
		width = abs(self.bb1_x-self.bb2_x)
		height = abs(self.bb1_y-self.bb2_y)

		self.surface = cairo.SVGSurface(self.output, width, height)
		self.ctx = ctx = cairo.Context(self.surface)
		ctx.scale(1, 1)

		ctx.set_source_rgb(1.0, 1.0, 1.0)
		ctx.rectangle(0, 0, width, height)
		ctx.fill()

		ctx.set_source_rgb(0.0, 0.0, 0.0)
		ctx.set_line_width(0.1)

		self._calc_real_origin()

	def _calc_real_origin(self):
		self.real_origin_x = self.origin_x - (self.origin_x + self.bb1_x)
		self.real_origin_y = self.origin_y - (self.origin_y + self.bb1_y)

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

	def move_origin(self, x, y):
		self.origin_x = x
		self.origin_y = y
		self._calc_real_origin()

	def bounding_box_top_left(self, x, y):
		self.bb1_x = x
		self.bb1_y = y
		self._init_surface()

	def bounding_box_bottom_right(self, x, y):
		self.bb2_x = x
		self.bb2_y = y
		self._init_surface()

	def move_to(self, x, y):
		self.ctx.line_to(self.real_origin_x+x, self.real_origin_y+y)
		self._custom_stroke(0, 0, 1)

	def line_to(self, x, y):
		self.ctx.line_to(self.real_origin_x+x, self.real_origin_y+y)
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
