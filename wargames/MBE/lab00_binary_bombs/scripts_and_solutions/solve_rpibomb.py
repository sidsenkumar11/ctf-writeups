from __future__ import print_function
from pwn import *
pwnlib.args.SILENT('SILENT')

MENU_END = '+---------------------------------------------------+'
p = process('./rpibomb')
print(p.recvuntil(MENU_END))

def cut_yellow_wire():

	# Send inputs
	p.sendline('1')
	p.sendline('84371065')
	p.sendline('')

	# Pretty print
	print(p.recvuntil(': '), end='')
	print('1')
	print(p.recvuntil(': '), end='')
	print('84371065')
	print(p.recvuntil('MENU '))
	print(p.recvuntil(MENU_END))

def cut_green_wire():

	# Send inputs
	p.sendline('2')
	p.sendline('dcaotdaeAAAABBB')
	p.sendline('')

	# Pretty print
	print(p.recvuntil(': '), end='')
	print('2')
	print(p.recvuntil(': '), end='')
	print('dcaotdaeAAAABBB')
	print(p.recvuntil('MENU '))
	print(p.recvuntil(MENU_END))

def cut_blue_wire():

	# Send inputs
	p.sendline('3')
	p.sendline('LLRR')
	p.sendline('')

	# Pretty print
	print(p.recvuntil(': '), end='')
	print('3')
	print(p.recvuntil(': '), end='')
	print('LLRR')
	print(p.recvuntil('MENU '))
	print(p.recvuntil(MENU_END))

def cut_red_wire():

	# Send menu input
	p.sendline('4')
	print(p.recvuntil(': '), end='')
	print('4')

	# Get and print seeds
	seeds = []
	print(p.recvuntil('CLOCK SYNC \x1b[0m'), end='')
	seeds.append(p.recvline().strip())
	print(seeds[-1])

	print(p.recvuntil('CLOCK SYNC \x1b[0m'), end='')
	seeds.append(p.recvline().strip())
	print(seeds[-1])

	print(p.recvuntil('CLOCK SYNC \x1b[0m'), end='')
	seeds.append(p.recvline().strip())
	print(seeds[-1])

	# Construct and send key
	seeds = [int(_, 16) for _ in seeds]
	key_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
	key = ''
	for i in range(19):
		key += key_chars[seeds[2] & 0x1F]
		seeds[2] = (seeds[2] >> 5) | (seeds[1] << 27)
		seeds[1] = (seeds[1] >> 5) | (seeds[0] << 27)
		seeds[0] = seeds[0] >> 5

	p.sendline(key)
	p.sendline('')

	# Pretty print
	print(p.recvuntil(': '), end='')
	print(key)
	print(p.recvuntil('MENU '))
	print(p.recvuntil(MENU_END))

def disarm():
	p.sendline('DISARM')
	print(p.recvuntil(': '), end='')
	print('DISARM')
	print(p.recvall())

cut_yellow_wire()
cut_green_wire()
cut_blue_wire()
cut_red_wire()
disarm()

p.close()
