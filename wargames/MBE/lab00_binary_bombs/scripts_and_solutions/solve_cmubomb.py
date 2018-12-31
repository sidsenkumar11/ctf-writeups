from pwn import *
pwnlib.args.SILENT('SILENT')

def send_and_print(text):
	print '>>> ' + text
	p.sendline(text)

# Start bomb
p = process('./cmubomb')
print p.recvuntil('Have a nice day!\n')

# Phase 1
send_and_print('Public speaking is very easy.')
print p.recvuntil('How about the next one?\n')

# Phase 2
send_and_print('1 2 6 24 120 720')
print p.recvuntil('Keep going!\n')

# Phase 3
send_and_print('0 q 777')
print p.recvuntil('Halfway there!\n')

# Phase 4
send_and_print('9 austinpowers')
print p.recvuntil('Try this one.\n')

# Phase 5
send_and_print('O@EKMA')
print p.recvuntil('On to the next...\n')

# Phase 6
send_and_print('4 2 6 3 1 5')
print p.recvuntil('But finding it and solving it are quite different...')

# Secret phase
send_and_print('1001')
print p.recvall()
p.close()
