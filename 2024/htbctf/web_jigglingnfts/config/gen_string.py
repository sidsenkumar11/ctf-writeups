import hashlib
import string
import random

def generate_random_string(length, chars):
    return ''.join(random.sample(chars, length))

def contains_only_alphanumeric(s: str) -> bool:
    return all(c.isnumeric() for c in s)

def find_md5_hash_with_0e():
    chars = string.ascii_lowercase + string.digits
    while True:
        length = random.randint(20, 25) 
        candidate = generate_random_string(length, chars)
        hash_object = hashlib.md5(candidate.encode())
        md5_hash = hash_object.hexdigest()
        if md5_hash.startswith('0e') and contains_only_alphanumeric(md5_hash[2:]):
            return candidate

has = find_md5_hash_with_0e()
print(has) # example (took 12 mins to run): efgmhtndr4x8631uvw07oclq
# with open('/www/.env', 'w') as f:
#     f.write(f'SECRET={has[2:]}')