IV_len = 16

with open("sample_ciphertext.txt", 'rb') as f:
    cipher_bytes = bytearray(f.read())

with open("sample_plaintext.txt", 'rb') as f:
    plain_bytes = bytearray(f.read())

intermediate = cipher_bytes[IV_len] ^ plain_bytes[0]

with open("encrypted_flag.txt", 'rb') as f:
    encflag_bytes = bytearray(f.read())

flag_bytes = [encflag_bytes[i] ^ intermediate for i in range(16, len(encflag_bytes))]
with open("flag.txt", 'wb') as f:
    f.write(''.join(chr(x) for x in flag_bytes))
