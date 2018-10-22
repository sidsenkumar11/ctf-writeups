# Use dynamic programming to generate the key after deriving its formula from the binary
x = 0x186b5
base_arr = [-1] * (x+1)
for n in xrange(x + 1):
    if n <= 4:
        base_arr[n] = n * n + 0x2345
    else:
        base_arr[n] = (base_arr[n-1] - base_arr[n-2]) + (base_arr[n-3] - base_arr[n-4]) + base_arr[n-5] * 0x1234

print hex(base_arr[x])
print hex(base_arr[x])[2:][-17:]
