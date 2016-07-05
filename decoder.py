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

def encodeFoo(val, length=1, signed=True):
	val = long(val) # XXX fill leading Bits
	if signed and val < 0:
		val = (1 << (7*length)) + val
	result = []
	for i in range(length):
		result.append(bit2front(int2foo(val & 0x7F)))
		val = val >> 7
	result.reverse()
	return result


if __name__ == "__main__":
	for i in range(0, 1000, 13):
		#print i, encodeFoo(i, 2), decodeFoo(encodeFoo(i,2))
		print -i, encodeFoo(-i, 2), decodeFoo(encodeFoo(-i, 2))
