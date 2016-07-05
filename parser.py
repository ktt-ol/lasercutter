#!/usr/bin/python
#
# Copyright (c) 2013 Florian Festi
# Copyright (c) 2013 Sebastian Reichel
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

import re, sys
from decoder import *
from gui import *


class ParamType:
	def __init__(self):
		raise NotImplementedError, "Do not instanciate!"
	@classmethod
	def read(cls, file_):
		return 0
	@classmethod
	def write(cls, file_, val):
		pass

def _buildIntClass(name, length, scale=1, signed=True):
	class cls(ParamType):
		@classmethod
		def read(cls, file_):
			return decodeFoo(bytearray(file_.read(length)), signed) / scale
		@classmethod
		def write(cls, file_, val):
			if not signed and val < 0:
				raise ValueError, "negative Value"
			for b in encodeFoo(val*scale, length, signed):
				file_.write(chr(b))
	cls.__name__ = name
	return cls


Int1 = _buildIntClass('Int1', 1)
UInt1 = _buildIntClass('UInt1', 1, signed=False)
Int2 = _buildIntClass('Int1', 2)
Int2X = _buildIntClass('Int1', 2, 1000.0)
UInt2 = _buildIntClass('UInt1', 2, signed=False)
Int5 = _buildIntClass('Int5', 5, 1000.0)
UInt5 = _buildIntClass('UInt5', 5, 1000.0, signed=False)
Percent = _buildIntClass('Int2', 2, 163.84, signed=False) # 163.84 = (2**(2*7) / 100.0)

class Byte(ParamType):
	@classmethod
	def read(cls, file_):
		return ord(file_.read(1))
	@classmethod
	def write(cls, file_, val):
		if not (0 <= val < 256):
			raise ValueError, "negative Value"
		file_.write(chr(val))

class Feature(Byte):
	feature_table = {
		0x2E : 'enable_laser_head_1',
		0xAE : 'disable_laser_head_1',
		0x30 : 'enable_laser_head_2',
		0xB0 : 'disable_laser_head_2',
	}

	reverse_table = dict(((name, code) for code, name in feature_table.iteritems()))
	@classmethod
        def read(cls, file_):
                val = Byte.read(file_)
		return cls.feature_table.get(val, "unknown_feature_%02x" % val)
	@classmethod
        def write(cls, file_, val):
		result = cls.reverse_table.get(val, None)
		if result is None:
			result = int(val[-2:], 16)
		Byte.write(file_, result)

def print_callback(name, params):
	print "%s:" % name, ', '.join((str(i) for i in params))

class Parser:

	def __init__(self, filename, callback=print_callback):
		self.filename = filename
		self.cb = callback

	def _readByte(self):
		return ord(self.f.read(1))

	def _readSettings(self):
		while True:
			cmd = self._readByte()
			if cmd == 0xF1:
				self.cb("end_of_file", [])
				return
			cmd = (cmd << 8) | self._readByte()
			if cmd in self.settings_table:
				params, name = self.settings_table[cmd]
				if isinstance(params, list):
					args = [paramtype.read(self.f)
						for paramtype in params]
					self.cb(name, args)
				else:
					args = params(self)
					self.cb(name, args)
				if name == '_81AC':
					break
			else:
				print "Unknown Setting: 0x%4x" % cmd
		return []

	command_table = {
		0x63 : ([Byte,Byte,Byte], 'magic'),
		0x33 : ([Int5, Int5], 'move_to'),
		0x13 : ([Int5, Int5], 'line_to'),
		0x93 : ([Int2X, Int2X], 'line_rel'),
		0x95 : ([Int2X], 'line_rel_vert'),
		0x15 : ([Int2X], 'line_rel_hor'),
		0xB3 : ([Int2X, Int2X], 'move_rel'),
		0x35 : ([Int2X], 'move_rel_hor'),
		0x00 : ([Int2X], 'move_rel_vert'),
		0xB5 : ([Int2], '_B5'),
		0x01 : ([Percent], '_01'),
		0x73 : ([Percent], '_73'),
		0x77 : ([Percent], '_77'),
		0xF7 : ([Percent], '_F7'),
		0xE1 : ([], 'xE1'),
		}

	E1_table = {
		0xB2 : ([Int5, Int5], 'move_origin'),
		0xBC : ([Int5, Int5], 'bounding_box_top_left'),
		0xC0 : ([Int5, Int5], 'bounding_box_bottom_right'),
		0x40 : ([Int5, Int5], '_40'),
		0x2A : ([Int5], '_2A'),
		0xAA : ([Int5], '_AA'),
		0x3E : ([Int2, Int2, Int5, Int5, Int5], 'gobal_settings'),
		0x3A : ([], 'settings'), # between layers / eof marker
		}

	settings_table = {
		0x75BA : ([Feature], 'enable_feature'),
		0x753C : ([Int1], '_753C'),
		0xF33A : ([Int1], '_F33A'),
		0xF33C : ([Int5], 'speed'),
		0x813A : ([UInt2], '_813A'),
		0x81BA : ([Percent], 'corner_power_1'),
		0x812C : ([Int5], '_812C'),
		0x813C : ([Percent], 'max_power_1'),
		0xFF3A : ([UInt2], '_FF3A'),
		0xFFBA : ([Percent], 'corner_power_2'),
		0xFF3C : ([Percent], 'max_power_2'),
		0x812C : ([Int5], 'laser_on_delay'),
		0x81AC : ([Int2], '_81AC'),
		0xF1   : ([], 'end_of_file'),
		}

	def parse(self):
		self.f = open(sys.argv[1], 'r+b')
		self.f.seek(0, 2) # goto end
		l = self.f.tell()
		self.f.seek(0) # back to the beginning

		while self.f.tell() < l:
			cmd = self._readByte()
			if cmd in self.command_table:
				params, name = self.command_table[cmd]
				args = [paramtype.read(self.f)
					for paramtype in params]
				self.cb(name, args)
				if cmd == 0xE1:
					subcmd = self._readByte()
					if subcmd in self.E1_table:
						params, name = self.E1_table[subcmd]
						args = [paramtype.read(self.f)
							for paramtype in params]
						self.cb(name, args)
						if subcmd in (0x3E, 0x3A):
							self._readSettings()
					else:
						print "WTF? E1 %2X" % subcmd
			else:
				print "Unknown byte found: 0x%02X" % cmd
				print "Position: 0x%04X" % (self.f.tell()-1)
				sys.exit(1)

def _reverse_table(t):
	result = {}
	for code, (args, name) in t.iteritems():
		result[name] = (args, code)
	return result

class Writer:
	command_table = _reverse_table(Parser.command_table)
	E1_table = _reverse_table(Parser.E1_table)
	settings_table = _reverse_table(Parser.settings_table)

	transitions = {
		0xE1 : E1_table,
		0x3E : settings_table,
		0x3A : settings_table,
		0x81AC : command_table
		}

	def __init__(self, filename):
		self.f = open(filename, 'wb')
		self.mode = self.command_table

	def command(self, name, args):
		if name in self.mode:
			params, code = self.mode[name]
			if len(args) != len(params):
				print "Got %i params expected %i!" % (len(args), len(params))
			if self.mode == self.settings_table and code != 0xF1:
				self.f.write(chr(code>>8))
			self.f.write(chr(code&0xFF))
			for arg, paramtype in zip(args, params):
				paramtype.write(self.f, arg)

			if code in self.transitions:
				self.mode = self.transitions[code]
			elif self.mode is self.E1_table:
				self.mode = self.command_table
		else:
			print "Unexpected command name:", name

if __name__ == "__main__":
	#out = GraphicalOutput(1024, 1024)
	out = Writer("output.ud")
	p = Parser(sys.argv[1], callback=out.command)
	p.parse()
