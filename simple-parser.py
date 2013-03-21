#!/usr/bin/python
import re, sys
from decoder import *
from gui import *

class Parser:

	def __init__(self, filename):
		self.filename = filename

	def _readByte(self):
		self.pos += 1
		return self.data[self.pos-1]

	def _readInt5(self):
		self.pos += 5
		return decodeFoo(self.data[self.pos-5:self.pos]) / 1000.0;

	def _readInt2(self):
		self.pos += 2
		return decodeFoo(self.data[self.pos-2:self.pos]) / 1000.0;

	def _readInt1(self):
		self.pos += 1
		return decodeFoo(self.data[self.pos-1:self.pos]);

	def _readUInt2(self):
		self.pos += 2
		return decodeFoo(self.data[self.pos-2:self.pos], signed=False) / 1000.0;


	def _readSettings2(self):
		x3A, xAB = self._readByte(), self._readByte()
		print "0x3A? : 0x%2x 0xAB? : 0x%2x" % (x3A, xAB)
		x3A, xAB = self._readByte(), self._readByte()
		print "0x3A? : 0x%2x 0xAB? : 0x%2x" % (x3A, xAB)
		x, y, z = self._readInt5(), self._readInt5(), self._readInt5()
		print "x, y, z:", x, y, z
		self._readSettings()

	def _readSettings(self):
		if self.data[self.pos] == 0xF1:
			print "End of File"
			#draw()
			sys.exit(0)
		while True:
			cmd = (self._readByte() << 8) | self._readByte()
			if cmd in self.settings_table:
				params, name = self.settings_table[cmd]
				args = [param(self) for param in params]
				print name, args
				if name == '81AC':
					break
			else:
				print "Unknown Setting: 0x%4x" % cmd



	parse_table = {
		0x63 : ([_readByte,_readByte,_readByte], 'MAGIC!!!!'),
		0x33 : ([_readInt5, _readInt5], 'move_to'),
		0x13 : ([_readInt5, _readInt5], 'line_to'),
		0x93 : ([_readInt2, _readInt2], 'line_rel'),
		0x95 : ([_readInt2], 'line_rel_vert'),
		0x15 : ([_readInt2], 'line_rel_hor'),
		0xB3 : ([_readInt2, _readInt2], 'move_rel'),
		0x35 : ([_readInt2], 'move_rel_hor'),
		0x00 : ([_readInt2], 'move_rel_vert'),
		0xB5 : ([_readInt2], 'B5'),
		}

	E1_table = {
		0xB2 : ([_readInt5, _readInt5], 'B2'),
		0xBC : ([_readInt5, _readInt5], 'BC'),
		0xC0 : ([_readInt5, _readInt5], 'C0'),
		0x40 : ([_readInt5, _readInt5], '40'),
		0x2A : ([_readInt5], '2A'),
		0xAA : ([_readInt5], 'AA'),
		0x3E : ([_readSettings2], 'settings'), # at beginning
		0x3A : ([_readSettings], 'settings'), # between layers/end
		}

	settings_table = {
		0x75BA : ([_readInt1], 'enable_feature'),
		0x753C : ([_readInt1], '753C'),
		0xF33A : ([_readInt1], 'F33A'),
		0xF33C : ([_readInt5], 'speed'),
		0x813A : ([_readUInt2], '813A'),
		0x81BA : ([_readUInt2], 'corner_power_1'),
		0x812C : ([_readInt5], '812C'),
		0x813C : ([_readUInt2], 'max_power_1'),
		0xFF3A : ([_readUInt2], 'FF3A'),
		0xFFBA : ([_readUInt2], 'corner_power_2'),
		0xFF3C : ([_readUInt2], 'max_power_2'),
		0x812C : ([_readInt5], 'laser_on_delay'),
		0x81AC : ([_readInt2], '81AC'),
		}

	def parse(self):
		self.data = bytearray(open(sys.argv[1], 'r+b').read())
		print "File Length:", len(self.data)
		print

		if len(self.data) < 0x8b + 12:
			print "File Truncated!"
			sys.exit(1)

		self.pos = 0

		while True:
			cmd = self._readByte()
			if cmd in self.parse_table:
				params, name = self.parse_table[cmd]
				args = [param(self) for param in params]
				print name, args
				#self.getattr(name)(*args)
			elif cmd == 0xE1:
				subcmd = self._readByte()
				if subcmd in self.E1_table:
					params, name = self.E1_table[subcmd]
					args = [param(self) for param in params]
					print name, args
				else:
					print "WTF? E1 %2X" % subcmd
			else:
				print "Unknown byte found: 0x%02X" % cmd
				print "Position: 0x%02X" % (self.pos -1)
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
