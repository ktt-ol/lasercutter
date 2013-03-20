#!/usr/bin/python
import re, sys

def tobin(x, count=8):
        """
        Integer to binary
        Count is number of bits
        """
        return "".join(map(lambda y:str((x>>y)&1), range(count-1, -1, -1)))

def bit(i, j):
	return ((bs[i]) >> j) & 1

def bit2end(val):
	# move bit 7 to pos 0
	return ((val & 0x7E) | (val>>7))

def foo2int(val):
	# turn weird counter into normal counting int
	val = bit2end(val)

	if val == 1:
		return 70
	elif val == 0:
		return 71
	low = (val-2) % 8
	if val < 0x3A + 8:
		return low + 8 * (7-((val-2) // 8))
	else:
		return low + 8 * (23-((val-2) // 8))


def int2foo(val):
	if val == 70:
		return 1
	elif val == 71:
		return 0
	if val < 64:
		return 0x3A + (val % 8) - 8 * (val//8) 
	else:
		return 2 + 23*8 + (val % 8) - 8 * (val//8)

def bit2front(val):
	return ((val & 1) << 7) | (val & 0x7E)

def decodeFoo(bs):
	val = 0L
	for b in bs:
		val = (val << 7) + foo2int(b)
	if val & (1L << (len(bs)*7-1)):
		val = val - (1L << (len(bs)*7))
	return val

def decodeY(bs):
	val = decodeFoo(bs)
	return val / 1000.0

def decodeX(bs):
	val = decodeFoo(bs)
	return val / 128000.0

def encodeFoo(val):
	val = long(round(val * 1000))
	return [
		bit2front(int2foo((val >> 21) & 0x7F)),
		bit2front(int2foo((val >> 14) & 0x7F)),
		bit2front(int2foo((val >> 7) & 0x7F)),
		bit2front(int2foo((val & 0x7F)))
		]

data = bytearray(open(sys.argv[1], 'r+b').read())

print "File Length:", len(data)
print

if len(data) < 0x8b + 12:
	print "File Truncated!"
	sys.exit(1)

start = 0x8b

while True:
	if data[start] == 0x33:
		print "Found line entry point"
		print "\tX:", decodeX([data[start+1], data[start+2], data[start+3], data[start+4], data[start+5], data[start+6]]);
		#print "\tX: %x %x %x %x %x %x" % (data[start+1], data[start+2], data[start+3], data[start+4], data[start+5], data[start+6]);
		print "\tY:", decodeY([data[start+7], data[start+8], data[start+9], data[start+10]]);
		start += 11
	elif data[start] == 0x13:
		print "Found line continuation point"
		print "\tX:", decodeX([data[start+1], data[start+2], data[start+3], data[start+4], data[start+5], data[start+6]]);
		#print "\tX: %x %x %x %x %x %x" % (data[start+1], data[start+2], data[start+3], data[start+4], data[start+5], data[start+6]);
		print "\tY:", decodeY([data[start+7], data[start+8], data[start+9], data[start+10]]);
		start += 11
	elif data[start] == 0x93:
		x = decodeFoo([data[start+1], data[start+2]]) / 1000.0
		y = decodeFoo([data[start+3], data[start+4]]) / 1000.0
		print "relative move: %f %f" % (x,y);
		start += 5
	elif data[start] == 0x95:
		print "relative Y move: %f" % (decodeFoo([data[start+1], data[start+2]]) / 1000.0)
		start += 3
	elif data[start] == 0x15:
		print "relative X move: %f" % (decodeFoo([data[start+1], data[start+2]]) / 1000.0)
		start += 3
	elif data[start] == 0xE1 and data[start+1] == 0x3A and data[start+2] == 0xF1:
		print "End of File"
		sys.exit(0)
	else:
		print "Unknown byte found: 0x%02X" % data[start]
		print "Position: 0x%02X" % start
		sys.exit(1)
