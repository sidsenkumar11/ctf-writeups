from pwn import *

def send_plain(pblock):
	p = remote('2018shell2.picoctf.com', 31123)
	p.recvline()
	p.recvuntil('Please enter your situation report: ')
	p.sendline(pblock)
	line = p.recvline()
	p.close()
	return [line[i:i+16] for i in range(0, len(line), 16)]

# Send the following as plaintext:
# - 'fying code is: ' + 1 byte of flag
# - Send all 256 possibilities of that flag byte.
# - If it doesn't show up, just add a single byte to the front of the plaintext. Repeat up to 16 times until:
# - a block repeats in the ciphertext

"""FIRST BLOCK
Agent,\nGreetings
. My situation r
eport is as foll
ows:\naaaaaaaaaaa -> ows:\naaaaaaaaaaa
fying code is: -  -> ying code is: --
bbbbbbbbbbbbbbbb  -> bbbbbbbbbbbbbbb\n
\nMy agent identi -> My agent identif
fying code is: _  -> ying code is: __
_________\nDown w
ith the soviets,
\n006\n000000000
"""

# picoCTF{@g3nt6_1
# $_th3_c00l3$t_50
plain = ''

# Get first block
prev_plain_block = 'fying code is: '
for flag_byte in range(16):
	old_plain = plain
	for guess in range(126, 32, -1):
		log.info('Block: {}'.format(0))
		log.info('Guess: {}'.format(guess))
		log.info('FB   : {}'.format(flag_byte))
		pblock = 11 * 'a'
		pblock += prev_plain_block[flag_byte:]
		pblock += plain
		pblock += chr(guess)
		pblock += (16 - flag_byte) * 'b'
		ciphertexts = send_plain(pblock)
		if [x for x in ciphertexts if ciphertexts.count(x) > 1]:
			plain += chr(guess)
			print plain
			break

	if plain == old_plain:
		print 'problem!'
		print plain
		break

"""SECOND BLOCK
Agent,\nGreetings
. My situation r
eport is as foll
ows:\naaaaaaaaaaa -> ows:\naaaaaaaaaaa
icoCTF{@g3nt6_1*  -> coCTF{@g3nt6_1**
bbbbbbbbbbbbbbbb  -> bbbbbbbbbbbbbbb\n
\nMy agent identi -> My agent identif
fying code is: p  -> ying code is: pi
icoCTF{@g3nt6_1*  -> coCTF{@g3nt6_1**
_________\nDown w
ith the soviets,
\n006\n000000000
"""

# Get remaining blocks
for block_num in range(2):
	prev_plain_block = plain[block_num * 16 + 1:]
	this_plain_block = ''
	for flag_byte in range(16):
		old_plain = plain
		for guess in range(126, 32, -1):
			log.info('Block: {}'.format(block_num+1))
			log.info('Guess: {}'.format(guess))
			log.info('FB   : {}'.format(flag_byte))
			pblock = 11 * 'a'
			pblock += prev_plain_block[flag_byte:]
			pblock += this_plain_block
			pblock += chr(guess)
			pblock += (16 - flag_byte) * 'b'
			ciphertexts = send_plain(pblock)
			if [x for x in ciphertexts if ciphertexts.count(x) > 1]:
				this_plain_block += chr(guess)
				plain += chr(guess)
				print plain
				break

		if plain == old_plain:
			print 'problem or end!'
			print plain
			import sys
			sys.exit(1)

print plain
