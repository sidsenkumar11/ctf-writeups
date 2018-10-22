from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from fractions import gcd
import glob
import gmpy

# Get all file names
# Note - the only given file was authorized_keys
# I had to turn SSH form into PEM form using RsaCtfTool
key_files = glob.glob("./*.pem")

# Extract n and e from all key files
keys = {}
for key_file in key_files:
	key = RSA.importKey(open(key_file).read())
	keys[key_file] = { "n" : key.n, "e" : key.e}

# Find all pairs of n with common factors
private_keys = {}

for key_file in key_files:
	key_one = keys[key_file]

	for other_key_file in key_files:
		key_two = keys[other_key_file]

		# Don't find GCD between the same exact keys
		if key_one == key_two:
			continue

		# Check if key found
		if gcd(key_one["n"], key_two["n"]) != 1:
			key_one_p = gcd(key_one["n"], key_two["n"])
			key_one_q = key_one["n"] / key_one_p
			key_one_e = key_one["e"]

			key_two_p = key_one_p
			key_two_q = key_two["n"] / key_two_p
			key_two_e = key_two["e"]

			private_keys[key_file] = {"p":key_one_p, "q":key_one_q, "e":key_one_e}
			private_keys[other_key_file] = {"p":key_two_p, "q":key_two_q,"e":key_two_e}

# Construct PKCS1_OAEP Private Keys
pkeys = {}
for key_file in private_keys:

	e = private_keys[key_file]["e"]
	p = private_keys[key_file]["p"]
	q = private_keys[key_file]["q"]
	n = p * q
	d = long(gmpy.invert(e, (p-1)*(q-1)))

	private_key = RSA.construct((n, e, d))
	encname = key_file[:key_file.index(".pem")] + ".private"
	with open(encname, 'w') as fout:
		fout.write(private_key.exportKey('PEM'))
