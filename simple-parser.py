#!/usr/bin/python
import re, sys
from decoder import *
from gui import *

data = bytearray(open(sys.argv[1], 'r+b').read())

print "File Length:", len(data)
print

if len(data) < 0x8b + 12:
	print "File Truncated!"
	sys.exit(1)

start = 0x8b

def parse_settings(data, pos):
	settings = {}
	settings["enable_laser_head_1"] = data[pos+7]
	settings["enable_laser_head_2"] = data[pos+10]
	settings["speed"] = decodeFoo([data[pos+22], data[pos+23], data[pos+24], data[pos+25], data[pos+26]]) / 1000.0
	settings["corner_power_1"] = decodeFoo([data[pos+29], data[pos+30]])
	settings["max_power_1"] = decodeFoo([data[pos+33], data[pos+34]])
	settings["corner_power_2"] = decodeFoo([data[pos+27], data[pos+38]])
	settings["max_power_2"] = decodeFoo([data[pos+41], data[pos+42]])
	settings["laser_on_delay"] = decodeFoo([data[pos+46], data[pos+47], data[pos+48], data[pos+49]])
	return settings

print parse_settings(data, 0x5c-7)

while True:
	if data[start] == 0x33:
		x = decodeFoo([data[start+1], data[start+2], data[start+3], data[start+4], data[start+5]]) / 1000.0;
		y = decodeFoo([data[start+6], data[start+7], data[start+8], data[start+9], data[start+10]]) / 1000.0;
		print "Found line entry point:", x, y
		move_to(x, y)
		start += 11
	elif data[start] == 0x13:
		x = decodeFoo([data[start+1], data[start+2], data[start+3], data[start+4], data[start+5]]) / 1000.0;
		y = decodeFoo([data[start+6], data[start+7], data[start+8], data[start+9], data[start+10]]) / 1000.0;
		print "Found line continuation point:", x, y
		line_to(x, y)
		start += 11
	elif data[start] == 0x93:
		x = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		y = decodeFoo([data[start+3], data[start+4]]) / 1000.0
		print "relative line:", x, y
		relative_line_to(x, y)
		start += 5
	elif data[start] == 0x95:
		y = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		print "relative Y line:", y
		relative_line_to(inc_y=y)
		start += 3
	elif data[start] == 0x15:
		x = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		print "relative X line:", x
		relative_line_to(inc_x=x)
		start += 3
	elif data[start] == 0xB3:
		x = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		y = decodeFoo([data[start+3], data[start+4]]) / 1000.0
		print "relative move:", x, y
		relative_move_to(x,y)
		start += 5
	elif data[start] == 0x35:
		x = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		print "relative X move:", x
		relative_move_to(inc_x=x)
		start += 3
	elif data[start] == 0x00:
		x = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		print "relative Y move:", x
		relative_move_to(inc_y=y)
		start += 3
	elif data[start] == 0xE1 and data[start+1] == 0x3A and data[start+2] == 0xF1:
		print "End of File"
		draw()
		sys.exit(0)
	else:
		print "Unknown byte found: 0x%02X" % data[start]
		print "Position: 0x%02X" % start
		sys.exit(1)
