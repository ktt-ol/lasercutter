#!/usr/bin/python
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

def decodeFoo(bs, signed=True):
	val = 0L
	for b in bs:
		val = (val << 7) + foo2int(b)
	if signed and val & (1L << (len(bs)*7-1)):
		val = val - (1L << (len(bs)*7))
	return val

def encodeFoo(val):
	val = long(round(val * 1000))
	return [
		bit2front(int2foo((val >> 21) & 0x7F)),
		bit2front(int2foo((val >> 14) & 0x7F)),
		bit2front(int2foo((val >> 7) & 0x7F)),
		bit2front(int2foo((val & 0x7F)))
		]
