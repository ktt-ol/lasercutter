#!/usr/bin/python
import re, sys
from decoder import *
from gui import *


def _buildIntClass(name, length, scale=1, signed=True):
	class cls:
		def __init__(self):
			raise NotImplementedError
		@classmethod
		def read(cls, file_):
			return decodeFoo(bytearray(file_.read(length)), signed) / scale
		@classmethod
		def write(cls, file_, val):
			if not signed and val < 0:
				raise ValueError, "negative Value"
			file_.write(encodeFoo(val*scale, length, signed))
	#cls.__name__ = name
	return cls


Int1 = _buildIntClass('Int1', 1)
UInt1 = _buildIntClass('UInt1', 1, signed=True)
Int2 = _buildIntClass('Int1', 2)
UInt2 = _buildIntClass('UInt1', 2, signed=True)
Int5 = _buildIntClass('Int5', 5, 1000.0)
UInt5 = _buildIntClass('UInt5', 5, 1000.0, signed=True)

class Byte:
	def __init__(self):
		raise NotImplementedError
	@classmethod
	def read(cls, file_):
		return ord(file_.read(1))
	@classmethod
	def write(cls, file_, val):
		if not (0 <= val < 256):
			raise ValueError, "negative Value"
		file_.write(chr(val))

class Parser:

	def __init__(self, filename):
		self.filename = filename

	def _readByte(self):
		return ord(self.f.read(1))

	def _readSettings2(self):
		x3A, xAB = self._readByte(), self._readByte()
		print "0x3A? : 0x%2x 0xAB? : 0x%2x" % (x3A, xAB)
		x3A, xAB = self._readByte(), self._readByte()
		print "0x3A? : 0x%2x 0xAB? : 0x%2x" % (x3A, xAB)
		x, y, z = Int5.read(self.f), Int5.read(self.f), Int5.read(self.f)
		print "x, y, z:", x, y, z
		self._readSettings()

	def _readSettings(self):
		while True:
			cmd = self._readByte()
			if cmd == 0xF1:
				print "End of File"
				#draw()
				print self.f.tell(), repr(self.f.read())
				self.f.seek(0,2)
				print self.f.tell()
				sys.exit(0)
			cmd = (cmd << 8) | self._readByte()
			if cmd in self.settings_table:
				params, name = self.settings_table[cmd]
				args = [paramtype.read(self.f)
					for paramtype in params]
				print name, args
				if name == '81AC':
					break
			else:
				print "Unknown Setting: 0x%4x" % cmd



	parse_table = {
		0x63 : ([Byte,Byte,Byte], 'MAGIC!!!!'),
		0x33 : ([Int5, Int5], 'move_to'),
		0x13 : ([Int5, Int5], 'line_to'),
		0x93 : ([Int2, Int2], 'line_rel'),
		0x95 : ([Int2], 'line_rel_vert'),
		0x15 : ([Int2], 'line_rel_hor'),
		0xB3 : ([Int2, Int2], 'move_rel'),
		0x35 : ([Int2], 'move_rel_hor'),
		0x00 : ([Int2], 'move_rel_vert'),
		0xB5 : ([Int2], 'B5'),
		}

	E1_table = {
		0xB2 : ([Int5, Int5], 'B2'),
		0xBC : ([Int5, Int5], 'BC'),
		0xC0 : ([Int5, Int5], 'C0'),
		0x40 : ([Int5, Int5], '40'),
		0x2A : ([Int5], '2A'),
		0xAA : ([Int5], 'AA'),
		0x3E : (_readSettings2, 'settings'), # at beginning
		0x3A : (_readSettings, 'settings'), # between layers/end
		}

	settings_table = {
		0x75BA : ([Int1], 'enable_feature'),
		0x753C : ([Int1], '753C'),
		0xF33A : ([Int1], 'F33A'),
		0xF33C : ([Int5], 'speed'),
		0x813A : ([UInt2], '813A'),
		0x81BA : ([UInt2], 'corner_power_1'),
		0x812C : ([Int5], '812C'),
		0x813C : ([UInt2], 'max_power_1'),
		0xFF3A : ([UInt2], 'FF3A'),
		0xFFBA : ([UInt2], 'corner_power_2'),
		0xFF3C : ([UInt2], 'max_power_2'),
		0x812C : ([Int5], 'laser_on_delay'),
		0x81AC : ([Int2], '81AC'),
		}

	def parse(self):
		self.f = open(sys.argv[1], 'r+b')
		self.f.seek(0, 2) # goto end
		l = self.f.tell()
		self.f.seek(0) # back to the beginning
		print "File Length:", l
		print

		if l < 0x8b + 12:
			print "File Truncated!"
			sys.exit(1)

		while True:
			cmd = self._readByte()
			if cmd in self.parse_table:
				params, name = self.parse_table[cmd]
				args = [paramtype.read(self.f)
					for paramtype in params]
				print name, args
				#self.getattr(name)(*args)
			elif cmd == 0xE1:
				subcmd = self._readByte()
				if subcmd in self.E1_table:
					params, name = self.E1_table[subcmd]
					if isinstance(params, list):
						args = [paramtype.read(self.f)
							for paramtype in params]
						print name, args
					else:
						params(self)
				else:
					print "WTF? E1 %2X" % subcmd
			else:
				print "Unknown byte found: 0x%02X" % cmd
				print "Position: 0x%04X" % (self.f.tell()-1)
				sys.exit(1)

"""
	if data[start] == 0x33:
		print "Found line entry point:", x, y
		move_to(x, y)
	elif data[start] == 0x13:
		print "Found line continuation point:", x, y
		line_to(x, y)
	elif data[start] == 0x93:
		print "relative line:", x, y
		relative_line_to(x, y)
	elif data[start] == 0x95:
		print "relative Y line:", y
		relative_line_to(inc_y=y)
	elif data[start] == 0x15:
		print "relative X line:", x
		relative_line_to(inc_x=x)
	elif data[start] == 0xB3:
		print "relative move:", x, y
		relative_move_to(x,y)
	elif data[start] == 0x35:
		print "relative X move:", x
		relative_move_to(inc_x=x)
	elif data[start] == 0x00:
		print "relative Y move:", x
		relative_move_to(inc_y=y)
"""

p = Parser(sys.argv[1])
p.parse()
